from rest_framework.permissions import BasePermission


class IsOrganizationMember(BasePermission):
    """Restrict access to objects belonging to the user's organization."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "organization_id")
            and request.user.organization_id is not None
        )
