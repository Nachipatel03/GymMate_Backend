from rest_framework.permissions import BasePermission

class HasRole(BasePermission):
    allowed_roles = []

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role.lower() in self.allowed_roles
        )


class IsAdmin(HasRole):
    allowed_roles = ["admin"]


class IsMember(HasRole):
    allowed_roles = ["member"]


class IsTrainer(HasRole):
    allowed_roles = ["trainer"]

class IsAdminOrTrainer(HasRole):   # 👈 HERE
    allowed_roles = ["admin", "trainer"]    
