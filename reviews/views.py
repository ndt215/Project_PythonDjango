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
#Phan quyen
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import SAFE_METHODS, AllowAny

from .permissions import ChuSoHuuHoacQuanTri, LaQuanTriVien, la_quan_tri

from rest_framework import generics

from .serializers import DangNhapSerializer
from .serializers import DangKySerializer

from django.contrib.auth import logout as django_logout
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated

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

    permission_classes = [LaQuanTriVien]

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

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [LaQuanTriVien()]



# ===========================================================================
# THẺ MÓN ĂN
# ===========================================================================
class TheMonAnViewSet(viewsets.ModelViewSet):
    """CRUD thẻ món ăn."""

    queryset = TheMonAn.objects.all()
    serializer_class = TheMonAnSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["ten_the"]

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [LaQuanTriVien()]



# ===========================================================================
# BÀI REVIEW
# ===========================================================================
class BaiReviewViewSet(viewsets.ModelViewSet):
    """CRUD bài review, kèm điểm, ảnh và danh sách thẻ."""

    queryset = BaiReview.objects.select_related(
        "nguoi_dung",
        "nha_hang",
    ).prefetch_related(
        "the_mon_an",
        "hinh_anh",
        # [MOI] nạp sẵn điểm + người chấm để tránh N+1 query
        "danh_sach_cham_diem__nguoi_dung",
    )
    serializer_class = BaiReviewSerializer
    # [SUA] Trước đây thiếu dòng này nên thành viên sửa/xóa được bài người khác
    permission_classes = [ChuSoHuuHoacQuanTri]
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
        user = self.request.user

        # 1. Lọc theo vai trò
        if not la_quan_tri(user):
            if user.is_authenticated:
                queryset = queryset.filter(
                    Q(trang_thai="da_dang") | Q(nguoi_dung=user)
                )
            else:
                queryset = queryset.filter(trang_thai="da_dang")


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

    def perform_create(self, serializer):
        serializer.save(nguoi_dung=self.request.user)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[LaQuanTriVien],
    )
    def duyet(self, request, pk=None):
        bai = self.get_object()
        bai.trang_thai = BaiReview.TrangThai.DA_DANG
        bai.save(update_fields=["trang_thai"])
        return Response({"trang_thai": bai.trang_thai})


# ===========================================================================
# CHẤM ĐIỂM
# [SUA 2026-11-17] Mọi thành viên đã đăng nhập đều được chấm điểm.
# Trước đây code chặn "chỉ chấm bài của mình" vì model là OneToOne.
# ===========================================================================
class ChamDiemViewSet(viewsets.ModelViewSet):
    """CRUD điểm đánh giá (mỗi người chấm một bài một lần)."""

    queryset = ChamDiem.objects.select_related("bai_review", "nguoi_dung")
    serializer_class = ChamDiemSerializer
    permission_classes = [ChuSoHuuHoacQuanTri]

    def get_queryset(self):
        """Lọc theo bài review: /api/cham-diem/?bai_review=1"""
        queryset = super().get_queryset()
        bai_review_id = self.request.query_params.get("bai_review")

        if bai_review_id:
            queryset = queryset.filter(bai_review_id=bai_review_id)

        return queryset

    def perform_create(self, serializer):
        bai = serializer.validated_data["bai_review"]

        # [MOI] Chỉ chấm bài đã đăng; tác giả/admin được chấm bài của mình
        if (
            bai.trang_thai != BaiReview.TrangThai.DA_DANG
            and not la_quan_tri(self.request.user)
            and bai.nguoi_dung_id != self.request.user.id
        ):
            raise PermissionDenied("Chỉ được chấm điểm bài đã đăng.")

        # [MOI] Chặn chấm trùng (UniqueConstraint cũng chặn, nhưng trả 400 đẹp hơn)
        if ChamDiem.objects.filter(
            bai_review=bai, nguoi_dung=self.request.user
        ).exists():
            raise ValidationError(
                {"chi_tiet": "Bạn đã chấm điểm bài này rồi."}
            )

        # [SUA] Tự gán người chấm, không tin dữ liệu client
        serializer.save(nguoi_dung=self.request.user)


