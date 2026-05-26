# Medical Reports System - PostgreSQL Setup

## Database Setup Instructions

### Step 1: Create the Database Schema

Run the following command in your terminal (make sure PostgreSQL is running):

```bash
psql -U postgres -d postgres -f schema.sql
```

Or connect to PostgreSQL and run the schema manually:

```bash
psql -U postgres
```

Then paste the contents of `schema.sql`.

### Step 2: Configure Database Connection

1. Copy `.env.example` to `.env` (if using environment variables)
2. Edit `config.php` and update the database credentials:
   - `DB_HOST`: Your PostgreSQL host (default: localhost)
   - `DB_PORT`: Your PostgreSQL port (default: 5432)
   - `DB_NAME`: Your database name (default: postgres)
   - `DB_USER`: Your PostgreSQL username (default: postgres)
   - `DB_PASS`: Your PostgreSQL password

### Step 3: Test the Connection

1. Make sure PostgreSQL is running
2. Make sure XAMPP Apache is running
3. Open your browser and navigate to:
   ```
   http://localhost/medical/test_connection.php
   ```

### Step 4: Enable PostgreSQL Extension in PHP

Make sure PostgreSQL extension is enabled in your PHP configuration:

1. Open `php.ini` (usually in `C:\xampp\php\php.ini`)
2. Find and uncomment these lines (remove the semicolon):
   ```
   extension=pdo_pgsql
   extension=pgsql
   ```
3. Restart Apache

## Database Tables

- **reports**: Main table for medical reports
- **report_files**: Stores file information for uploaded reports
- **extracted_text**: Stores OCR-extracted text from reports
- **lab_results**: Stores structured lab test results
- **explanations**: Stores AI-generated explanations and tips

## VS Code Extensions (Recommended)

Install these extensions in VS Code:
- **PostgreSQL** by Chris Kolkman
- **SQLTools** by Matheus Teixeira
- **SQLTools PostgreSQL Driver** by Matheus Teixeira
- **PHP Intelephense** by Ben Mewburn

## Connecting VS Code to PostgreSQL

1. Install the SQLTools extension
2. Click on the SQLTools icon in VS Code sidebar
3. Click "Add New Connection"
4. Select "PostgreSQL"
5. Enter your connection details:
   - Connection name: Medical Reports DB
   - Server: localhost
   - Port: 5432
   - Database: postgres
   - Username: postgres
   - Password: [your password]
6. Click "Test Connection" then "Save Connection"

Now you can browse tables, run queries, and manage your database directly from VS Code!
