"""Serializers defining the public representations of shop resources."""

from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Product, Review, Store


class ReviewSerializer(serializers.ModelSerializer):
    """Serialize product reviews without exposing buyer account details."""

    buyer = serializers.CharField(source="buyer.username", read_only=True)

    class Meta:
        model = Review
        fields = ["id", "buyer", "rating", "comment", "verified", "created_at"]


class ProductSerializer(serializers.ModelSerializer):
    """Serialize a product and its read-only reviews."""

    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "store", "name", "description", "price", "stock",
            "image", "reviews",
        ]
        read_only_fields = ["store"]


class StoreSerializer(serializers.ModelSerializer):
    """Serialize a store together with its active products."""

    owner = serializers.CharField(source="owner.username", read_only=True)
    products = serializers.SerializerMethodField()

    class Meta:
        model = Store
        fields = ["id", "owner", "name", "description", "logo", "products"]

    def get_products(self, store):
        products = store.products.filter(is_active=True)
        return ProductSerializer(products, many=True, context=self.context).data


class VendorSerializer(serializers.ModelSerializer):
    """Serialize a vendor and the vendor's active stores."""

    stores = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "stores"]

    def get_stores(self, vendor):
        stores = vendor.stores.filter(is_active=True)
        return StoreSerializer(stores, many=True, context=self.context).data