# ===========================================================================
# HÌNH ẢNH
# [SUA 2026-11-17] Mọi thành viên đã đăng nhập đều được tải ảnh lên.
# Ảnh do ai tải thì người đó (hoặc admin) được sửa/xóa.
# ===========================================================================
class HinhAnhViewSet(viewsets.ModelViewSet):
    """Tải lên và quản lý ảnh của bài review (multipart/form-data)."""

    queryset = HinhAnh.objects.select_related("bai_review", "nguoi_dung")
    serializer_class = HinhAnhSerializer
    permission_classes = [ChuSoHuuHoacQuanTri]

    def get_queryset(self):
        """Lọc ảnh theo bài review: /api/hinh-anh/?bai_review=1"""
        queryset = super().get_queryset()

        # Khách không thấy ảnh của bài chưa đăng
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(bai_review__trang_thai="da_dang")

        bai_review_id = self.request.query_params.get("bai_review")

        if bai_review_id:
            queryset = queryset.filter(bai_review_id=bai_review_id)

        return queryset

    def perform_create(self, serializer):
        # [SUA] Bỏ kiểm tra "chỉ chủ bài"; mọi thành viên đều được upload
        # và server tự gán người tải ảnh.
        serializer.save(nguoi_dung=self.request.user)


# ===========================================================================
# BÌNH LUẬN
# ===========================================================================
class BinhLuanViewSet(viewsets.ModelViewSet):
    """CRUD bình luận, lọc được theo bài review."""

    queryset = BinhLuan.objects.select_related("nguoi_dung", "bai_review")
    serializer_class = BinhLuanSerializer
    permission_classes = [ChuSoHuuHoacQuanTri]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Khách không thấy bình luận của bài chưa đăng
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(bai_review__trang_thai="da_dang")

        bai_review_id = self.request.query_params.get("bai_review")
        if bai_review_id:
            queryset = queryset.filter(bai_review_id=bai_review_id)

        return queryset

    def perform_create(self, serializer):
        serializer.save(nguoi_dung=self.request.user)


# ===========================================================================
# CÁC BẢNG NỐI
# ===========================================================================
class LuotThichViewSet(viewsets.ModelViewSet):
    """Thích / bỏ thích bài review (mỗi người - mỗi bài chỉ một bản ghi)."""

    queryset = LuotThich.objects.select_related("nguoi_dung", "bai_review")
    serializer_class = LuotThichSerializer
    permission_classes = [ChuSoHuuHoacQuanTri]

    def perform_create(self, serializer):
        serializer.save(nguoi_dung=self.request.user)


class QuanYeuThichViewSet(viewsets.ModelViewSet):
    """Lưu / bỏ lưu nhà hàng yêu thích."""

    queryset = QuanYeuThich.objects.select_related("nguoi_dung", "nha_hang")
    serializer_class = QuanYeuThichSerializer
    permission_classes = [ChuSoHuuHoacQuanTri]

    def perform_create(self, serializer):
        serializer.save(nguoi_dung=self.request.user)


class TheoDoiViewSet(viewsets.ModelViewSet):
    """Theo dõi / bỏ theo dõi người dùng khác."""

    queryset = TheoDoi.objects.select_related(
        "nguoi_theo_doi", "nguoi_duoc_theo_doi"
    )
    serializer_class = TheoDoiSerializer
    permission_classes = [ChuSoHuuHoacQuanTri]

    def perform_create(self, serializer):
        serializer.save(nguoi_theo_doi=self.request.user)


# ===========================================================================
# ENDPOINT TỔNG QUAN (dễ kiểm tra API đã chạy hay chưa)
# ===========================================================================
class TongQuanView(APIView):
    """
    GET /api/tong-quan/

    Trả về số lượng bản ghi của 10 bảng, giúp người mới kiểm tra nhanh
    dữ liệu mẫu sau khi chạy migrate.
    """
    permission_classes = [LaQuanTriVien]

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


class DangNhapView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = DangNhapSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "nguoi_dung": NguoiDungSerializer(user).data,
            }
        )

class DangKyView(generics.CreateAPIView): #CreateApiView de tao nhu 1 Browsable API
    serializer_class = DangKySerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "nguoi_dung": NguoiDungSerializer(user).data,
            },
            status=201,
        )

class DangXuatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.auth is not None:
            request.auth.delete()      # xóa token trong CSDL
        else:
            django_logout(request)      # đăng xuất session (Browsable API)

        return Response({"thong_bao": "Đăng xuất thành công."})


#Kiem tra token con hieu luc khong?
class HoSoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(NguoiDungSerializer(request.user).data)
