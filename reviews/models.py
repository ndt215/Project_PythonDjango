"""
Định nghĩa 10 bảng (Model) cho hệ thống Măm Măm Food Review.

Quy ước chung:
- Dùng tiếng Việt có dấu trong verbose_name để trang Admin hiển thị đẹp.
- Tiền tệ tính bằng VNĐ (số nguyên, không có phần thập phân).
- Các bảng nối (LuotThich, QuanYeuThich, TheoDoi) dùng UniqueConstraint
  (cách khai báo hiện đại của Django, thay cho unique_together cũ)
  để tránh việc một người thích/theo dõi trùng nhiều lần.

Sau khi sửa file này, chạy:
    python manage.py makemigrations
    python manage.py migrate
"""

from django.conf import settings
from django.contrib.auth.models import AbstractUser , UserManager
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg, F
from django.utils.text import slugify


# ===========================================================================
# 1. NGƯỜI DÙNG
# Kế thừa AbstractUser nên có sẵn: username, password, first_name, last_name,
# is_staff, is_superuser, is_active, date_joined...
# Bổ sung các trường nghiệp vụ: họ tên, email, ảnh đại diện, tiểu sử, vai trò...
# ===========================================================================

class NguoiDungManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("vai_tro", "quan_tri_vien")
        return super().create_superuser(username, email, password, **extra_fields)

class NguoiDung(AbstractUser):
    """Người dùng hệ thống: Quản trị viên, Thành viên hoặc Khách."""
    objects = NguoiDungManager()

    class VaiTro(models.TextChoices):
        QUAN_TRI_VIEN = "quan_tri_vien", "Quản trị viên"
        THANH_VIEN = "thanh_vien", "Thành viên"
        KHACH = "khach", "Khách"

    class TrangThai(models.TextChoices):
        HOAT_DONG = "hoat_dong", "Hoạt động"
        BI_KHOA = "bi_khoa", "Bị khóa"

    ho_ten = models.CharField("Họ và tên", max_length=150, blank=True)
    email = models.EmailField("Email", unique=True)
    anh_dai_dien = models.ImageField(
        "Ảnh đại diện",
        upload_to="avatars/",
        blank=True,
        null=True,
        help_text="Ảnh vuông, kích thước tối thiểu 200x200 px.",
    )
    tieu_su = models.TextField("Tiểu sử", blank=True)
    vai_tro = models.CharField(
        "Vai trò",
        max_length=20,
        choices=VaiTro.choices,
        default=VaiTro.THANH_VIEN,
    )
    trang_thai = models.CharField(
        "Trạng thái",
        max_length=20,
        choices=TrangThai.choices,
        default=TrangThai.HOAT_DONG,
    )
    ngay_tao = models.DateTimeField("Ngày tạo", auto_now_add=True)
    ngay_cap_nhat = models.DateTimeField("Ngày cập nhật", auto_now=True)

    class Meta:
        verbose_name = "Người dùng"
        verbose_name_plural = "Danh sách người dùng"
        ordering = ["-ngay_tao"]

    def __str__(self):
        return self.ho_ten or self.username

    @property
    def la_quan_tri_vien(self):
        """True nếu người dùng có vai trò quản trị viên."""
        return self.vai_tro == self.VaiTro.QUAN_TRI_VIEN


