# admin.py
"""Admin registrations for the shop application."""


from django.contrib import admin
from .models import (
    Store,
    Product,
    Order,
    OrderItem,
    Review,
    PasswordResetToken,
)
admin.site.register([
    Store,
    Product,
    Order,
    OrderItem,
    Review,
    PasswordResetToken,
])
