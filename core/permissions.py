from rest_framework import permissions

from .models import SecurityLog
from .services import MembershipService


def _request_ip(request):
    return request.META.get("REMOTE_ADDR")


class IsProjectAdminOrReadOnly(permissions.BasePermission):
    """
    Cualquier miembro del proyecto puede leer.
    Solo un admin del proyecto puede modificar.
    """

    def has_object_permission(self, request, view, obj):
        project = obj.project if hasattr(obj, "project") else obj
        if request.method in permissions.SAFE_METHODS:
            return MembershipService.is_member(request.user, project)
        is_admin = MembershipService.is_admin(request.user, project)
        if not is_admin and MembershipService.is_member(request.user, project):
            SecurityLog.objects.create(
                user=request.user,
                action="permission_denied",
                detail=f"{request.method} {obj._meta.model_name}"[:255],
                ip_address=_request_ip(request),
            )
        return is_admin
