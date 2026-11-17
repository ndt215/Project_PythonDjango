"""
Test tự động cho phần phân quyền chấm điểm và hình ảnh.

Chạy:
    python manage.py test reviews -v 2
"""

import io

from django.test import TestCase, override_settings
from PIL import Image
from rest_framework.test import APIClient

from .models import BaiReview, ChamDiem, HinhAnh, NguoiDung, NhaHang


def tao_anh_jpeg(ten="test.jpg"):
    """Sinh một file JPEG nhỏ để test upload."""
    buffer = io.BytesIO()
    Image.new("RGB", (10, 10), "red").save(buffer, "JPEG")
    buffer.seek(0)
    from django.core.files.uploadedfile import SimpleUploadedFile

    return SimpleUploadedFile(ten, buffer.read(), content_type="image/jpeg")


# Lưu file trong bộ nhớ để test không cần ghi vào ổ đĩa
@override_settings(
    STORAGES={
        "default": {
            "BACKEND": "django.core.files.storage.InMemoryStorage",
        },
    }
)
class ChamDiemVaHinhAnhTests(TestCase):
    def setUp(self):
        self.a = NguoiDung.objects.create_user(
            username="member_a",
            email="a@example.com",
            password="matkhau123",
            ho_ten="Thành viên A",
        )
        self.b = NguoiDung.objects.create_user(
            username="member_b",
            email="b@example.com",
            password="matkhau123",
            ho_ten="Thành viên B",
        )
        self.admin = NguoiDung.objects.create_superuser(
            username="admin_test",
            email="admin@example.com",
            password="matkhau123",
        )
        self.nha_hang = NhaHang.objects.create(
            ten_quan="Quán Test",
            dia_chi="1 Nguyễn Huệ",
            quan_huyen="Quận 1",
            thanh_pho="TP. Hồ Chí Minh",
        )
        self.bai = BaiReview.objects.create(
            nguoi_dung=self.a,
            nha_hang=self.nha_hang,
            tieu_de="Bài test",
            noi_dung="Nội dung test",
            trang_thai=BaiReview.TrangThai.DA_DANG,
        )

        self.client_a = APIClient()
        self.client_a.force_authenticate(self.a)

        self.client_b = APIClient()
        self.client_b.force_authenticate(self.b)

        self.client_admin = APIClient()
        self.client_admin.force_authenticate(self.admin)

        self.client_khach = APIClient()

    def _cham(self, client, vi_giac=5, khong_gian=5, phuc_vu=5, gia_ca=5):
        return client.post(
            "/api/cham-diem/",
            {
                "bai_review": self.bai.id,
                "vi_giac": vi_giac,
                "khong_gian": khong_gian,
                "phuc_vu": phuc_vu,
                "gia_ca": gia_ca,
            },
            format="json",
        )

    # ------------------------------------------------------------------
    # CHẤM ĐIỂM
    # ------------------------------------------------------------------
    def test_hai_thanh_vien_cung_cham_duoc_mot_bai(self):
        r1 = self._cham(self.client_a, 5, 5, 5, 5)
        r2 = self._cham(self.client_b, 4, 4, 4, 4)

        self.assertEqual(r1.status_code, 201, r1.data)
        self.assertEqual(r2.status_code, 201, r2.data)
        self.assertEqual(ChamDiem.objects.filter(bai_review=self.bai).count(), 2)

        self.bai.refresh_from_db()
        # (5.0 + 4.0) / 2 = 4.5
        self.assertAlmostEqual(self.bai.diem_trung_binh, 4.5, places=1)

    def test_mot_nguoi_khong_cham_trung(self):
        self.assertEqual(self._cham(self.client_a).status_code, 201)
        r = self._cham(self.client_a)
        self.assertEqual(r.status_code, 400, r.data)

    def test_chi_chu_diem_hoac_admin_duoc_sua_xoa(self):
        r = self._cham(self.client_a)
        diem_id = r.data["id"]

        # B không sửa được điểm của A
        r = self.client_b.patch(
            f"/api/cham-diem/{diem_id}/", {"vi_giac": 1}, format="json"
        )
        self.assertEqual(r.status_code, 403, r.data)

        # A sửa điểm của mình được
        r = self.client_a.patch(
            f"/api/cham-diem/{diem_id}/", {"vi_giac": 3}, format="json"
        )
        self.assertEqual(r.status_code, 200, r.data)

        # Admin sửa được điểm của A
        r = self.client_admin.patch(
            f"/api/cham-diem/{diem_id}/", {"vi_giac": 2}, format="json"
        )
        self.assertEqual(r.status_code, 200, r.data)

    def test_diem_trung_binh_cap_nhat_khi_xoa(self):
        r_a = self._cham(self.client_a, 5, 5, 5, 5)
        self._cham(self.client_b, 3, 3, 3, 3)

        self.bai.refresh_from_db()
        self.assertAlmostEqual(self.bai.diem_trung_binh, 4.0, places=1)

        self.client_admin.delete(f"/api/cham-diem/{r_a.data['id']}/")

        self.bai.refresh_from_db()
        self.assertAlmostEqual(self.bai.diem_trung_binh, 3.0, places=1)

    def test_bai_review_tra_ve_danh_sach_cham_diem(self):
        self._cham(self.client_a)
        self._cham(self.client_b, 4, 4, 4, 4)

        r = self.client_khach.get(f"/api/bai-review/{self.bai.id}/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data["danh_sach_cham_diem"]), 2)
        self.assertIsNone(r.data["diem_cua_toi"])

        r = self.client_a.get(f"/api/bai-review/{self.bai.id}/")
        self.assertEqual(r.data["diem_cua_toi"]["vi_giac"], 5.0)

    # ------------------------------------------------------------------
    # HÌNH ẢNH
    # ------------------------------------------------------------------
    def test_moi_thanh_vien_duoc_upload_anh(self):
        r = self.client_a.post(
            "/api/hinh-anh/",
            {"bai_review": self.bai.id, "hinh_anh": tao_anh_jpeg("a.jpg")},
            format="multipart",
        )
        self.assertEqual(r.status_code, 201, r.data)
        self.assertEqual(r.data["nguoi_dung"], self.a.id)

        r = self.client_b.post(
            "/api/hinh-anh/",
            {"bai_review": self.bai.id, "hinh_anh": tao_anh_jpeg("b.jpg")},
            format="multipart",
        )
        self.assertEqual(r.status_code, 201, r.data)
        self.assertEqual(HinhAnh.objects.filter(bai_review=self.bai).count(), 2)

    def test_chi_nguoi_tai_anh_hoac_admin_duoc_xoa(self):
        r = self.client_a.post(
            "/api/hinh-anh/",
            {"bai_review": self.bai.id, "hinh_anh": tao_anh_jpeg("a.jpg")},
            format="multipart",
        )
        anh_id = r.data["id"]

        # B không xóa được ảnh của A
        self.assertEqual(
            self.client_b.delete(f"/api/hinh-anh/{anh_id}/").status_code, 403
        )

        # Chủ ảnh xóa được
        self.assertEqual(
            self.client_a.delete(f"/api/hinh-anh/{anh_id}/").status_code, 204
        )

    # ------------------------------------------------------------------
    # BÀI REVIEW
    # ------------------------------------------------------------------
    def test_khong_the_tao_bai_hoac_tu_duyet(self):
        r = self.client_a.post(
            "/api/bai-review/",
            {
                "nguoi_dung": self.b.id,          # bị bỏ qua
                "nha_hang": self.nha_hang.id,
                "tieu_de": "Bài mới",
                "noi_dung": "Nội dung",
                "trang_thai": "da_dang",          # bị bỏ qua
            },
            format="json",
        )
        self.assertEqual(r.status_code, 201, r.data)
        self.assertEqual(r.data["nguoi_dung"], self.a.id)
        self.assertEqual(r.data["trang_thai"], "cho_duyet")

    def test_chi_chu_bai_hoac_admin_duoc_sua(self):
        r = self.client_b.patch(
            f"/api/bai-review/{self.bai.id}/",
            {"tieu_de": "B sửa trộm"},
            format="json",
        )
        self.assertEqual(r.status_code, 403, r.data)

        r = self.client_a.patch(
            f"/api/bai-review/{self.bai.id}/",
            {"tieu_de": "A sửa bài mình"},
            format="json",
        )
        self.assertEqual(r.status_code, 200, r.data)

        r = self.client_admin.post(f"/api/bai-review/{self.bai.id}/duyet/")
        self.assertEqual(r.status_code, 200, r.data)
