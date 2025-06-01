# CyberPanel Reseller Panel

## Description
A Django-based web application designed to enable users to manage and resell shared hosting accounts by interacting with the CyberPanel API. This panel provides a user-friendly interface for customers to order hosting plans and manage their services, and an admin interface for administrators to manage plans and customer accounts.

## Features Implemented
*   **User Authentication:** Customer registration, login, logout, and password change capabilities.
*   **Hosting Plan Management (Admin):** Administrators can define hosting plans (e.g., Basic, Pro) with specific resource allocations (disk space, bandwidth, etc.) and pricing. Each plan in the panel is linked to a corresponding package name in CyberPanel.
*   **Customer Hosting Order System:**
    *   Authenticated customers can browse available hosting plans.
    *   Customers can order a selected plan by providing a domain name.
    *   The system generates a unique username and secure password for the new CyberPanel account.
    *   On order, the application (simulates) calls the CyberPanel API to create the new website/hosting account.
*   **Customer Service Dashboard:**
    *   Customers can view a list of their ordered services.
    *   Details provided include domain name, hosting plan, CyberPanel username, service status, and creation date.
    *   Essential connection information such as FTP hostname and nameservers (configurable in Django settings) are displayed.
*   **Admin Service Management:**
    *   Administrators can view and manage customer services.
    *   Admin actions are available to (simulate) suspend, unsuspend, or delete customer websites via the CyberPanel API. The local service status (`is_active`) is updated accordingly.
*   **User Interface:** The application uses the Bootstrap 5 framework for a responsive and modern UI.
*   **Unit Tests:** A suite of unit tests is provided for models, forms, views, and the CyberPanel API interaction layer (using mocks).

## Setup Instructions (Development)

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd cyberpanel_reseller_project
    ```

2.  **Create and Activate Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Settings (`cyberpanel_reseller/settings.py`):**
    *   **`SECRET_KEY`**: Ensure this is set. Django's `startproject` generates one. For production, use a strong, unique key.
    *   **CyberPanel API Details (Crucial):**
        *   `CYBERPANEL_API_URL`: Your CyberPanel server's API URL (e.g., `https://your_server_ip:8090/api/`).
        *   `CYBERPANEL_ADMIN_USERNAME`: Your CyberPanel admin username.
        *   `CYBERPANEL_ADMIN_PASSWORD`: Your CyberPanel admin password.
    *   **Customer-Facing Information:**
        *   `PRIMARY_NAMESERVER`: E.g., `ns1.yourdomain.com`.
        *   `SECONDARY_NAMESERVER`: E.g., `ns2.yourdomain.com`.
        *   `CYBERPANEL_HOSTNAME`: The hostname or IP address customers should use for FTP/SFTP (usually your CyberPanel server's main IP or hostname).
    *   **Security Note:** For production, it is strongly recommended to use environment variables for all sensitive settings (SECRET_KEY, API credentials, database passwords) rather than hardcoding them in `settings.py`.

5.  **Database Migrations:**
    *   The project is configured for SQLite by default. If you continue with SQLite, ensure the directory is writable.
    *   Run migrations to set up the database schema:
        ```bash
        python manage.py makemigrations panel
        python manage.py migrate
        ```
        *(Note: Previous subtasks in this session encountered timeouts with migration commands in the automated environment. These may need to be run manually if issues persist.)*

6.  **Create Superuser (Admin Account):**
    *   This account is used to access the Django admin interface (`/admin/`).
        ```bash
        python manage.py createsuperuser
        ```
        *(Follow the prompts to set username, email, and password. Previous subtasks also noted timeouts with this command in the automated environment.)*

7.  **Run Development Server:**
    ```bash
    python manage.py runserver
    ```

8.  **Access the Panel:**
    *   **Main Panel:** `http://127.0.0.1:8000/panel/` (e.g., for plan listing, login, etc.)
    *   **Admin Interface:** `http://127.0.0.1:8000/admin/`

## CyberPanel Pre-requisites

*   **CyberPanel Installation:** You must have a working CyberPanel installation on a server.
*   **API Accessibility:** Ensure the CyberPanel API is enabled and accessible from where you are running this Django application.
*   **Hosting Packages in CyberPanel:** Before users can order plans, you need to create corresponding "packages" within your CyberPanel admin interface. The `cyberpanel_package_name` field in the Django `HostingPlan` model must exactly match the name of a package you've created in CyberPanel (e.g., "Default", "StarterPlan", "ProPlan").

## Running Tests
To run the unit tests for the `panel` app:
```bash
python manage.py test panel
```
*(Note: Test execution also timed out in previous automated subtasks.)*

## Production Considerations (Brief Overview)

*   **Secrets Management:** Use environment variables or a vault service (e.g., HashiCorp Vault, AWS Secrets Manager) for `SECRET_KEY`, `CYBERPANEL_ADMIN_PASSWORD`, database credentials, and other sensitive data. Do NOT hardcode these in `settings.py` for a production deployment.
*   **`DEBUG = False`**: Set `DEBUG = False` in `settings.py` for production to avoid exposing sensitive debug information.
*   **`ALLOWED_HOSTS`**: Configure `ALLOWED_HOSTS` in `settings.py` with the domain(s) that will serve your application.
*   **Web Server:** Use a production-grade WSGI server like Gunicorn or uWSGI.
*   **Reverse Proxy:** Place a reverse proxy like Nginx or Apache in front of the WSGI server to handle tasks like serving static files, SSL termination, and load balancing.
*   **Static Files:** Run `python manage.py collectstatic` and configure your web server to serve files from the `STATIC_ROOT` directory.
*   **Database:** Consider using a more robust database like PostgreSQL or MySQL for production instead of SQLite.
*   **HTTPS:** Ensure your site is served over HTTPS.
*   **Error Reporting:** Set up error reporting tools (e.g., Sentry).
*   **Backups:** Implement regular backups of your database and application code/media.

---
This README provides a basic guide. Further customization and security hardening are essential for a production environment.
