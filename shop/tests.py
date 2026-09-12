"""Tests for the main registration and shopping improvements."""


import shutil
import tempfile

from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings, TestCase
from django.urls import reverse

from .forms import RegisterForm
from .models import Product, Store
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


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


class ShopAPITests(TestCase):
    """Test API authentication, retrieval, and vendor ownership rules."""

    def setUp(self):
        vendors = Group.objects.create(name="Vendors")
        buyers = Group.objects.create(name="Buyers")
        self.vendor = User.objects.create_user(
            "vendor_api", password="password")
        self.other_vendor = User.objects.create_user(
            "other_vendor", password="password"
        )
        self.buyer = User.objects.create_user("buyer_api", password="password")
        self.vendor.groups.add(vendors)
        self.other_vendor.groups.add(vendors)
        self.buyer.groups.add(buyers)
        self.store = Store.objects.create(owner=self.vendor, name="API Store")
        self.client = APIClient()

    def authenticate(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_unauthenticated_user_cannot_list_stores(self):
        response = self.client.get(reverse("api_stores"))
        self.assertEqual(response.status_code, 401)

    def test_buyer_can_retrieve_stores_but_cannot_create_one(self):
        self.authenticate(self.buyer)
        self.assertEqual(self.client.get(
            reverse("api_stores")).status_code, 200)
        response = self.client.post(reverse("api_stores"), {"name": "Nope"})
        self.assertEqual(response.status_code, 403)

    def test_vendor_can_create_own_store(self):
        self.authenticate(self.vendor)
        response = self.client.post(
            reverse("api_stores"),
            {"name": "New API Store", "description": "Created over REST"},
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Store.objects.get(
            name="New API Store").owner, self.vendor)

    def test_vendor_can_add_product_to_own_store(self):
        self.authenticate(self.vendor)
        response = self.client.post(
            reverse("api_store_products", args=[self.store.pk]),
            {"name": "API Product", "price": "25.00", "stock": 4},
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Product.objects.filter(
                name="API Product", store=self.store).exists()
        )

    def test_vendor_cannot_add_product_to_another_vendor_store(self):
        self.authenticate(self.other_vendor)
        response = self.client.post(
            reverse("api_store_products", args=[self.store.pk]),
            {"name": "Forbidden Product", "price": "25.00", "stock": 4},
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Product.objects.filter(
            name="Forbidden Product").exists())


class ImageUploadTests(TestCase):
    """Test uploading, displaying, and removing shop images."""

    @classmethod
    def setUpClass(cls):
        """Create a temporary media directory for image tests."""
        super().setUpClass()
        cls.media_root = tempfile.mkdtemp()
        cls.media_override = override_settings(
            MEDIA_ROOT=cls.media_root,
        )
        cls.media_override.enable()

    @classmethod
    def tearDownClass(cls):
        """Remove the temporary media directory after the tests."""
        cls.media_override.disable()
        shutil.rmtree(cls.media_root)
        super().tearDownClass()

    def setUp(self):
        """Create a vendor, store, and product for each test."""
        vendors = Group.objects.create(name="Vendors")
        self.vendor = User.objects.create_user(
            username="image_vendor",
            password="password",
        )
        self.vendor.groups.add(vendors)
        self.store = Store.objects.create(
            owner=self.vendor,
            name="Image Store",
            description="A store used for image tests.",
        )
        self.product = Product.objects.create(
            store=self.store,
            name="Image Product",
            description="A product used for image tests.",
            price="10.00",
            stock=2,
        )
        self.client.login(
            username="image_vendor",
            password="password",
        )

    @staticmethod
    def image_file(name):
        """Return a valid one-pixel GIF uploaded entirely from memory."""
        content = (
            b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,"
            b"\x00\x00\x00\x00\x01\x00\x01\x00\x00"
            b"\x02\x02D\x01\x00;"
        )
        return SimpleUploadedFile(
            name=name,
            content=content,
            content_type="image/gif",
        )

    def test_store_logo_upload_display_and_delete(self):
        """Upload, display, and remove a store logo."""
        response = self.client.post(
            reverse("store_edit", args=[self.store.pk]),
            {
                "name": self.store.name,
                "description": self.store.description,
                "logo": self.image_file("logo.gif"),
            },
        )
        self.assertRedirects(
            response,
            reverse("store_detail", args=[self.store.pk]),
        )
        self.store.refresh_from_db()
        self.assertTrue(
            self.store.logo.name.endswith("logo.gif"),
        )
        detail_response = self.client.get(
            reverse("store_detail", args=[self.store.pk]),
        )
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(
            detail_response,
            self.store.logo.url,
        )
        delete_response = self.client.post(
            reverse("store_logo_delete", args=[self.store.pk]),
        )
        self.assertRedirects(
            delete_response,
            reverse("store_detail", args=[self.store.pk]),
        )
        self.store.refresh_from_db()
        self.assertFalse(self.store.logo)

    def test_product_image_upload_display_and_delete(self):
        """Upload, display, and remove a product image."""
        response = self.client.post(
            reverse("product_edit", args=[self.product.pk]),
            {
                "name": self.product.name,
                "description": self.product.description,
                "price": "10.00",
                "stock": 2,
                "image": self.image_file("product.gif"),
            },
        )
        self.assertRedirects(
            response,
            reverse("product_detail", args=[self.product.pk]),
        )
        self.product.refresh_from_db()
        self.assertTrue(
            self.product.image.name.endswith("product.gif"),
        )
        detail_response = self.client.get(
            reverse("product_detail", args=[self.product.pk]),
        )
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(
            detail_response,
            self.product.image.url,
        )
        delete_response = self.client.post(
            reverse(
                "product_image_delete",
                args=[self.product.pk],
            ),
        )
        self.assertRedirects(
            delete_response,
            reverse("product_detail", args=[self.product.pk]),
        )
        self.product.refresh_from_db()
        self.assertFalse(self.product.image)
