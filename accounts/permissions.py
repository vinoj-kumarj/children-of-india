from rest_framework.permissions import BasePermission


class IsCoordinator(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "coordinator"


class IsLead(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "lead"


class IsField(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "field"