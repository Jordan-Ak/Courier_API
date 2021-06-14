from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj.user:
            return True
        
        return request.user.is_staff

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return  request.user.is_staff

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user.is_staff