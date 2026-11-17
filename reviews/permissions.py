from rest_framework.permissions import SAFE_METHODS, BasePermission


def la_quan_tri(user):
    """Quản trị viên = superuser HOẶC staff HOẶC vai_tro quản trị."""
    return bool(
        user
        and user.is_authenticated
        and (
            user.is_superuser
            or user.is_staff
            or getattr(user, "vai_tro", "") == "quan_tri_vien"
        )
    )


class LaQuanTriVien(BasePermission):
    """Chỉ quản trị viên."""

    message = "Chỉ quản trị viên mới được thực hiện thao tác này."

    def has_permission(self, request, view):
        return la_quan_tri(request.user)


class ChuSoHuuHoacQuanTri(BasePermission):
    """
    - Ai cũng đọc được (GET).
    - Phải đăng nhập mới được ghi.
    - Chỉ chủ sở hữu hoặc quản trị viên mới được sửa/xóa.
    """

    message = "Bạn chỉ được thay đổi dữ liệu của chính mình."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if la_quan_tri(request.user):
            return True

        # Chủ sở hữu trực tiếp
        chu_so_huu_id = getattr(obj, "nguoi_dung_id", None)

        # Bảng TheoDoi dùng tên khác
        if chu_so_huu_id is None:
            chu_so_huu_id = getattr(obj, "nguoi_theo_doi_id", None)

        # HinhAnh / ChamDiem: chủ sở hữu nằm ở bài review
        if chu_so_huu_id is None and hasattr(obj, "bai_review"):
            chu_so_huu_id = obj.bai_review.nguoi_dung_id

        return chu_so_huu_id == request.user.id