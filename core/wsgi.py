"""
Cấu hình WSGI - dùng cho các web server đồng bộ (Gunicorn, uWSGI...).

Tham khảo: https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

application = get_wsgi_application()
