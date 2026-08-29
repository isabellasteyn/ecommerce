from django.urls import path
from . import views
urlpatterns = [
    path("", views.product_list, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("stores/", views.store_list, name="store_list"),
    path("stores/new/", views.store_create, name="store_create"),
    path("stores/<int:pk>/edit/", views.store_edit, name="store_edit"),
    path("stores/<int:pk>/delete/", views.store_delete, name="store_delete"),
    path("products/new/", views.product_create, name="product_create"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
    path("products/<int:pk>/edit/", views.product_edit, name="product_edit"),
    path("products/<int:pk>/delete/",
         views.product_delete,
         name="product_delete"
         ),
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:pk>/", views.cart_add, name="cart_add"),
    path("cart/update/<int:pk>/", views.cart_update, name="cart_update"),
    path("cart/remove/<int:pk>/", views.cart_remove, name="cart_remove"),
    path("cart/clear/", views.cart_clear, name="cart_clear"),
    path("checkout/", views.checkout, name="checkout"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("reset-password/<str:token>/",
         views.reset_password,
         name="reset_password"
         ),
]
