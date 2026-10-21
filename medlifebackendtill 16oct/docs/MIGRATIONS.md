<!-- # Database connection and migrations (start here)

## The mental model
A **migration** is a numbered recipe file that builds or changes tables. Django remembers which recipes already ran in a table called `django_migrations`. `migrate` runs only the recipes not yet listed there, so running it twice is harmless.

This project has 3 apps with tables: `accounts` (0001, 0002), `members` (0001), `chat` (0001). `core` and `ai` have no tables. Plus Django's own (auth, admin, sessions...).

## Connect to the database
1. PostgreSQL must be running on the host/port in `.env` (`POSTGRES_HOST`, `POSTGRES_PORT` = **5433** in the supplied `.env`).
2. The user and database from `.env` must exist (one-time, as the postgres admin in `psql`):
```sql
CREATE USER medlife_user WITH PASSWORD 'your-password-from-.env' CREATEDB;
CREATE DATABASE medlife OWNER medlife_user;
```
   (If the user already exists: `ALTER USER medlife_user CREATEDB;`. CREATEDB is only needed for `manage.py test`.)
3. `.env` sits next to `manage.py`. Test the connection: `python manage.py check --database default` then `python manage.py showmigrations`.

## Case A: the database you already migrated with the old project
```powershell
python manage.py showmigrations accounts members chat   # all should show [X]
python manage.py migrate                                 # prints "No migrations to apply."
```
Nothing is rebuilt and no data is touched, because no model or migration file was changed in this version.
Optional safety backup first: `pg_dump -p 5433 -U medlife_user -d medlife -F c -f medlife_backup.dump`

## Case B: a brand-new empty database
```powershell
python manage.py migrate        # creates every table (accounts.0001 ... chat.0001)
python manage.py createsuperuser # optional, for /admin/
```

## Case C: Docker PostgreSQL
```powershell
docker compose up -d db     # reads POSTGRES_* from .env, published on POSTGRES_PORT (5433)
python manage.py migrate
```

## When you change a model later
```powershell
python manage.py makemigrations     # writes a new numbered file; READ it
python manage.py migrate
python manage.py makemigrations --check --dry-run   # must say "No changes detected"
```
Rules that prevent migration pain: commit the migration files; never edit or delete a migration that has been applied anywhere; never delete the `migrations/` folders; never rename a model/field by hand (use `makemigrations` and answer "yes" to the rename question); don't run `--fake` unless you are certain the table already matches.

## Troubleshooting
| Message | Cause | Fix |
|---|---|---|
| `connection refused` / `could not connect` | wrong port or PostgreSQL stopped | match `POSTGRES_PORT` in `.env` to the server (5433) and start PostgreSQL / `docker compose up -d db` |
| `password authentication failed for user` | `.env` password differs from the DB user's | `ALTER USER medlife_user WITH PASSWORD '...';` or fix `.env`. A real shell variable named `POSTGRES_PASSWORD` overrides `.env`: `Remove-Item Env:POSTGRES_PASSWORD` |
| `database "medlife" does not exist` | step 2 above not done | `CREATE DATABASE medlife OWNER medlife_user;` |
| `permission denied for schema public` | PostgreSQL 15+ and the DB is not owned by the user | `ALTER DATABASE medlife OWNER TO medlife_user;` |
| `permission denied to create database` (only `manage.py test`) | missing CREATEDB | `ALTER USER medlife_user CREATEDB;` |
| `relation "accounts_account" already exists` | tables exist but `django_migrations` does not know | restore the matching backup, or if the schema is certainly identical `python manage.py migrate --fake` |
| `ModuleNotFoundError: dotenv/rest_framework/psycopg` | packages not installed in the active venv | activate `.venv`, `pip install -r requirements/dev.txt` |
| `POSTGRES_PASSWORD is empty` | `.env` not next to `manage.py`, or saved as `.env.txt` | place it correctly |
| `No changes detected` after editing a model | app not in `INSTALLED_APPS`, or edited the wrong file | check `config/settings/base.py` |
| `ImproperlyConfigured: DJANGO_SECRET_KEY ...` | production settings with a placeholder key | generate a real key (see README production checklist) | -->




# Database connection and migrations (start here)

