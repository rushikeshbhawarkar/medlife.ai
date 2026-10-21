# Adding a feature

1. Create a Django app under `apps/` (for example `python manage.py startapp reminders apps/reminders`), then make sure its package path and `apps.py` are correct.
2. Add `apps.reminders` to `INSTALLED_APPS` in `config/settings/base.py`.
3. Define database tables in `models.py`, register each model in `admin.py`, and create migrations with `python manage.py makemigrations reminders`.
4. Add request/response validation in `serializers.py`.
5. Put business rules, transactions, and ORM operations in `services.py`; keep HTTP views thin in `views.py`.
6. Add feature routes in `urls.py`.
7. Add one `include("apps.reminders.urls")` line to `config/urls.py` under the `medlife/` prefix.
8. Write model and API tests under `tests/`, including success, validation, and failure cases.
9. Document endpoints and database relationships in `docs/API.md` and `docs/DATABASE.md`.
10. Run `python manage.py makemigrations`, `python manage.py migrate`, and `python manage.py test` against PostgreSQL.

For a detailed walkthrough with an example, database-change recipes and troubleshooting, see `FUTURE_UPDATES.md`. For environment variables, see `ENV_GUIDE.md`.
