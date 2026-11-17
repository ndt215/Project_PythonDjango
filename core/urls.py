"""
URL gốc của toàn dự án.

- /admin/  -> Trang quản trị Django
- /api/    -> Toàn bộ REST API của app reviews
- /media/  -> File ảnh người dùng upload (chỉ phục vụ khi DEBUG = True)
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("api-auth/", include("rest_framework.urls")), #Session API
    path("admin/", admin.site.urls),
    # Toàn bộ endpoint API nằm trong app reviews
    path("api/", include("reviews.urls")),
]

# Khi phát triển (DEBUG = True), Django tự phục vụ ảnh trong thư mục media/.
# Khi triển khai thật, hãy để Nginx/Apache hoặc dịch vụ lưu trữ đám mây làm việc này.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
