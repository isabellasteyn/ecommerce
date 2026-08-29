from decimal import Decimal
import secrets
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import RegisterForm, StoreForm, ProductForm, ReviewForm
from shop.models import Store, Product, Order, OrderItem, PasswordResetToken


def is_vendor(u):
    """Return whether a user belongs to the Vendors group."""
    return u.is_authenticated and u.groups.filter(name="Vendors").exists()


def is_buyer(u):
    """Return whether a user belongs to the Buyers group."""
    return u.is_authenticated and u.groups.filter(name="Buyers").exists()


def product_list(request):
    """Display all active products from all active stores."""
    products = Product.objects.select_related("store").filter(
        is_active=True,
        store__is_active=True,
    )

    return render(
        request,
        "shop/product_list.html",
        {"products": products},
    )


def register(request):
    """Register a buyer or vendor after validating their details."""
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if User.objects.filter(
            username=form.cleaned_data["username"]
        ).exists():
            form.add_error("username", "Username already exists.")
        else:
            user = User.objects.create_user(
                form.cleaned_data["username"],
                form.cleaned_data["email"],
                form.cleaned_data["password"]
            )
            role_name = (
                "Vendors"
                if form.cleaned_data["role"] == "vendor"
                else "Buyers"
            )
            group = Group.objects.get_or_create(name=role_name)[0]
            user.groups.add(group)
            login(request, user)
            return redirect("home")
    return render(
        request,
        "shop/form.html",
        {"form": form, "title": "Register"}
    )


def login_view(request):
    """Authenticate a user and start their session."""
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )
        if user:
            login(request, user)
            return redirect("home")
        messages.error(request, "Invalid username or password.")
    return render(request, "shop/login.html")


def logout_view(request):
    """End the current user's session."""
    logout(request)
    return redirect("home")


@login_required
@user_passes_test(is_vendor)
def store_list(request):
    """Display the active stores belonging to the logged-in vendor."""
    stores = request.user.stores.filter(is_active=True)
    return render(
        request,
        "shop/stores.html",
        {"stores": stores}
    )


@login_required
@user_passes_test(is_vendor)
def store_create(request):
    """Create a store owned by the logged-in vendor."""
    form = StoreForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        store = form.save(commit=False)
        store.owner = request.user
        store.save()
        return redirect("store_list")
    return render(
        request,
        "shop/form.html",
        {
            "form": form,
            "title": "Create store",
            "cancel_url": "store_list",
        }
    )


def owned_store(request, pk):
    """Retrieve an active store only when it belongs to the current user."""
    return get_object_or_404(
        Store,
        pk=pk,
        owner=request.user,
        is_active=True,
    )


@login_required
@user_passes_test(is_vendor)
def store_edit(request, pk):
    """Edit one of the logged-in vendor's stores."""
    store = owned_store(request, pk)
    form = StoreForm(request.POST or None, instance=store)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("store_list")
    return render(
        request,
        "shop/form.html",
        {
            "form": form,
            "title": "Edit store",
            "cancel_url": "store_list",
        }
    )


@login_required
@user_passes_test(is_vendor)
def store_delete(request, pk):
    """Delete one of the logged-in vendor's stores after confirmation."""
    store = owned_store(request, pk)
    if request.method == "POST":
        store.is_active = False
        store.save()

        Product.objects.filter(store=store).update(is_active=False)

        messages.success(
            request,
            "Store removed successfully.",
        )
        return redirect("store_list")
    return render(
        request,
        "shop/confirm.html",
        {
            "object": store,
            "cancel_url": "store_list"
        },
    )


@login_required
@user_passes_test(is_vendor)
def product_create(request):
    """Create a product in one of the logged-in vendor's active stores."""
    stores = request.user.stores.filter(is_active=True)
    if not stores:
        messages.error(request, "Create a store first.")
        return redirect("store_create")
    form = ProductForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        store_id = request.POST.get("store")
        store = get_object_or_404(Store, pk=store_id, owner=request.user)
        product = form.save(commit=False)
        product.store = store
        product.save()
        return redirect("store_list")
    return render(
        request,
        "shop/product_form.html",
        {
            "form": form,
            "stores": stores,
            "title": "Add product",
            "cancel_url": "store_list"
        }
    )


