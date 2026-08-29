# context_processors.py
"""Custom template context processors for user roles."""


def user_roles(request):
    """Add the current user's vendor and buyer roles to templates."""
    is_vendor = (
        request.user.is_authenticated and request.user.groups.filter(
            name="Vendors"
        ).exists()
    )

    return {
        "is_vendor": is_vendor,
        "is_buyer": (
            request.user.is_authenticated and request.user.groups.filter(
                name="Buyers"
            ).exists()
        ),
    }
