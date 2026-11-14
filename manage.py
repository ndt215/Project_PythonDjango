#!/usr/bin/env python
"""Công cụ dòng lệnh của Django để quản lý dự án.

Các lệnh thường dùng (chạy trong Terminal của PyCharm):

    python manage.py makemigrations   # Sinh file migration từ models.py
    python manage.py migrate          # Tạo các bảng trong db.sqlite3
    python manage.py createsuperuser  # Tạo tài khoản quản trị
    python manage.py runserver        # Chạy server API
"""

import os
import sys


def main():
    """Chạy các tác vụ quản trị của Django."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Không import được Django. Bạn đã kích hoạt môi trường ảo (virtualenv) "
            "và chạy 'pip install -r requirements.txt' chưa?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
