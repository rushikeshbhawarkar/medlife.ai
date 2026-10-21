# How to make future updates to this backend

Read this before adding a feature, changing the database, or changing an endpoint. It builds from the big idea down to exact commands. (`ADDING_A_FEATURE.md` is the short checklist; this is the detailed version with an example.)

## 1. The big idea (a restaurant)

| Restaurant | This backend | File |
|---|---|---|
| Front door and menu: which dishes exist | **URLs** map a web address to a function | `urls.py` |
| Waiter: takes the order, checks it is complete, brings the plate | **Views** read the request, call the service, return JSON | `views.py` |
| Order slip checker: "no table number? send it back" | **Serializers** check the incoming data is valid | `serializers.py` |
| Kitchen: the real cooking and the rules | **Services** hold the business rules | `services.py` |
| Pantry shelves: what is stored and how | **Models** describe the database tables | `models.py` |
| Pantry change log: "we added a shelf on Tuesday" | **Migrations** record each table change | `migrations/` |
| Safety inspector | **Tests** prove it still works | `tests/` |

```text
React  ->  urls.py  ->  views.py  ->  serializers.py (validate)
                                  ->  services.py (rules)  ->  models.py  ->  PostgreSQL
```

**Golden rule:** each layer does only its own job. Views stay thin, rules live in services. This is why a change is usually 1-3 small edits, not a rewrite.

## 2. Where everything lives

```text
backend/
  .env                  secrets and settings (never commit; see ENV_GUIDE.md)
  manage.py             the command-line tool (runserver, migrate, test ...)
  config/               project-wide: settings/base.py, urls.py (the master address book)
  apps/
    core/               shared bits: /health/, error format, identity.py (who is calling)
    accounts/           signup, signin, Account table (email + hashed password)
    members/            family profiles + question counter (tokens)
    chat/               saved chat messages
    ai/                 /prompt/ and AI providers
  docs/                 these guides
```

An **app** is just a folder that owns one feature (its own table, endpoints and tests).

## 3. The one hard rule: match the frontend exactly

The React app calls fixed addresses, so the backend must match them **character for character**, including the trailing slash:

| Frontend calls | Backend route |
|---|---|
| `/signup`, `/signin`, `/getmember`, `/addmember`, `/editmember`, `/removemember` | no trailing slash |
| `/tokens/`, `/prompt/`, `/fetchChat/`, `/saveChat/` | trailing slash |

`APPEND_SLASH = False` is deliberate: Django will **not** auto-redirect `/x` to `/x/`, so a mismatch gives 404. Errors must look like `{"detail": "message"}`, because the frontend shows `detail` to the user. Raising a DRF exception (`ValidationError`, `NotFound`, or a small `APIException` subclass) does this automatically.

## 4. Recipe A: add a brand-new feature (example: "reminders")

Say each family member can have medicine reminders.

| Step | What you do | Command / file |
|---|---|---|
| 1 | Create the app folder | `mkdir apps/reminders` then `python manage.py startapp reminders apps/reminders` |
| 2 | Fix its name in `apps/reminders/apps.py` | `name = "apps.reminders"` |
| 3 | Register it | add `"apps.reminders"` to `INSTALLED_APPS` in `config/settings/base.py` |
| 4 | Describe the table | `models.py`, e.g. a `Reminder` with `member = ForeignKey(FamilyMember, on_delete=CASCADE)`, `text`, `time` |
| 5 | Register in admin | `admin.py` so you can inspect rows at `/admin/` |
| 6 | Create the migration | `python manage.py makemigrations reminders` |
| 7 | Apply it to the database | `python manage.py migrate` |
| 8 | Validate input | `serializers.py` |
| 9 | Write the rules | `services.py` (look the account up with `get_or_create_account`, the member with `apps.members.services._member`) |
| 10 | Thin views | `views.py`, copy the style of `apps/chat/views.py` |
| 11 | Routes | `apps/reminders/urls.py` |
| 12 | Plug into the master address book | one line in `config/urls.py`: `path("medlife/", include("apps.reminders.urls"))` |
| 13 | Tests | `apps/reminders/tests/test_api.py` (success, bad input, missing member) |
| 14 | Document | add endpoints to `docs/API.md`, tables to `docs/DATABASE.md` |
| 15 | Run everything | `python manage.py test` |

Minimal skeleton for steps 8-12:

```python
# serializers.py
class ReminderSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=200)

# services.py
def add_reminder(email, member_name, text):
    account = get_or_create_account(email)
    member = _member(account, member_name)        # raises 404/400 for us
    return Reminder.objects.create(member=member, text=text)

# views.py
@api_view(["POST"])
def addreminder(request):
    email = caller_email(request)
    s = ReminderSerializer(data=request.data); s.is_valid(raise_exception=True)
    r = services.add_reminder(email, request.query_params.get("member_name", ""), s.validated_data["text"])
    return Response({"id": r.id}, status=201)

# urls.py
urlpatterns = [path("addreminder", views.addreminder, name="addreminder")]
```

Then the frontend adds one line to `src/services/api.js` that calls `/addreminder` with the same name.

## 5. Recipe B: change an existing table (add or remove a column)

Example: add `allergies` to a family member.

1. Edit the model in `apps/members/models.py`: `allergies = models.CharField(max_length=500, blank=True, default="")`. Always give new columns a `default` (or `null=True`) so existing rows stay valid.
2. Accept it in `apps/members/serializers.py` (`MemberInputSerializer` field, `to_model_values()`, `member_to_frontend()`). The API uses camelCase (`bloodPressure`) and the database uses snake_case (`blood_pressure`); these two functions are the translators.
3. `python manage.py makemigrations` creates a new numbered file in `migrations/`. Open it and check it only does what you expect.
4. `python manage.py migrate` applies it.
5. Update/add tests, then `python manage.py test`.

**Never edit an old migration** that has already been applied. Always make a new one. **Commit the migration file** with the model change.

## 6. Recipe C: change how an endpoint behaves

| I want to change... | Edit |
|---|---|
| A validation message or limit (password length, name length) | `serializers.py` |
| A rule (max members, question limit) | `services.py` and `MAX_MEMBERS` / `TOKEN_LIMIT` in `config/settings/base.py` |
| What JSON comes back | `views.py` (and the serializer or helper it uses) |
| An address | `urls.py`; remember the frontend must match |

## 7. Recipe D: login that protects data (the next big upgrade)

Today `/signin` checks the password but the data endpoints still trust the `email` they are sent. To make it truly secure:

1. `/signin` also returns a token (JWT or a session cookie).
2. The frontend sends it with every request.
3. Replace the body of `caller_email()` in `apps/core/identity.py` so it reads the logged-in account from the token instead of the `email` parameter. Because every view calls this one function, nothing else changes.

## 8. Everyday commands

| Task | Command (run inside `backend/`, virtual environment active) |
|---|---|
| Start the server | `python manage.py runserver 8000` |
| Create/update tables | `python manage.py makemigrations` then `python manage.py migrate` |
| See pending model changes without writing | `python manage.py makemigrations --check --dry-run` |
| Run all tests | `python manage.py test` |
| Run one app's tests | `python manage.py test apps.accounts` |
| Create an admin login | `python manage.py createsuperuser` |
| Quick health check | open `http://localhost:8000/medlife/health/` |
| Try an endpoint | `curl.exe -X POST "http://localhost:8000/medlife/signin" -H "Content-Type: application/json" -d "{\"email\":\"a@b.com\",\"password\":\"secret1\"}"` |

Windows note: `curl.exe` (with `.exe`) avoids PowerShell's `curl` alias.

## 9. Before you call a change "done"

- [ ] `python manage.py makemigrations --check --dry-run` says "No changes detected" (models and migrations agree)
- [ ] `python manage.py test` passes
- [ ] Endpoint address and slash style match what the frontend calls
- [ ] Errors come back as `{"detail": "..."}`
- [ ] `docs/API.md` / `docs/DATABASE.md` updated
- [ ] Any new setting has a safe default and is documented in `docs/ENV_GUIDE.md`

## 10. Common errors

| Symptom | Usual cause |
|---|---|
| 404 on an endpoint | Slash mismatch with the frontend, or the app's `urls.py` is not included in `config/urls.py` |
| `relation "..." does not exist` | You forgot `python manage.py migrate` |
| `No module named 'apps.x'` | App not in `INSTALLED_APPS`, or `apps.py` `name` is wrong |
| CORS error in the browser | Frontend address missing from `CORS_ALLOWED_ORIGINS` in `.env` |
| `POSTGRES_PASSWORD is empty` | `.env` missing or in the wrong folder (see `ENV_GUIDE.md`) |
| Frontend shows demo data, not database data | The frontend is still in demo mode (`let demo` in `src/services/api.js`), so it never calls this backend |
