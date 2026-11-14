"""
API Views cho app reviews.

Giai đoạn khung dự án, mỗi bảng dùng ModelViewSet để có sẵn đủ 5 thao tác
CRUD (List / Create / Retrieve / Update / Destroy) mà không phải viết nhiều code:

    GET    /api/nha-hang/          -> Danh sách (có phân trang)
    POST   /api/nha-hang/          -> Tạo mới
    GET    /api/nha-hang/{id}/     -> Xem chi tiết
    PUT    /api/nha-hang/{id}/     -> Cập nhật toàn bộ
    PATCH  /api/nha-hang/{id}/     -> Cập nhật một phần
    DELETE /api/nha-hang/{id}/     -> Xóa

Tài liệu: https://www.django-rest-framework.org/api-guide/viewsets/
"""

from rest_framework import filters, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    BaiReview,
    BinhLuan,
    ChamDiem,
    HinhAnh,
    LuotThich,
    NguoiDung,
    NhaHang,
    QuanYeuThich,
    TheMonAn,
    TheoDoi,
)
from .serializers import (
    BaiReviewSerializer,
    BinhLuanSerializer,
    ChamDiemSerializer,
    HinhAnhSerializer,
    LuotThichSerializer,
    NguoiDungSerializer,
    NhaHangSerializer,
    QuanYeuThichSerializer,
    TheMonAnSerializer,
    TheoDoiSerializer,
)


# ===========================================================================
# NGƯỜI DÙNG
# ===========================================================================
class NguoiDungViewSet(viewsets.ModelViewSet):
    """CRUD người dùng + tìm kiếm theo tên/username/email."""

    queryset = NguoiDung.objects.all().order_by("-ngay_tao")
    serializer_class = NguoiDungSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["username", "ho_ten", "email"]
    ordering_fields = ["ngay_tao", "username"]


# ===========================================================================
# NHÀ HÀNG
# ===========================================================================
class NhaHangViewSet(viewsets.ModelViewSet):
    """CRUD nhà hàng + tìm kiếm theo tên, địa chỉ, quận, thành phố."""

    queryset = NhaHang.objects.all()
    serializer_class = NhaHangSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["ten_quan", "dia_chi", "quan_huyen", "thanh_pho"]
    ordering_fields = ["ten_quan", "gia_tu", "ngay_tao"]

    def get_queryset(self):
        """Hỗ trợ lọc nhanh: /api/nha-hang/?loai_am_thuc=hai_san"""
        queryset = super().get_queryset()
        loai_am_thuc = self.request.query_params.get("loai_am_thuc")

        if loai_am_thuc:
            queryset = queryset.filter(loai_am_thuc=loai_am_thuc)

        return queryset


# ===========================================================================
# THẺ MÓN ĂN
# ===========================================================================
class TheMonAnViewSet(viewsets.ModelViewSet):
    """CRUD thẻ món ăn."""

    queryset = TheMonAn.objects.all()
    serializer_class = TheMonAnSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["ten_the"]


# ===========================================================================
# BÀI REVIEW
# ===========================================================================
class BaiReviewViewSet(viewsets.ModelViewSet):
    """CRUD bài review, kèm điểm, ảnh và danh sách thẻ."""

    queryset = BaiReview.objects.select_related(
        "nguoi_dung",
        "nha_hang",
    ).prefetch_related("the_mon_an", "hinh_anh")
    serializer_class = BaiReviewSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["tieu_de", "noi_dung", "nha_hang__ten_quan"]
    ordering_fields = ["ngay_tao", "diem_trung_binh", "luot_thich"]

    def get_queryset(self):
        """
        Lọc theo bài đã đăng và theo khóa ngoại:
            /api/bai-review/?nha_hang=1
            /api/bai-review/?nguoi_dung=2
            /api/bai-review/?trang_thai=da_dang
        """
        queryset = super().get_queryset()

        nha_hang_id = self.request.query_params.get("nha_hang")
        if nha_hang_id:
            queryset = queryset.filter(nha_hang_id=nha_hang_id)

        nguoi_dung_id = self.request.query_params.get("nguoi_dung")
        if nguoi_dung_id:
            queryset = queryset.filter(nguoi_dung_id=nguoi_dung_id)

        trang_thai = self.request.query_params.get("trang_thai")
        if trang_thai:
            queryset = queryset.filter(trang_thai=trang_thai)

        return queryset


