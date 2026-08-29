# 4. Failure and Recovery Plan

| Possible failure | Application response or recovery |
| --- | --- |
| Invalid login | Keep the user logged out and show an error. |
| Duplicate username or email | Reject registration and show the affected form error. |
| Passwords do not match | Reject the form and ask the user to correct the confirmation. |
| User opens an unauthorised page | Django redirects to login or denies the role check. |
| Invalid or excessive cart quantity | Keep the previous cart value and show the available stock. |
| Product is removed before checkout | Stop checkout and return the buyer to the cart. |
| Stock changes before checkout | Lock and recheck products; do not create a partial order. |
| Database error during checkout | The transaction rolls back the order and stock changes. |
| Expired or reused reset link | Reject the link and direct the user to request a new one. |
| Email delivery problem | During development, emails are printed to the console for testing. In production, email errors should be logged and retried. |

Database backups and secure environment configuration should be used in production. Errors should be logged without exposing passwords, secret keys, or database credentials.
