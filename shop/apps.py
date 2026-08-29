# apps.py
"""Configuration for the shop application."""


from django.apps import AppConfig


class ShopConfig(AppConfig):
    """Configure the shop Django application."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "shop"
