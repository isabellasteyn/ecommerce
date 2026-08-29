# 1. System Requirements

## Purpose

The application allows vendors to sell products and buyers to browse and purchase them.

## Users and requirements

### Guest

- View products and product details.
- Register as a buyer or vendor.
- Log in and request a password reset.

### Vendor

- Log in and log out.
- Create, view, update, and delete only their own stores.
- Create, view, update, and delete products in their own stores.
- Set a product price and available stock.
- Vendors cannot access the buyer cart or checkout functions.

### Buyer

- Log in and log out.
- View products from different stores.
- Add a selected quantity to a session-based cart.
- View, update, remove, or clear cart items.
- Continue shopping before checkout.
- Checkout only when enough stock is available.
- Receive an invoice by email after checkout.
- Leave verified reviews for purchased products and unverified reviews for other products.

## Main data

The system stores users, groups, stores, products, orders, order items, reviews, and password-reset tokens. The cart remains in the buyer's Django session until it is cleared or checkout succeeds.
