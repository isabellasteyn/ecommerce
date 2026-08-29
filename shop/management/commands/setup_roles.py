from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    """Create the vendor and buyer groups used by the application."""

    help = "Create the Vendors and Buyers groups and assign permissions."

    def handle(self, *args, **kwargs):
        """Create groups and assign the shop permissions."""
        vendors, _ = Group.objects.get_or_create(name="Vendors")
        buyers, _ = Group.objects.get_or_create(name="Buyers")
        vendors.permissions.set(Permission.objects.filter(
            content_type__app_label="shop"))
        self.stdout.write(self.style.SUCCESS(
            "Vendors and Buyers groups created."))
