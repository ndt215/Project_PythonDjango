"""Cấu hình của app reviews."""

from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "reviews"
    verbose_name = "Quản lý Review Ẩm thực"
