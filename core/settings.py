"""
Cấu hình Django 6.1 cho dự án "Măm Măm Food Review".

Mọi thiết lập quan trọng đều được chú thích bằng tiếng Việt để người mới
dễ đọc và dễ chỉnh sửa. File này được tạo bởi lệnh:
    django-admin startproject core .

Lưu ý: Django 6.1 yêu cầu Python 3.12 trở lên.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# ĐƯỜNG DẪN GỐC
# BASE_DIR trỏ tới thư mục chứa manage.py (thư mục gốc của dự án).
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# BẢO MẬT
# SECRET_KEY chỉ dùng khi phát triển. Khi triển khai thật, hãy đọc giá trị này
# từ biến môi trường (os.environ) và tuyệt đối không đưa lên GitHub.
# ---------------------------------------------------------------------------
SECRET_KEY = "django-insecure-mam-mam-food-review-2024-hay-doi-key-nay-khi-di-lam-that"

# DEBUG = True giúp hiển thị lỗi chi tiết và phục vụ file media khi dev.
# Khi chạy thật (production) phải đặt DEBUG = False.
DEBUG = True

# Cho phép tất cả host truy cập, thuận tiện khi test API bằng Postman/điện thoại.
ALLOWED_HOSTS = ["*"]


# ---------------------------------------------------------------------------
# ỨNG DỤNG ĐÃ CÀI ĐẶT
# 'rest_framework' -> Django REST Framework (xây dựng API JSON)
# 'corsheaders'    -> Cho phép ứng dụng web/mobile khác gọi API
# 'reviews'        -> Ứng dụng chính chứa 10 bảng nghiệp vụ
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Thư viện bên thứ ba
    "rest_framework",
    "corsheaders",
    # Ứng dụng của dự án
    "reviews",
]


# ---------------------------------------------------------------------------
# MIDDLEWARE
# CorsMiddleware nên đặt càng sớm càng tốt (đặc biệt trước CommonMiddleware).
# ---------------------------------------------------------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# File chứa danh sách URL gốc của toàn dự án
ROOT_URLCONF = "core.urls"


# ---------------------------------------------------------------------------
# TEMPLATE
# Phục vụ giao diện Admin và trang "Browsable API" của DRF.
# ---------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"


# ---------------------------------------------------------------------------
# CƠ SỞ DỮ LIỆU
# Dùng SQLite mặc định, file db.sqlite3 nằm ngay cạnh manage.py.
# File này được tạo tự động khi chạy: python manage.py migrate
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ---------------------------------------------------------------------------
# MÔ HÌNH NGƯỜI DÙNG TÙY BIẾN
# Dùng bảng NguoiDung trong app reviews (kế thừa AbstractUser của Django).
# Lưu ý: phải khai báo dòng này TRƯỚC khi chạy migrate lần đầu.
# ---------------------------------------------------------------------------
AUTH_USER_MODEL = "reviews.NguoiDung"


# ---------------------------------------------------------------------------
# KIỂM TRA MẬT KHẨU
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# ---------------------------------------------------------------------------
# NGÔN NGỮ & THỜI GIAN
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "vi"
TIME_ZONE = "Asia/Ho_Chi_Minh"
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------------
# FILE TĨNH (CSS/JS của trang Admin) VÀ FILE MEDIA (ảnh người dùng upload)
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ---------------------------------------------------------------------------
# GIÁ TRỊ MẶC ĐỊNH CHO KHÓA CHÍNH
# ---------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ---------------------------------------------------------------------------
# CẤU HÌNH DJANGO REST FRAMEWORK
# - Phân trang 10 bản ghi / trang để API gọn gàng.
# - Cho phép mọi người gọi API (chưa cần đăng nhập) trong giai đoạn học.
# - Hiển thị giao diện Browsable API để test trực tiếp trên trình duyệt.
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
}


# ---------------------------------------------------------------------------
# CẤU HÌNH CORS
# Cho phép mọi nguồn gọi API. Khi chạy thật nên thay bằng danh sách cụ thể:
# CORS_ALLOWED_ORIGINS = ["https://mammam.vn", "http://localhost:3000"]
# ---------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