# ===========================================================================
# CHẤM ĐIỂM
# ===========================================================================
class ChamDiemViewSet(viewsets.ModelViewSet):
    """CRUD điểm đánh giá (mỗi bài review chỉ có một bản ghi điểm)."""

    queryset = ChamDiem.objects.select_related("bai_review")
    serializer_class = ChamDiemSerializer


# ===========================================================================
# HÌNH ẢNH
# ===========================================================================
class HinhAnhViewSet(viewsets.ModelViewSet):
    """Tải lên và quản lý ảnh của bài review (multipart/form-data)."""

    queryset = HinhAnh.objects.select_related("bai_review")
    serializer_class = HinhAnhSerializer

    def get_queryset(self):
        """Lọc ảnh theo bài review: /api/hinh-anh/?bai_review=1"""
        queryset = super().get_queryset()
        bai_review_id = self.request.query_params.get("bai_review")

        if bai_review_id:
            queryset = queryset.filter(bai_review_id=bai_review_id)

        return queryset


# ===========================================================================
# BÌNH LUẬN
# ===========================================================================
class BinhLuanViewSet(viewsets.ModelViewSet):
    """CRUD bình luận, lọc được theo bài review."""

    queryset = BinhLuan.objects.select_related("nguoi_dung", "bai_review")
    serializer_class = BinhLuanSerializer

    def get_queryset(self):
        """Ví dụ: /api/binh-luan/?bai_review=1"""
        queryset = super().get_queryset()
        bai_review_id = self.request.query_params.get("bai_review")

        if bai_review_id:
            queryset = queryset.filter(bai_review_id=bai_review_id)

        return queryset


# ===========================================================================
# CÁC BẢNG NỐI
# ===========================================================================
class LuotThichViewSet(viewsets.ModelViewSet):
    """Thích / bỏ thích bài review (mỗi người - mỗi bài chỉ một bản ghi)."""

    queryset = LuotThich.objects.select_related("nguoi_dung", "bai_review")
    serializer_class = LuotThichSerializer


class QuanYeuThichViewSet(viewsets.ModelViewSet):
    """Lưu / bỏ lưu nhà hàng yêu thích."""

    queryset = QuanYeuThich.objects.select_related("nguoi_dung", "nha_hang")
    serializer_class = QuanYeuThichSerializer


class TheoDoiViewSet(viewsets.ModelViewSet):
    """Theo dõi / bỏ theo dõi người dùng khác."""

    queryset = TheoDoi.objects.select_related(
        "nguoi_theo_doi",
        "nguoi_duoc_theo_doi",
    )
    serializer_class = TheoDoiSerializer


# ===========================================================================
# ENDPOINT TỔNG QUAN (dễ kiểm tra API đã chạy hay chưa)
# ===========================================================================
class TongQuanView(APIView):
    """
    GET /api/tong-quan/

    Trả về số lượng bản ghi của 10 bảng, giúp người mới kiểm tra nhanh
    dữ liệu mẫu sau khi chạy migrate.
    """

    def get(self, request):
        du_lieu = {
            "nguoi_dung": NguoiDung.objects.count(),
            "nha_hang": NhaHang.objects.count(),
            "the_mon_an": TheMonAn.objects.count(),
            "bai_review": BaiReview.objects.count(),
            "cham_diem": ChamDiem.objects.count(),
            "hinh_anh": HinhAnh.objects.count(),
            "binh_luan": BinhLuan.objects.count(),
            "luot_thich": LuotThich.objects.count(),
            "quan_yeu_thich": QuanYeuThich.objects.count(),
            "theo_doi": TheoDoi.objects.count(),
        }

        return Response(
            {
                "thong_bao": "API Măm Măm Food Review đang hoạt động.",
                "so_luong_ban_ghi": du_lieu,
            }
        )