## The mental model
A **migration** is a numbered recipe file that builds or changes tables. Django remembers which recipes already ran in a table called `django_migrations`. `migrate` runs only the recipes not yet listed there, so running it twice is harmless.

The project has tables for `accounts`, `members`, `chat`, and `documents` (`ScannedDocument`). The documents app has an additive `0001_initial` migration that creates its own table; it does not alter existing account, member, or chat tables. `core` and `ai` have no application tables. Django also creates its own auth/admin/session tables.

## Connect to the database
1. PostgreSQL must be running on the host/port in `.env` (`POSTGRES_HOST`, `POSTGRES_PORT` = **5433** in the supplied `.env`).
2. The user and database from `.env` must exist (one-time, as the postgres admin in `psql`):
```sql
CREATE USER medlife_user WITH PASSWORD 'your-password-from-.env' CREATEDB;
CREATE DATABASE medlife OWNER medlife_user;
```
   (If the user already exists: `ALTER USER medlife_user CREATEDB;`. CREATEDB is only needed for `manage.py test`.)
3. `.env` sits next to `manage.py`. Test the connection: `python manage.py check --database default` then `python manage.py showmigrations`.

## Case A: the database you already migrated with the old project
```powershell
python manage.py showmigrations accounts members chat documents
python manage.py migrate
```
On an existing database, Django applies only migrations not yet recorded as applied. For this feature, that normally means applying `documents.0001_initial` to create the new `documents_scanneddocument` table; existing account, member, chat, and other data are not recreated or reset.
Optional safety backup first: `pg_dump -p 5433 -U medlife_user -d medlife -F c -f medlife_backup.dump`

## Case B: a brand-new empty database
```powershell
python manage.py migrate        # creates all tables, including documents_scanneddocument
python manage.py createsuperuser # optional, for /admin/
```

## Case C: Docker PostgreSQL
```powershell
docker compose up -d db     # reads POSTGRES_* from .env, published on POSTGRES_PORT (5433)
python manage.py migrate
```

## When you change a model later
```powershell
python manage.py makemigrations     # writes a new numbered file; READ it
python manage.py migrate
python manage.py makemigrations --check --dry-run   # must say "No changes detected"
```
Rules that prevent migration pain: commit the migration files; never edit or delete a migration that has been applied anywhere; never delete the `migrations/` folders; never rename a model/field by hand (use `makemigrations` and answer "yes" to the rename question); don't run `--fake` unless you are certain the table already matches.

## Troubleshooting
| Message | Cause | Fix |
|---|---|---|
| `connection refused` / `could not connect` | wrong port or PostgreSQL stopped | match `POSTGRES_PORT` in `.env` to the server (5433) and start PostgreSQL / `docker compose up -d db` |
| `password authentication failed for user` | `.env` password differs from the DB user's | `ALTER USER medlife_user WITH PASSWORD '...';` or fix `.env`. A real shell variable named `POSTGRES_PASSWORD` overrides `.env`: `Remove-Item Env:POSTGRES_PASSWORD` |
| `database "medlife" does not exist` | step 2 above not done | `CREATE DATABASE medlife OWNER medlife_user;` |
| `permission denied for schema public` | PostgreSQL 15+ and the DB is not owned by the user | `ALTER DATABASE medlife OWNER TO medlife_user;` |
| `permission denied to create database` (only `manage.py test`) | missing CREATEDB | `ALTER USER medlife_user CREATEDB;` |
| `relation "accounts_account" already exists` | tables exist but `django_migrations` does not know | restore the matching backup, or if the schema is certainly identical `python manage.py migrate --fake` |
| `ModuleNotFoundError: dotenv/rest_framework/psycopg` | packages not installed in the active venv | activate `.venv`, `pip install -r requirements/dev.txt` |
| `POSTGRES_PASSWORD is empty` | `.env` not next to `manage.py`, or saved as `.env.txt` | place it correctly |
| `No changes detected` after editing a model | app not in `INSTALLED_APPS`, or edited the wrong file | check `config/settings/base.py` |
| `ImproperlyConfigured: DJANGO_SECRET_KEY ...` | production settings with a placeholder key | generate a real key (see README production checklist) |
