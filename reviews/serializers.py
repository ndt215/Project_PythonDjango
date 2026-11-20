"""
ModelSerializer cho các bảng chính của app reviews.

Serializer có nhiệm vụ:
1. Chuyển Model (Python) -> JSON để trả về cho client.
2. Kiểm tra dữ liệu (validate) khi client gửi JSON lên để tạo/cập nhật.

Tài liệu: https://www.django-rest-framework.org/api-guide/serializers/
"""

from django.contrib.auth import authenticate
from rest_framework import serializers

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


# ===========================================================================
# NGƯỜI DÙNG
# ===========================================================================
class NguoiDungSerializer(serializers.ModelSerializer):
    """Hiển thị thông tin người dùng, có hỗ trợ đặt mật khẩu khi tạo mới."""

    # Client gửi lên trường "mat_khau", hệ thống băm ra trường "password".
    mat_khau = serializers.CharField(
        write_only=True,
        required=False,
        min_length=6,
        help_text="Mật khẩu (tối thiểu 6 ký tự), không bao giờ được trả về.",
    )

    class Meta:
        model = NguoiDung
        fields = [
            "id",
            "username",
            "ho_ten",
            "email",
            "anh_dai_dien",
            "tieu_su",
            "vai_tro",
            "trang_thai",
            "mat_khau",
            "ngay_tao",
        ]
        read_only_fields = ["id", "ngay_tao", "vai_tro", "trang_thai"]

    def create(self, validated_data):
        """Băm mật khẩu trước khi lưu vào CSDL (không lưu mật khẩu thô)."""
        mat_khau = validated_data.pop("password", None)
        nguoi_dung = NguoiDung(**validated_data)

        if mat_khau:
            nguoi_dung.set_password(mat_khau)
        else:
            # Không có mật khẩu -> tài khoản không thể đăng nhập bằng mật khẩu.
            nguoi_dung.set_unusable_password()

        nguoi_dung.save()
        return nguoi_dung

    def update(self, instance, validated_data):
        """Cập nhật thông tin, nếu có mật khẩu mới thì băm lại."""
        mat_khau = validated_data.pop("password", None)
        instance = super().update(instance, validated_data)

        if mat_khau:
            instance.set_password(mat_khau)
            instance.save()

        return instance


# ===========================================================================
# NHÀ HÀNG
# ===========================================================================
class NhaHangSerializer(serializers.ModelSerializer):
    khoang_gia = serializers.ReadOnlyField()
    so_bai_review = serializers.IntegerField(
        source="bai_review.count",
        read_only=True,
    )

    class Meta:
        model = NhaHang
        fields = [
            "id",
            "ten_quan",
            "slug",
            "dia_chi",
            "quan_huyen",
            "thanh_pho",
            "so_dien_thoai",
            "loai_am_thuc",
            "gia_tu",
            "gia_den",
            "khoang_gia",
            "gio_mo_cua",
            "gio_dong_cua",
            "so_bai_review",
            "ngay_tao",
            "ngay_cap_nhat",
        ]
        read_only_fields = ["id", "slug", "ngay_tao", "ngay_cap_nhat"]

    def validate(self, attrs):
        """Kiểm tra giá đến không được nhỏ hơn giá từ."""
        gia_tu = attrs.get("gia_tu", getattr(self.instance, "gia_tu", 0))
        gia_den = attrs.get("gia_den", getattr(self.instance, "gia_den", 0))

        if gia_den and gia_tu and gia_den < gia_tu:
            raise serializers.ValidationError(
                {"gia_den": "Giá đến phải lớn hơn hoặc bằng giá từ."}
            )
        return attrs


# ===========================================================================
# THẺ MÓN ĂN
# ===========================================================================
class TheMonAnSerializer(serializers.ModelSerializer):
    so_bai_review = serializers.IntegerField(
        source="bai_review.count",
        read_only=True,
    )

    class Meta:
        model = TheMonAn
        fields = ["id", "ten_the", "slug", "so_bai_review", "ngay_tao"]
        read_only_fields = ["id", "slug", "ngay_tao"]