def owned_product(request, pk):
    """Retrieve a product only when its store belongs to the user."""
    return get_object_or_404(
        Product,
        pk=pk,
        is_active=True,
        store__is_active=True,
        store__owner=request.user
    )


@login_required
@user_passes_test(is_vendor)
def product_edit(request, pk):
    """Edit a product owned by the logged-in vendor."""
    product = owned_product(request, pk)
    form = ProductForm(request.POST or None, instance=product)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("store_list")
    return render(
        request,
        "shop/form.html",
        {
            "form": form,
            "title": "Edit product",
            "cancel_url": "store_list"
        }
    )


@login_required
@user_passes_test(is_vendor)
def product_delete(request, pk):
    """Remove a product from sale while preserving order history."""
    product = owned_product(request, pk)
    if request.method == "POST":
        if request.method == "POST":
            product.is_active = False
            product.save()

            messages.success(
                request,
                "Product removed successfully.",
            )
            return redirect("store_list")
    return render(
        request,
        "shop/confirm.html", {
            "object": product,
            "cancel_url": "store_list"
        }
    )


def product_detail(request, pk):
    """Display an active product and allow buyers to leave reviews."""
    product = get_object_or_404(
        Product,
        pk=pk,
        is_active=True,
        store__is_active=True,
    )
    form = ReviewForm(request.POST or None)
    if request.method == "POST":
        if not is_buyer(request.user):
            return HttpResponseForbidden("Only buyers may review products.")
        if form.is_valid():
            verified = OrderItem.objects.filter(
                order__buyer=request.user, product=product).exists()
            review = form.save(commit=False)
            review.product = product
            review.buyer = request.user
            review.verified = verified
            review.save()
            return redirect("product_detail", pk=pk)
    return render(
        request,
        "shop/product_detail.html",
        {"product": product, "form": form}
    )


@login_required
@user_passes_test(is_buyer)
def cart_add(request, pk):
    """Add the requested quantity without exceeding available stock."""
    if request.method == "POST":
        product = get_object_or_404(
            Product,
            pk=pk,
            is_active=True,
            store__is_active=True,
        )
        try:
            quantity = int(request.POST.get("quantity", 1))
        except (TypeError, ValueError):
            quantity = 0

        if quantity < 1:
            messages.error(request, "Quantity must be at least 1.")
            return redirect("product_detail", pk=pk)

        cart = request.session.get("cart", {})
        key = str(pk)
        new_quantity = cart.get(key, 0) + quantity

        if new_quantity > product.stock:
            messages.error(
                request,
                f"Only {product.stock} item(s) of "
                f"{product.name} are available.",
            )
            return redirect("product_detail", pk=pk)

        cart[key] = new_quantity
        request.session["cart"] = cart
        request.session.modified = True
    return redirect("cart")


@login_required
@user_passes_test(is_buyer)
def cart_view(request):
    """Display the products currently saved in the buyer's cart."""
    cart = request.session.get("cart", {})
    rows = []
    total = Decimal("0")
    for key, qty in cart.items():
        try:
            p = Product.objects.get(
                pk=int(key),
                is_active=True,
            )
            subtotal = p.price * qty
            total += subtotal
            rows.append((p, qty, subtotal))
        except Product.DoesNotExist:
            pass
    return render(request, "shop/cart.html", {"rows": rows, "total": total})


@login_required
@user_passes_test(is_buyer)
def cart_update(request, pk):
    """Update a cart item's quantity without exceeding its stock."""
    if request.method == "POST":
        product = get_object_or_404(
            Product,
            pk=pk,
            is_active=True,
            store__is_active=True,
        )
        try:
            quantity = int(request.POST.get("quantity", 1))
        except (TypeError, ValueError):
            quantity = 0

        if quantity < 1:
            messages.error(request, "Quantity must be at least 1.")
        elif quantity > product.stock:
            messages.error(
                request,
                f"Only {product.stock} item(s) of {product.name} are "
                f"available.",
            )
        else:
            cart = request.session.get("cart", {})
            cart[str(pk)] = quantity
            request.session["cart"] = cart
            request.session.modified = True

    return redirect("cart")


