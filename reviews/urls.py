"""
Định tuyến API của app reviews.

Dùng DefaultRouter để tự sinh route chuẩn REST cho từng ViewSet.
Router cũng tạo sẵn trang gốc /api/ liệt kê tất cả endpoint (rất tiện để test).
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

# Đăng ký 10 endpoint tương ứng 10 bảng nghiệp vụ
router.register("nguoi-dung", views.NguoiDungViewSet, basename="nguoi-dung")
router.register("nha-hang", views.NhaHangViewSet, basename="nha-hang")
router.register("the-mon-an", views.TheMonAnViewSet, basename="the-mon-an")
router.register("bai-review", views.BaiReviewViewSet, basename="bai-review")
router.register("cham-diem", views.ChamDiemViewSet, basename="cham-diem")
router.register("hinh-anh", views.HinhAnhViewSet, basename="hinh-anh")
router.register("binh-luan", views.BinhLuanViewSet, basename="binh-luan")
router.register("luot-thich", views.LuotThichViewSet, basename="luot-thich")
router.register(
    "quan-yeu-thich",
    views.QuanYeuThichViewSet,
    basename="quan-yeu-thich",
)
router.register("theo-doi", views.TheoDoiViewSet, basename="theo-doi")

urlpatterns = [
    path("", include(router.urls)),
    path("tong-quan/", views.TongQuanView.as_view(), name="tong-quan"),
]
