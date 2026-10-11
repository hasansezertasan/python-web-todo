# django-api-sqlite-drf

Todo JSON API built with Django, Django REST framework (DRF) and SQLite storage.
Implements the [JSON API contract](../../specs/json-api.md) and
[shared todo behavior](../../specs/todo-behavior.md).

## Run

From this directory:

```sh
uv run python manage.py runserver
```

Tables are migrated automatically on `runserver` startup (see "Test isolation"
below). Then `GET http://localhost:8000/todos`. Data persists in `db.sqlite3`
in this directory.

## Layout

Django's native layout (project + app packages, root `manage.py`) conflicts
with the repo `src` rule, so per the skill's idiom-over-rule guidance:

- `manage.py` stays at the example root (framework-mandated, allowed) and only
  wires `src/` onto `sys.path` before delegating to Django.
- Project and app code live in the single package `src/app/` (`settings`,
  `urls`, `wsgi`, `models`, `serializers`, `views`, plus the `create_app()`
  factory in `main.py`), keeping the hatchling `packages = ["src/app"]` build
  working. One package doubles as project and app instead of the classic
  `project/` + `app/` split.

## Test isolation (for the shared harness)

- DB path override: `TODO_DB_PATH` env var, read by `src/app/settings.py`
  (defaults to `db.sqlite3` inside this directory). `create_app(db_path=...)`
  in `src/app/main.py` also accepts the path as a parameter and overrides
  `DATABASES["default"]["NAME"]` in-process, so it works even if settings were
  already imported.
- Migrations run automatically at startup/setup: `create_app()` calls
  `call_command("migrate", run_syncdb=True)`, and `manage.py runserver` does
  the same before serving. No migration files are shipped; tables for the
  migration-less `app` are created via Django's `run_syncdb` path.

## Notes

- Validation errors (missing/empty title) are `422` with a JSON body, per the
  contract: DRF serializers natively return `400`, so a small
  `EXCEPTION_HANDLER` (`app.views.api_exception_handler`) maps serializer
  `400`s to `422`.
- Unknown ids and unknown paths return `404` with a JSON body (DRF default
  detail plus a catch-all route, so non-integer ids are JSON too).
- OpenAPI: exempt — plain DRF generic views with no schema generator, same
  exemption class as bare-Flask-style examples.
