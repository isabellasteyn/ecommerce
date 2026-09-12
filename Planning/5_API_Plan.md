# REST API plan

## Representation

The API uses JSON by default and also accepts multipart form data for optional
store logos and product images. Nested read representations make it possible to
retrieve each vendor's stores and each store's products. Reviews expose the
buyer's username, rating, comment, verified status, and date.

## Endpoints

| Method | Endpoint                              | Access          | Purpose                                          |
| ------ | ------------------------------------- | --------------- | ------------------------------------------------ |
| POST   | `/api/token/`                         | Registered user | Exchange username/password for a token           |
| GET    | `/api/vendors/`                       | Buyer or vendor | Retrieve vendors, stores, and products           |
| GET    | `/api/stores/`                        | Buyer or vendor | Retrieve all active stores and products          |
| POST   | `/api/stores/`                        | Vendor          | Create a store owned by the authenticated vendor |
| GET    | `/api/stores/<store_id>/products/`    | Buyer or vendor | Retrieve active products in a store              |
| POST   | `/api/stores/<store_id>/products/`    | Store owner     | Add a product to the vendor's own store          |
| GET    | `/api/products/<product_id>/reviews/` | Buyer or vendor | Retrieve a product's reviews                     |

Every request except token acquisition requires either the header
`Authorization: Token <token>` or an authenticated Django session. Buyers have read-only access. A vendor cannot add a product to another vendor's store.

The X call fails safely: missing credentials or an X outage is logged, while the successfully created store or product remains available.
