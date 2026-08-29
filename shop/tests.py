"""Tests for the main registration and shopping improvements."""


from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from .forms import RegisterForm
from .models import Product, Store


class RegistrationTests(TestCase):
    """Test registration validation."""

    def test_passwords_must_match(self):
        """Reject a form when password confirmation is different."""
        form = RegisterForm({
            "username": "buyer",
            "email": "buyer@example.com",
            "password": "A-strong-password-123",
            "confirm_password": "different",
            "role": "buyer",
        })
        self.assertFalse(form.is_valid())

    def test_email_must_be_unique(self):
        """Reject an email already used by another account."""
        User.objects.create_user("first", "same@example.com", "password")
        form = RegisterForm({
            "username": "second",
            "email": "SAME@example.com",
            "password": "A-strong-password-123",
            "confirm_password": "A-strong-password-123",
            "role": "buyer",
        })
        self.assertFalse(form.is_valid())


class CartTests(TestCase):
    """Test buyer cart quantity management."""

    def setUp(self):
        """Create a buyer and a product for each cart test."""
        buyers = Group.objects.create(name="Buyers")
        vendor = User.objects.create_user("vendor", password="password")
        self.buyer = User.objects.create_user("buyer", password="password")
        self.buyer.groups.add(buyers)
        store = Store.objects.create(owner=vendor, name="Test Store")
        self.product = Product.objects.create(
            store=store,
            name="Test Product",
            price="10.00",
            stock=5,
        )
        self.client.login(username="buyer", password="password")

    def test_add_selected_quantity(self):
        """Add the quantity supplied by the buyer to the session cart."""
        self.client.post(
            reverse("cart_add", args=[self.product.pk]),
            {"quantity": 3},
        )
        self.assertEqual(
            self.client.session["cart"][str(self.product.pk)],
            3,
        )

    def test_cannot_add_more_than_stock(self):
        """Do not add a quantity greater than available stock."""
        self.client.post(
            reverse("cart_add", args=[self.product.pk]),
            {"quantity": 6},
        )
        self.assertNotIn(str(self.product.pk),
                         self.client.session.get("cart", {}))

    def test_remove_cart_item(self):
        """Remove a selected product from the cart."""
        session = self.client.session
        session["cart"] = {str(self.product.pk): 2}
        session.save()
        self.client.post(reverse("cart_remove", args=[self.product.pk]))
        self.assertNotIn(str(self.product.pk), self.client.session["cart"])

    def test_checkout_reduces_stock(self):
        """Reduce product stock after a successful checkout."""
        session = self.client.session
        session["cart"] = {str(self.product.pk): 2}
        session.save()
        self.client.post(reverse("checkout"))
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)
