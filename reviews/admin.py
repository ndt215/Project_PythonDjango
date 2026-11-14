"""
Đăng ký 10 Model vào trang quản trị Django (/admin/).

Nhờ file này, sau khi tạo superuser bạn có thể quản lý toàn bộ dữ liệu
(thêm quán, duyệt bài review, xem ảnh, bình luận...) bằng giao diện web.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

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

# ---------------------------------------------------------------------------
# Tiêu đề hiển thị trên trang Admin
# ---------------------------------------------------------------------------
admin.site.site_header = "Măm Măm Food Review - Quản trị"
admin.site.site_title = "Măm Măm Food Review"
admin.site.index_title = "Bảng điều khiển"


# ===========================================================================
# 1. NGƯỜI DÙNG
# Kế thừa UserAdmin để giữ nguyên chức năng đổi mật khẩu của Django.
# ===========================================================================
@admin.register(NguoiDung)
class NguoiDungAdmin(UserAdmin):
    list_display = [
        "username",
        "ho_ten",
        "email",
        "vai_tro",
        "trang_thai",
        "is_staff",
        "ngay_tao",
    ]
    list_filter = ["vai_tro", "trang_thai", "is_staff", "is_superuser"]
    search_fields = ["username", "ho_ten", "email"]
    ordering = ["-ngay_tao"]
    readonly_fields = ["ngay_tao", "ngay_cap_nhat", "last_login", "date_joined"]

    fieldsets = UserAdmin.fieldsets + (
        (
            "Thông tin Măm Măm",
            {
                "fields": (
                    "ho_ten",
                    "anh_dai_dien",
                    "tieu_su",
                    "vai_tro",
                    "trang_thai",
                    "ngay_tao",
                    "ngay_cap_nhat",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Thông tin Măm Măm",
            {
                "fields": (
                    "ho_ten",
                    "email",
                    "vai_tro",
                    "trang_thai",
                )
            },
        ),
    )


# ===========================================================================
# 2. NHÀ HÀNG
# ===========================================================================
@admin.register(NhaHang)
class NhaHangAdmin(admin.ModelAdmin):
    list_display = [
        "ten_quan",
        "quan_huyen",
        "thanh_pho",
        "loai_am_thuc",
        "khoang_gia",
        "so_dien_thoai",
        "ngay_tao",
    ]
    list_filter = ["loai_am_thuc", "thanh_pho", "quan_huyen"]
    search_fields = ["ten_quan", "dia_chi", "quan_huyen", "thanh_pho"]
    prepopulated_fields = {"slug": ("ten_quan",)}
    list_per_page = 20


# ===========================================================================
# 3. THẺ MÓN ĂN
# ===========================================================================
@admin.register(TheMonAn)
class TheMonAnAdmin(admin.ModelAdmin):
    list_display = ["ten_the", "slug", "ngay_tao"]
    search_fields = ["ten_the"]
    prepopulated_fields = {"slug": ("ten_the",)}


# ---------------------------------------------------------------------------
# Inline: hiển thị và nhập trực tiếp điểm / ảnh / bình luận trong bài review
# ---------------------------------------------------------------------------
class ChamDiemInline(admin.StackedInline):
    model = ChamDiem
    extra = 1
    max_num = 1


class HinhAnhInline(admin.TabularInline):
    model = HinhAnh
    extra = 1
    fields = ["hinh_anh", "mo_ta", "la_anh_bia", "thu_tu"]


class BinhLuanInline(admin.TabularInline):
    model = BinhLuan
    extra = 0
    fields = ["nguoi_dung", "noi_dung", "luot_thich", "ngay_tao"]
    readonly_fields = ["ngay_tao"]


# ===========================================================================
# 4. BÀI REVIEW
# ===========================================================================
@admin.register(BaiReview)
class BaiReviewAdmin(admin.ModelAdmin):
    list_display = [
        "tieu_de",
        "nha_hang",
        "nguoi_dung",
        "diem_trung_binh",
        "trang_thai",
        "luot_thich",
        "ngay_tao",
    ]
    list_filter = ["trang_thai", "ngay_tao", "the_mon_an"]
    search_fields = ["tieu_de", "noi_dung", "nha_hang__ten_quan"]
    filter_horizontal = ["the_mon_an"]
    readonly_fields = ["diem_trung_binh", "luot_thich", "ngay_tao", "ngay_cap_nhat"]
    inlines = [ChamDiemInline, HinhAnhInline, BinhLuanInline]
    list_per_page = 20


# ===========================================================================
# 5. CHẤM ĐIỂM
# ===========================================================================
@admin.register(ChamDiem)
class ChamDiemAdmin(admin.ModelAdmin):
    list_display = [
        "bai_review",
        "vi_giac",
        "khong_gian",
        "phuc_vu",
        "gia_ca",
        "diem_trung_binh",
        "ngay_cap_nhat",
    ]
    search_fields = ["bai_review__tieu_de"]


# ===========================================================================
# 6. HÌNH ẢNH
# ===========================================================================
@admin.register(HinhAnh)
class HinhAnhAdmin(admin.ModelAdmin):
    list_display = ["bai_review", "mo_ta", "la_anh_bia", "thu_tu", "ngay_tao"]
    list_filter = ["la_anh_bia"]
    search_fields = ["bai_review__tieu_de", "mo_ta"]


# ===========================================================================
# 7. BÌNH LUẬN
# ===========================================================================
@admin.register(BinhLuan)
class BinhLuanAdmin(admin.ModelAdmin):
    list_display = ["nguoi_dung", "bai_review", "noi_dung", "luot_thich", "ngay_tao"]
    list_filter = ["ngay_tao"]
    search_fields = ["noi_dung", "nguoi_dung__username", "bai_review__tieu_de"]


# ===========================================================================
# 8. LƯỢT THÍCH
# ===========================================================================
@admin.register(LuotThich)
class LuotThichAdmin(admin.ModelAdmin):
    list_display = ["nguoi_dung", "bai_review", "ngay_tao"]
    search_fields = ["nguoi_dung__username", "bai_review__tieu_de"]


# ===========================================================================
# 9. QUÁN YÊU THÍCH
# ===========================================================================
@admin.register(QuanYeuThich)
class QuanYeuThichAdmin(admin.ModelAdmin):
    list_display = ["nguoi_dung", "nha_hang", "ngay_tao"]
    search_fields = ["nguoi_dung__username", "nha_hang__ten_quan"]


# ===========================================================================
# 10. THEO DÕI
# ===========================================================================
@admin.register(TheoDoi)
class TheoDoiAdmin(admin.ModelAdmin):
    list_display = ["nguoi_theo_doi", "nguoi_duoc_theo_doi", "ngay_tao"]
    search_fields = [
        "nguoi_theo_doi__username",
        "nguoi_duoc_theo_doi__username",
    ]
