# Ecommerce Store — Django + SQL Server

## Phase 6 shopping cart

This project uses Django 5.2, Microsoft SQL Server (database `EcommerceDB` on `localhost`), and ODBC Driver 18. Product records and uploaded media remain in your local database and `media/` folder.

### Update an existing installation (recommended)

1. Back up `C:\EcommerceStore` and your SQL Server `EcommerceDB` database.
2. After merging the Phase 6 pull request on GitHub, open PowerShell in `C:\EcommerceStore`:
   ```powershell
   git status
   git pull origin main
   .\venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   python manage.py check
   python manage.py runserver
   ```
3. Open http://127.0.0.1:8000/ and click a product's **View Details**. Use **Add to Cart**, then **My Cart**.

**Important:** `git pull` may refuse if you have uncommitted local changes. Do not discard local changes or overwrite your working files; save a backup or ask for help resolving them.

### First-time installation

Create a Python 3.11 virtual environment, install `requirements.txt`, and configure SQL Server with Windows Authentication. SQL Server and ODBC Driver 18 must already be installed. Create the `EcommerceDB` database and run:

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit `/admin/` to create categories and products. Do not run `createsuperuser` again if you already have an account.

### What works

- Product catalog and product detail pages
- Guest/session or signed-in shopping carts
- Add, update, remove cart items
- Stock and quantity checks

Checkout and payment are **not implemented yet**.

### Security

The repository is configured for local development. Its original Django secret key was committed publicly. Rotate the key before any public deployment, move configuration secrets into environment variables, and disable `DEBUG` for production. Do not commit database backups, credentials, personal records, virtual environments, or uploaded customer files.
