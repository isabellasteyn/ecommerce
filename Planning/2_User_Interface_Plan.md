# 2. User Interface Plan

## General layout

Every page uses the same simple header and navigation. The main page lists products with their store, price, and stock. Forms display labels, validation messages, and clear action buttons.

## Guest pages

- Product list and product detail pages.
- Registration page with username, unique email, password, password confirmation, and role.
- Login and forgot password pages.

## Vendor pages

- Navigation shows Products, My stores, and Logout.
- My stores lists each store and its products with create, edit, and delete actions.
- The buyer Cart link is hidden.

## Buyer pages

- Navigation shows Products, Cart, and Logout.
- Product detail has an editable quantity field limited by current stock.
- Cart displays product, editable quantity, subtotal, Update, and Remove.
- Cart also provides Continue shopping, Checkout, and Cancel order / Clear cart.

## User experience choices

Only role authorised actions are displayed. Destructive actions use confirmation or POST forms. Error and success messages explain invalid quantities, stock shortages, login problems, and password-reset results.