# ===========================================================================
# 2. NHÀ HÀNG / QUÁN ĂN
# ===========================================================================
class NhaHang(models.Model):
    """Thông tin một quán ăn, nhà hàng được đưa lên hệ thống."""

    class LoaiAmThuc(models.TextChoices):
        MON_VIET = "mon_viet", "Món Việt"
        MON_NUOC = "mon_nuoc", "Món nước"
        HAI_SAN = "hai_san", "Hải sản"
        DO_AN_NHANH = "do_an_nhanh", "Đồ ăn nhanh"
        DO_UONG = "do_uong", "Đồ uống / Cà phê"
        KHAC = "khac", "Khác"

    ten_quan = models.CharField("Tên quán", max_length=200)
    slug = models.SlugField(
        "Đường dẫn (slug)",
        max_length=220,
        unique=True,
        blank=True,
        help_text="Bỏ trống để hệ thống tự tạo từ tên quán." #Tự động tạo tên qua save()  ,
    )
    dia_chi = models.CharField("Địa chỉ", max_length=255)
    quan_huyen = models.CharField("Quận/Huyện", max_length=100)
    thanh_pho = models.CharField("Thành phố", max_length=100)
    so_dien_thoai = models.CharField("Số điện thoại", max_length=20, blank=True)
    loai_am_thuc = models.CharField(
        "Loại ẩm thực",
        max_length=30,
        choices=LoaiAmThuc.choices,
        default=LoaiAmThuc.MON_VIET,
    )
    gia_tu = models.PositiveIntegerField(
        "Giá từ (VNĐ)",
        default=0,
        help_text="Giá thấp nhất của một món, đơn vị VNĐ. Ví dụ: 30000",
    )
    gia_den = models.PositiveIntegerField(
        "Giá đến (VNĐ)",
        default=0,
        help_text="Giá cao nhất của một món, đơn vị VNĐ. Ví dụ: 150000",
    )
    gio_mo_cua = models.TimeField("Giờ mở cửa", blank=True, null=True)
    gio_dong_cua = models.TimeField("Giờ đóng cửa", blank=True, null=True)
    ngay_tao = models.DateTimeField("Ngày tạo", auto_now_add=True)
    ngay_cap_nhat = models.DateTimeField("Ngày cập nhật", auto_now=True)

    class Meta:
        verbose_name = "Nhà hàng"
        verbose_name_plural = "Danh sách nhà hàng"
        ordering = ["ten_quan"]

    def __str__(self):
        return f"{self.ten_quan} ({self.quan_huyen}, {self.thanh_pho})"

    def save(self, *args, **kwargs):
        """Tự sinh slug duy nhất từ tên quán nếu người dùng để trống."""
        if not self.slug:
            goc = slugify(self.ten_quan)[:200] or "nha-hang"
            #[:200] cắt đúng 200 ký tự chừa 20 để điền hậu tố
            slug = goc
            so_thu_tu = 2
            while (
                    NhaHang.objects.filter(slug=slug).exclude(pk=self.pk).exists()
            ):
                slug = f"{goc}-{so_thu_tu}"
                so_thu_tu += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def khoang_gia(self):
        """Chuỗi hiển thị khoảng giá, ví dụ: '30.000đ - 150.000đ'."""
        return f"{self.gia_tu:,}đ - {self.gia_den:,}đ".replace(",", ".")


# ===========================================================================
# 3. THẺ MÓN ĂN (TAG)
# ===========================================================================
class TheMonAn(models.Model):
    """Thẻ phân loại món ăn, ví dụ: Phở, Bún chả, Trà sữa, Đồ chay..."""

    ten_the = models.CharField("Tên thẻ", max_length=100, unique=True)
    slug = models.SlugField(
        "Đường dẫn (slug)",
        max_length=120,
        unique=True,
        blank=True,
        help_text="Bỏ trống để hệ thống tự tạo từ tên thẻ.",
    )
    ngay_tao = models.DateTimeField("Ngày tạo", auto_now_add=True)

    class Meta:
        verbose_name = "Thẻ món ăn"
        verbose_name_plural = "Danh sách thẻ món ăn"
        ordering = ["ten_the"]

    def __str__(self):
        return self.ten_the

    def save(self, *args, **kwargs):
        """Tự sinh slug duy nhất từ tên thẻ nếu để trống."""
        if not self.slug:
            goc = slugify(self.ten_the)[:100] or "the-mon-an"
            slug = goc
            so_thu_tu = 2
            while (
                TheMonAn.objects.filter(slug=slug).exclude(pk=self.pk).exists()
            ):
                slug = f"{goc}-{so_thu_tu}"
                so_thu_tu += 1
            self.slug = slug
        super().save(*args, **kwargs)