@login_required
@user_passes_test(is_buyer)
def cart_remove(request, pk):
    """Remove one product from the buyer's cart."""
    if request.method == "POST":
        cart = request.session.get("cart", {})
        cart.pop(str(pk), None)
        request.session["cart"] = cart
        request.session.modified = True
    return redirect("cart")


@login_required
@user_passes_test(is_buyer)
def cart_clear(request):
    """Remove every product from the buyer's cart."""
    if request.method == "POST":
        request.session["cart"] = {}
        request.session.modified = True
    return redirect("cart")


@login_required
@user_passes_test(is_buyer)
@transaction.atomic
def checkout(request):
    """Create an order, reduce stock, email an invoice, and clear the cart."""
    if request.method != "POST":
        return redirect("cart")

    cart = request.session.get("cart", {})

    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect("cart")

    products = {}

    # Validate every product before creating the order.
    for key, qty in cart.items():
        try:
            product = Product.objects.select_for_update().get(
                pk=int(key),
                is_active=True,
                store__is_active=True,
            )
        except Product.DoesNotExist:
            messages.error(
                request,
                "A product in your cart is no longer available."
            )
            return redirect("cart")

        if product.stock < qty:
            messages.error(
                request,
                f"Sorry, there is insufficient stock for "
                f"{product.name}. Only {product.stock} item(s) "
                f"are available."
            )
            return redirect("cart")

        products[int(key)] = product

    # All products have enough stock, so create the order.
    order = Order.objects.create(
        buyer=request.user
    )

    total = Decimal("0")
    lines = []

    for key, qty in cart.items():
        product = products[int(key)]

        product.stock -= qty
        product.save()

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=qty,
            unit_price=product.price,
        )

        subtotal = product.price * qty
        total += subtotal

        lines.append(
            f"{product.name} x{qty} = R{subtotal}"
        )

    order.total = total
    order.save()

    # Clear the cart only after the order succeeds.
    request.session["cart"] = {}
    request.session.modified = True

    invoice_lines = "\n".join(lines)
    message = (
        f"Thank you for your purchase.\n\n"
        f"{invoice_lines}"
        f"\n\nTotal: R{total}"
    )

    send_mail(
        f"Invoice {order.invoice_number}",
        message,
        None,
        [request.user.email],
    )

    return render(
        request,
        "shop/checkout_success.html",
        {
            "order": order,
        },
    )


def forgot_password(request):
    """Email a temporary password reset link when an account exists."""
    if request.method == "POST":
        user = User.objects.filter(email=request.POST.get("email")).first()
        if user:
            token = secrets.token_urlsafe(32)
            PasswordResetToken.objects.create(
                user=user,
                token=token,
                expires_at=timezone.now() + timedelta(minutes=30)
            )
            url = request.build_absolute_uri(f"/reset-password/{token}/")
            send_mail(
                "Password reset",
                f"Use this link within 30 minutes:\n{url}",
                None,
                [user.email]
            )
        messages.success(
            request,
            "If the email exists, a reset link has been sent."
        )
        return redirect("login")
    return render(request, "shop/forgot_password.html")


def reset_password(request, token):
    """Validate a reset token and save the user's new password."""
    record = get_object_or_404(PasswordResetToken, token=token)
    if not record.valid():
        messages.error(request, "This reset link has expired or was used.")
        return redirect("forgot_password")
    if request.method == "POST":
        password = request.POST.get("password")
        confirm = request.POST.get("confirm")
        if password != confirm:
            messages.error(request, "Passwords do not match.")
        else:
            try:
                validate_password(password, record.user)
            except Exception as e:
                messages.error(request, str(e))
            else:
                record.user.set_password(password)
                record.user.save()
                record.used = True
                record.save()
                return redirect("login")
    return render(request, "shop/reset_password.html")
