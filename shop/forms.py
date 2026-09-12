# forms.py
"""Forms used by the shop application."""


from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from shop.models import Store, Product, Review


class RegisterForm(forms.Form):
    """Collect and validate the details required to register a user."""

    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput,
    )
    role = forms.ChoiceField(
        choices=[("buyer", "Buyer"), ("vendor", "Vendor")])

    def clean_email(self):
        """Prevent two accounts from using the same email address."""
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "This email address is already in use."
            )
        return email

    def clean(self):
        """Check that both passwords match and meet Django's rules."""
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirmation = cleaned_data.get("confirm_password")

        if password and confirmation and password != confirmation:
            self.add_error("confirm_password", "Passwords do not match.")
        elif password:
            validate_password(password)

        return cleaned_data


class StoreForm(forms.ModelForm):
    """Form used by vendors to create and edit stores."""

    class Meta:
        """Configure the Store model fields shown in the form."""
        model = Store
        fields = ["name", "description", "logo"]


class ProductForm(forms.ModelForm):
    """Form used by vendors to create and edit products."""

    class Meta:
        """Configure the Product model fields shown in the form."""
        model = Product
        fields = ["name", "description", "price", "stock", "image"]


class ReviewForm(forms.ModelForm):
    """Form used by buyers to leave a product review."""

    class Meta:
        """Configure the Review model fields shown in the form."""
        model = Review
        fields = ["rating", "comment"]
        labels = {
            "rating": "Rating (1 to 5)",
        }
        widgets = {
            "rating": forms.NumberInput(attrs={"min": 1, "max": 5}),
        }

    def clean_rating(self):
        """Ensure that the rating is between one and five."""
        value = self.cleaned_data["rating"]
        if not 1 <= value <= 5:
            raise forms.ValidationError("Rating must be 1-5.")
        return value