# ===========================================================================
# 4. BÀI REVIEW
# ===========================================================================
class BaiReview(models.Model):
    """Bài đánh giá của một người dùng về một nhà hàng."""

    class TrangThai(models.TextChoices):
        CHO_DUYET = "cho_duyet", "Chờ duyệt"
        DA_DANG = "da_dang", "Đã đăng"
        AN = "an", "Ẩn"

    nguoi_dung = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bai_review",
        verbose_name="Người viết",
    )
    nha_hang = models.ForeignKey(
        NhaHang,
        on_delete=models.CASCADE,
        related_name="bai_review",
        verbose_name="Nhà hàng",
    )
    tieu_de = models.CharField("Tiêu đề", max_length=255)
    noi_dung = models.TextField("Nội dung review")
    diem_trung_binh = models.FloatField(
        "Điểm trung bình",
        default=0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        help_text="Từ 0.0 đến 5.0, được cập nhật tự động khi chấm điểm.",
    )
    trang_thai = models.CharField(
        "Trạng thái",
        max_length=20,
        choices=TrangThai.choices,
        default=TrangThai.CHO_DUYET,
    )
    luot_thich = models.PositiveIntegerField(
        "Lượt thích",
        default=0,
        help_text="Số lượt thích (bộ đếm nhanh, cập nhật từ bảng LuotThich).",
    )
    the_mon_an = models.ManyToManyField(
        TheMonAn,
        related_name="bai_review",
        blank=True,
        verbose_name="Thẻ món ăn",
    )
    ngay_tao = models.DateTimeField("Ngày tạo", auto_now_add=True)
    ngay_cap_nhat = models.DateTimeField("Ngày cập nhật", auto_now=True)

    class Meta:
        verbose_name = "Bài review"
        verbose_name_plural = "Các bài review"
        ordering = ["-ngay_tao"]

    def __str__(self):
        return f"{self.tieu_de} - {self.nha_hang.ten_quan}"


# ===========================================================================
# 5. CHẤM ĐIỂM
# [SUA 2026-11-17] Trước đây dùng OneToOneField -> mỗi bài chỉ có MỘT bản ghi
# điểm, nên chỉ tác giả bài (hoặc admin) mới chấm được.
# Nay đổi sang ForeignKey + them nguoi_dung + UniqueConstraint: MỌI thành viên
# đã đăng nhập đều chấm được, mỗi người một lượt/bài.
# ===========================================================================
class ChamDiem(models.Model):
    """4 tiêu chí chấm điểm, mỗi tiêu chí từ 1.0 đến 5.0."""

    # [SUA] OneToOneField -> ForeignKey, related_name mới
    bai_review = models.ForeignKey(
        BaiReview,
        on_delete=models.CASCADE,
        related_name="danh_sach_cham_diem",
        verbose_name="Bài review",
    )
    # [MOI] Ai là người chấm điểm này
    nguoi_dung = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cham_diem",
        verbose_name="Người chấm",
        null=True,
        blank=True,
        help_text="Tạm cho phép null để giữ dữ liệu cũ; API luôn tự gán.",
    )
    vi_giac = models.FloatField(
        "Vị giác",
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)],
    )
    khong_gian = models.FloatField(
        "Không gian",
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)],
    )
    phuc_vu = models.FloatField(
        "Phục vụ",
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)],
    )
    gia_ca = models.FloatField(
        "Giá cả",
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)],
    )
    ngay_tao = models.DateTimeField("Ngày tạo", auto_now_add=True)
    ngay_cap_nhat = models.DateTimeField("Ngày cập nhật", auto_now=True)

    class Meta:
        verbose_name = "Chấm điểm"
        verbose_name_plural = "Chấm điểm"
        ordering = ["-ngay_tao"]
        # [MOI] Mỗi người chỉ chấm một bài một lần
        constraints = [
            models.UniqueConstraint(
                fields=["nguoi_dung", "bai_review"],
                name="uniq_cham_diem_nguoi_bai",
            )
        ]

    def __str__(self):
        nguoi_cham = self.nguoi_dung or "Ẩn danh"
        return f'{nguoi_cham} chấm "{self.bai_review.tieu_de}" ({self.diem_trung_binh}/5)'

    @property
    def diem_trung_binh(self):
        """Trung bình cộng 4 tiêu chí của RIÊNG lượt chấm này."""
        return round(
            (self.vi_giac + self.khong_gian + self.phuc_vu + self.gia_ca) / 4,
            1,
        )

    @staticmethod
    def cap_nhat_diem_trung_binh(bai_review_id):
        """
        [MOI] Tính lại điểm trung bình của bài review từ TẤT CẢ lượt chấm.
        Trước đây chỉ lấy điểm của bản ghi duy nhất.
        """
        ket_qua = ChamDiem.objects.filter(
            bai_review_id=bai_review_id
        ).aggregate(
            tb=Avg(
                (F("vi_giac") + F("khong_gian") + F("phuc_vu") + F("gia_ca"))
                / 4.0
            )
        )
        BaiReview.objects.filter(pk=bai_review_id).update(
            diem_trung_binh=round(ket_qua["tb"] or 0, 1)
        )

    def save(self, *args, **kwargs):
        """[SUA] Lưu điểm rồi tính lại trung bình cộng của mọi lượt chấm."""
        super().save(*args, **kwargs)
        self.cap_nhat_diem_trung_binh(self.bai_review_id)

    def delete(self, *args, **kwargs):
        """[MOI] Khi xóa một lượt chấm, tính lại điểm trung bình của bài."""
        bai_review_id = self.bai_review_id
        ket_qua = super().delete(*args, **kwargs)
        self.cap_nhat_diem_trung_binh(bai_review_id)
        return ket_qua