# ===========================================================================
# CHẤM ĐIỂM
# ===========================================================================
class ChamDiemSerializer(serializers.ModelSerializer):
    # [MOI] Người chấm do server gán, client không được tự chọn
    nguoi_dung = serializers.PrimaryKeyRelatedField(read_only=True)
    ten_nguoi_dung = serializers.CharField(
        source="nguoi_dung.username",
        read_only=True,
    )
    diem_trung_binh = serializers.ReadOnlyField()

    class Meta:
        model = ChamDiem
        fields = [
            "id",
            "bai_review",
            "nguoi_dung",
            "ten_nguoi_dung",
            "vi_giac",
            "khong_gian",
            "phuc_vu",
            "gia_ca",
            "diem_trung_binh",
            "ngay_tao",
            "ngay_cap_nhat",
        ]
        read_only_fields = [
            "id",
            "nguoi_dung",
            "diem_trung_binh",
            "ngay_tao",
            "ngay_cap_nhat",
        ]


# ===========================================================================
# HÌNH ẢNH
# ===========================================================================
class HinhAnhSerializer(serializers.ModelSerializer):
    # [MOI] Người tải ảnh do server gán
    nguoi_dung = serializers.PrimaryKeyRelatedField(read_only=True)
    ten_nguoi_dung = serializers.CharField(
        source="nguoi_dung.username",
        read_only=True,
    )

    class Meta:
        model = HinhAnh
        fields = [
            "id",
            "bai_review",
            "nguoi_dung",
            "ten_nguoi_dung",
            "hinh_anh",
            "mo_ta",
            "la_anh_bia",
            "thu_tu",
            "ngay_tao",
        ]
        read_only_fields = ["id", "nguoi_dung", "ngay_tao"]


# ===========================================================================
# BÀI REVIEW
# ===========================================================================
class BaiReviewSerializer(serializers.ModelSerializer):
    # Thông tin đọc thêm để client không phải gọi thêm API
    ten_nguoi_dung = serializers.CharField(
        source="nguoi_dung.username",
        read_only=True,
    )
    ten_nha_hang = serializers.CharField(
        source="nha_hang.ten_quan",
        read_only=True,
    )
    # [SUA] Một bài review có NHIỀU lượt chấm (trước đây là một)
    danh_sach_cham_diem = ChamDiemSerializer(many=True, read_only=True)
    hinh_anh = HinhAnhSerializer(many=True, read_only=True)
    danh_sach_the = TheMonAnSerializer(
        source="the_mon_an",
        many=True,
        read_only=True,
    )
    # Khi tạo/cập nhật, client gửi danh sách ID thẻ: "the_mon_an": [1, 2]
    the_mon_an = serializers.PrimaryKeyRelatedField(
        queryset=TheMonAn.objects.all(),
        many=True,
        required=False,
        write_only=True,
    )

    diem_cua_toi = serializers.SerializerMethodField()

    def get_diem_cua_toi(self, obj):
        """[MOI] Trả về lượt chấm của người đang gọi (nếu đã đăng nhập)."""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None

        cham_diem = obj.danh_sach_cham_diem.filter(
            nguoi_dung=request.user
        ).first()
        return ChamDiemSerializer(cham_diem).data if cham_diem else None

    class Meta:
        model = BaiReview
        fields = [
            "id",
            "nguoi_dung",
            "ten_nguoi_dung",
            "nha_hang",
            "ten_nha_hang",
            "tieu_de",
            "noi_dung",
            "diem_trung_binh",
            "trang_thai",
            "luot_thich",
            "the_mon_an",
            "danh_sach_the",
            "danh_sach_cham_diem",
            "diem_cua_toi",
            "hinh_anh",
            "ngay_tao",
            "ngay_cap_nhat",
        ]
        read_only_fields = [
            "id",
            # [SUA] Không cho client tự đổi chủ bài / tự duyệt bài
            "nguoi_dung",
            "trang_thai",
            "diem_trung_binh",
            "luot_thich",
            "ngay_tao",
            "ngay_cap_nhat",
        ]


