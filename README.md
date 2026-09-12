# Django eCommerce Application - Practical Task 1

A user registers as either a vendor or a buyer. Vendors manage their own stores and products. Buyers browse products, manage a session-based cart, check out, and leave verified or unverified reviews.

## Main features

- User registration, login, logout, and password reset
- Separate vendor and buyer roles
- Store and product CRUD for vendors
- Session-based cart CRUD for buyers
- Stock validation when adding, updating, and checking out
- Order creation, stock reduction, and console invoice email
- Verified reviews when the buyer previously purchased the product

## Requirements

- Python 3.11 or newer
- MySQL installed and running
- Git

## Installation

1. Clone the repository and enter the project folder. Replace the example URL with your own repository URL.

```bash
git clone https://github.com/isabellasteyn/ecommerce.git
cd ecommerce
```

2. Create and activate a virtual environment inside the project folder.

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install the packages from the requirements file.

```bash
python -m pip install -r requirements.txt
```

4. Start the MariaDB server if it's not already running.

```bash
brew services start mariadb
```

5. Open MySQL as the root user.

```bash
mariadb -u root -p
```

6. Create the database and a project database user. Change `your_password` to a password of your choice.

```sql
CREATE DATABASE ecommerce_db CHARACTER SET utf8mb4;
CREATE USER 'ecommerce_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON ecommerce_db.* TO 'ecommerce_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

7. Copy the environment template file and replace with your own environment variables.

```bash
cp .env.example .env
```

8. Generate a Django secret key.

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Open `.env`, paste the generated value after `SECRET_KEY=`, and update `DB_PASSWORD` to the MySQL password created above.

9. Create the database tables.

```bash
python manage.py migrate
```

10. Create the vendor and buyer roles before starting the application.

```bash
python manage.py setup_roles
```

11. Create an administrator account.

```bash
python manage.py createsuperuser
```

12. Start the development server.

```bash
python manage.py runserver
```

Open <http://127.0.0.1:8000/> in a browser. Administrator access is available at <http://127.0.0.1:8000/admin/>.

The project uses Django's console email backend by default. Checkout invoices and password-reset links are printed in the terminal instead of being sent to a real email address.

## REST API

Create a token by sending a username and password to the token endpoint:

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -d "username=vendor" -d "password=your-password"
```

Use the returned token on protected requests:

```bash
curl http://127.0.0.1:8000/api/stores/ \
  -H "Authorization: Token YOUR_TOKEN"
```

Vendors can create stores and add products to their own stores. Buyers and
vendors can retrieve vendors, active stores, active products, and reviews. See
`Planning/5_API_Plan.md` for the endpoint table and sequence diagram.

## X integration

Create an X developer project/app with read-and-write permissions, then place
its OAuth 1.0a credentials in `.env`:

```text
X_API_KEY=...
X_API_SECRET=...
X_ACCESS_TOKEN=...
X_ACCESS_TOKEN_SECRET=...
```

When all credentials are set, store and product creation through either the web
forms or API publishes an announcement. Logos and product images are uploaded
when present. With blank credentials, posting is disabled without interrupting
normal eCommerce functionality.

## Tests

To run project tests, use:

```bash
python manage.py check
python manage.py test
```

To test using SQLite instead of MySQL, run:

```bash
USE_SQLITE=True python manage.py test
```

## Planning documents

The `Planning` folder contains the documentation and diagrams for the project.
