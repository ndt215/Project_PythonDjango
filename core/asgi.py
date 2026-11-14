"""
Cấu hình ASGI - dùng cho web server bất đồng bộ (Uvicorn, Daphne...).

Tham khảo: https://docs.djangoproject.com/en/6.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

application = get_asgi_application()