# ===========================================================================
# BÌNH LUẬN
# ===========================================================================
class BinhLuanSerializer(serializers.ModelSerializer):
    ten_nguoi_dung = serializers.CharField(
        source="nguoi_dung.username",
        read_only=True,
    )

    class Meta:
        model = BinhLuan
        fields = [
            "id",
            "bai_review",
            "nguoi_dung",
            "ten_nguoi_dung",
            "noi_dung",
            "luot_thich",
            "ngay_tao",
        ]
        read_only_fields = ["id","nguoi_dung", "luot_thich", "ngay_tao"]


# ===========================================================================
# CÁC BẢNG NỐI
# ===========================================================================
class LuotThichSerializer(serializers.ModelSerializer):
    class Meta:
        model = LuotThich
        fields = ["id", "nguoi_dung", "bai_review", "ngay_tao"]
        read_only_fields = ["id","nguoi_dung" , "ngay_tao"]


class QuanYeuThichSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuanYeuThich
        fields = ["id", "nguoi_dung", "nha_hang", "ngay_tao"]
        read_only_fields = ["id", "ngay_tao"]


class TheoDoiSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheoDoi
        fields = [
            "id",
            "nguoi_theo_doi",
            "nguoi_duoc_theo_doi",
            "ngay_tao",
        ]
        read_only_fields = ["id","nguoi_theo_doi", "ngay_tao"]

    def validate(self, attrs):
        nguoi_theo_doi = self.context["request"].user
        nguoi_duoc = attrs.get("nguoi_duoc_theo_doi")

        if nguoi_duoc and nguoi_duoc.pk == nguoi_theo_doi.pk:
            raise serializers.ValidationError(
                "Bạn không thể tự theo dõi chính mình."
            )
        return attrs

#   -------
#   DANG KY
#   -------
class DangKySerializer(serializers.ModelSerializer):
    mat_khau = serializers.CharField(
        label="Mật khẩu",
        write_only=True,
        min_length=6,
        trim_whitespace=False,
        style={"input_type": "password"},
        help_text="Tối thiểu 6 ký tự.",
        error_messages={
            "min_length": "Mật khẩu phải có ít nhất 6 ký tự.",
        },
    )
    mat_khau_2 = serializers.CharField(
        label="Nhập lại mật khẩu",
        write_only=True,
        min_length=6,
        trim_whitespace=False,
        style={"input_type": "password"},
        help_text="Gõ lại mật khẩu để xác nhận.",
        error_messages={
            "min_length": "Mật khẩu nhập lại phải có ít nhất 6 ký tự.",
        },
    )

    class Meta:
        model = NguoiDung
        fields = ["username", "email", "ho_ten", "mat_khau", "mat_khau_2"]
        extra_kwargs = {
            "username": {"label": "Tên đăng nhập"},
            "email": {"label": "Email"},
            "ho_ten": {"label": "Họ và tên"},
        }
    def validate(self, attrs):
        mat_khau = attrs.get("mat_khau")
        mat_khau_2 = attrs.get("mat_khau_2")

        if mat_khau and mat_khau_2 and mat_khau != mat_khau_2:
            raise serializers.ValidationError(
                {"mat_khau_2": "Mật khẩu nhập lại không khớp."}
            )

        return attrs

    def create(self, validated_data):
        validated_data.pop("mat_khau_2")
        mat_khau = validated_data.pop("mat_khau")

        validated_data.setdefault("vai_tro", NguoiDung.VaiTro.THANH_VIEN)

        return NguoiDung.objects.create_user(
            password=mat_khau,
            **validated_data,
        )


#   ---------------------
#    CHUC NANG DANG NHAP
#   ---------------------
class DangNhapSerializer(serializers.Serializer): #Khong phai mot bang nen kthua Serializer
    """Nhận username/password và xác thực với CSDL."""

    username = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate(self, attrs):
        user = authenticate(
            username=attrs.get("username"),
            password=attrs.get("password"),
        )

        if user is None:
            raise serializers.ValidationError(
                "Sai tên đăng nhập hoặc mật khẩu."
            )

        attrs["user"] = user
        return attrs