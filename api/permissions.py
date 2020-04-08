from rest_framework import permissions


class IsAllowedUser(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsCategoryOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.marathon.organizer == request.user


class IsSponsorOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.marathon.organizer == request.user


class IsMarathonOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.organizer == request.user
        

class IsPaymentOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or obj.marathon.organizer == request.user


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to check if user is admin
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin