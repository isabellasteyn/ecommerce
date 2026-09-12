"""Optional X API integration for announcing new stores and products."""

import logging

import tweepy
from django.conf import settings

logger = logging.getLogger(__name__)


def _credentials_available():
    """Return whether all four OAuth 1.0a credentials are configured."""
    return all([
        settings.X_API_KEY,
        settings.X_API_SECRET,
        settings.X_ACCESS_TOKEN,
        settings.X_ACCESS_TOKEN_SECRET,
    ])


def _post(text, image_field=None):
    """Create an X post, uploading an optional Django image first."""
    if not _credentials_available():
        logger.info("X posting skipped because credentials are not configured.")
        return None

    try:
        auth = tweepy.OAuth1UserHandler(
            settings.X_API_KEY,
            settings.X_API_SECRET,
            settings.X_ACCESS_TOKEN,
            settings.X_ACCESS_TOKEN_SECRET,
        )
        media_ids = None
        if image_field:
            api = tweepy.API(auth)
            with image_field.open("rb") as image:
                media = api.media_upload(
                    filename=image_field.name, file=image
                )
            media_ids = [media.media_id]

        client = tweepy.Client(
            consumer_key=settings.X_API_KEY,
            consumer_secret=settings.X_API_SECRET,
            access_token=settings.X_ACCESS_TOKEN,
            access_token_secret=settings.X_ACCESS_TOKEN_SECRET,
        )
        return client.create_tweet(text=text[:280], media_ids=media_ids)
    except Exception:
        # A social API outage must never prevent creation of shop data.
        logger.exception("Could not publish announcement to X.")
        return None


def post_store(store):
    """Announce a newly created store, including its logo when supplied."""
    text = f"New store: {store.name}\n\n{store.description}".strip()
    return _post(text, store.logo if store.logo else None)


def post_product(product):
    """Announce a newly created product, including its image when supplied."""
    text = (
        f"New product from {product.store.name}: {product.name}\n\n"
        f"{product.description}"
    ).strip()
    return _post(text, product.image if product.image else None)
