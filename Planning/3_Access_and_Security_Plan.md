# 3. Access Control and Data Security Plan

## Authentication and roles

Django authentication stores hashed passwords and manages user sessions. New users join either the Buyers or Vendors group. The `setup_roles` command creates these groups before the server is used.

Vendor views use login and role checks. Database queries also restrict stores and products to the logged-in owner. Buyer cart, checkout, and review actions require the buyer role. Navigation hides actions that do not belong to the user's role.

## Input and account security

- Registration requires matching passwords and uses Django password validation.
- Email addresses are checked case-insensitively to prevent duplicates.
- Django forms validate model input.
- Password-reset tokens expire, can only be used once, and do not reveal whether an email exists.
- Secrets and database credentials are stored in `.env`, which is excluded from Git.

## Purchase security

The cart accepts positive whole-number quantities only. Quantity is checked against stock when a product is added or updated. Checkout checks stock again inside a database transaction and locks product rows. Stock is reduced only when the entire order can be completed.
