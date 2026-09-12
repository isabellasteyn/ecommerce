"""REST API views for store, product, vendor, and review resources."""

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from .api_permissions import IsStoreOwner, IsVendorOrReadOnly
from .models import Product, Review, Store
from .serializers import (
    ProductSerializer, ReviewSerializer, StoreSerializer, VendorSerializer,
)
from .services.x_client import post_product, post_store


class VendorListView(generics.ListAPIView):
    """List vendors, with their active stores and products."""

    serializer_class = VendorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(groups__name="Vendors").distinct()


class StoreListCreateView(generics.ListCreateAPIView):
    """List active stores or create a store for the logged-in vendor."""

    serializer_class = StoreSerializer
    permission_classes = [IsVendorOrReadOnly]

    def get_queryset(self):
        return Store.objects.filter(is_active=True).select_related("owner")

    def perform_create(self, serializer):
        store = serializer.save(owner=self.request.user)
        post_store(store)


class StoreProductListCreateView(generics.ListCreateAPIView):
    """List a store's products or let its owner add a product."""

    serializer_class = ProductSerializer
    permission_classes = [IsVendorOrReadOnly]

    def get_store(self):
        return get_object_or_404(
            Store, pk=self.kwargs["store_pk"], is_active=True
        )

    def get_queryset(self):
        return Product.objects.filter(
            store=self.get_store(), is_active=True
        ).select_related("store")

    def perform_create(self, serializer):
        store = self.get_store()
        permission = IsStoreOwner()
        if not permission.has_object_permission(self.request, self, store):
            raise PermissionDenied(permission.message)
        product = serializer.save(store=store)
        post_product(product)


class ProductReviewListView(generics.ListAPIView):
    """Return all reviews for one active product."""

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        product = get_object_or_404(
            Product,
            pk=self.kwargs["product_pk"],
            is_active=True,
            store__is_active=True,
        )
        return Review.objects.filter(product=product).select_related("buyer")
