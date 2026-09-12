"""Custom permissions for the shop API."""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsVendorOrReadOnly(BasePermission):
    """Allow authenticated users to read and vendors to create resources."""

    message = "Only vendors may create stores or products."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return (
            request.user.is_authenticated
            and request.user.groups.filter(name="Vendors").exists()
        )


class IsStoreOwner(BasePermission):
    """Allow a vendor to add products only to a store they own."""

    message = "You may only add products to your own store."

    def has_object_permission(self, request, view, obj):
        return obj.owner_id == request.user.id