# ===========================================================================
# 6. HÌNH ẢNH CỦA BÀI REVIEW
# ===========================================================================
class HinhAnh(models.Model):
    """Ảnh minh họa cho bài review, lưu tại thư mục media/reviews/."""

    bai_review = models.ForeignKey(
        BaiReview,
        on_delete=models.CASCADE,
        related_name="hinh_anh",
        verbose_name="Bài review",
    )
    # [MOI] Ai là người tải ảnh lên (để biết ai được sửa/xóa ảnh)
    nguoi_dung = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hinh_anh",
        verbose_name="Người tải ảnh",
        null=True,
        blank=True,
        help_text="Tạm cho phép null để giữ dữ liệu cũ; API luôn tự gán.",
    )
    hinh_anh = models.ImageField(
        "Hình ảnh",
        upload_to="reviews/",
        help_text="Chọn ảnh JPG/PNG từ máy tính để tải lên.",
    )
    mo_ta = models.CharField("Mô tả", max_length=255, blank=True)
    la_anh_bia = models.BooleanField(
        "Là ảnh bìa",
        default=False,
        help_text="Mỗi bài review chỉ nên có một ảnh bìa.",
    )
    thu_tu = models.PositiveIntegerField(
        "Thứ tự hiển thị",
        default=0,
        help_text="Số nhỏ hơn sẽ hiển thị trước.",
    )
    ngay_tao = models.DateTimeField("Ngày tạo", auto_now_add=True)

    class Meta:
        verbose_name = "Hình ảnh"
        verbose_name_plural = "Danh sách hình ảnh"
        ordering = ["thu_tu", "id"]

    def __str__(self):
        return f"Ảnh {self.thu_tu} - {self.bai_review.tieu_de}"


# ===========================================================================
# 7. BÌNH LUẬN
# ===========================================================================
class BinhLuan(models.Model):
    """Bình luận của người dùng dưới một bài review."""

    bai_review = models.ForeignKey(
        BaiReview,
        on_delete=models.CASCADE,
        related_name="binh_luan",
        verbose_name="Bài review",
    )
    nguoi_dung = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="binh_luan",
        verbose_name="Người bình luận",
    )
    noi_dung = models.TextField("Nội dung bình luận")
    luot_thich = models.PositiveIntegerField("Lượt thích", default=0)
    ngay_tao = models.DateTimeField("Ngày tạo", auto_now_add=True)

    class Meta:
        verbose_name = "Bình luận"
        verbose_name_plural = "Bình luận"
        ordering = ["-ngay_tao"]

    def __str__(self):
        return f"{self.nguoi_dung} bình luận về \"{self.bai_review.tieu_de}\""


# ===========================================================================
# 8. LƯỢT THÍCH BÀI REVIEW
# ===========================================================================
class LuotThich(models.Model):
    """Ghi nhận một người dùng đã thích một bài review."""

    nguoi_dung = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="luot_thich",
        verbose_name="Người dùng",
    )
    bai_review = models.ForeignKey(
        BaiReview,
        on_delete=models.CASCADE,
        related_name="danh_sach_luot_thich",
        verbose_name="Bài review",
    )
    ngay_tao = models.DateTimeField("Ngày thích", auto_now_add=True)

    class Meta:
        verbose_name = "Lượt thích"
        verbose_name_plural = "Lượt thích"
        ordering = ["-ngay_tao"]
        # Một người chỉ được thích một bài review một lần
        constraints = [
            models.UniqueConstraint(
                fields=["nguoi_dung", "bai_review"],
                name="uniq_luot_thich_nguoi_bai",
            )
        ]

    def __str__(self):
        return f"{self.nguoi_dung} thích \"{self.bai_review.tieu_de}\""


# ===========================================================================
# 9. QUÁN YÊU THÍCH (BOOKMARK)
# ===========================================================================
class QuanYeuThich(models.Model):
    """Người dùng lưu một nhà hàng vào danh sách yêu thích."""

    nguoi_dung = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quan_yeu_thich",
        verbose_name="Người dùng",
    )
    nha_hang = models.ForeignKey(
        NhaHang,
        on_delete=models.CASCADE,
        related_name="quan_yeu_thich",
        verbose_name="Nhà hàng",
    )
    ngay_tao = models.DateTimeField("Ngày lưu", auto_now_add=True)

    class Meta:
        verbose_name = "Quán yêu thích"
        verbose_name_plural = "Quán yêu thích"
        ordering = ["-ngay_tao"]
        # Mỗi người chỉ lưu một quán một lần
        constraints = [
            models.UniqueConstraint(
                fields=["nguoi_dung", "nha_hang"],
                name="uniq_quan_yeu_thich",
            )
        ]

    def __str__(self):
        return f"{self.nguoi_dung} yêu thích {self.nha_hang.ten_quan}"


# ===========================================================================
# 10. THEO DÕI NGƯỜI DÙNG
# ===========================================================================
class TheoDoi(models.Model):
    """Quan hệ theo dõi giữa hai người dùng (giống Follow trên mạng xã hội)."""

    nguoi_theo_doi = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dang_theo_doi",
        verbose_name="Người theo dõi",
    )
    nguoi_duoc_theo_doi = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="nguoi_theo_doi",
        verbose_name="Người được theo dõi",
    )
    ngay_tao = models.DateTimeField("Ngày theo dõi", auto_now_add=True)

    class Meta:
        verbose_name = "Theo dõi"
        verbose_name_plural = "Theo dõi"
        ordering = ["-ngay_tao"]
        # Không thể theo dõi cùng một người hai lần
        constraints = [
            models.UniqueConstraint(
                fields=["nguoi_theo_doi", "nguoi_duoc_theo_doi"],
                name="uniq_theo_doi",
            ),
            # Chặn tự theo dõi chính mình ngay ở tầng cơ sở dữ liệu
            models.CheckConstraint(
                condition=~models.Q(
                    nguoi_theo_doi=models.F("nguoi_duoc_theo_doi")
                ),
                name="ck_theo_doi_khong_tu_theo_doi",
            ),
        ]

    def __str__(self):
        return f"{self.nguoi_theo_doi} theo dõi {self.nguoi_duoc_theo_doi}"
