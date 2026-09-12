from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("shop", "0003_store_is_active")]

    operations = [
        migrations.AddField(
            model_name="store",
            name="logo",
            field=models.ImageField(
                blank=True, null=True, upload_to="store_logos/"
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="image",
            field=models.ImageField(
                blank=True, null=True, upload_to="product_images/"
            ),
        ),
    ]
