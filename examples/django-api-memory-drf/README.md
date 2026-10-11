# django-api-memory-drf

Todo JSON API built with Django + Django REST Framework and in-memory storage.
Implements the [JSON API contract](../../specs/json-api.md) and
[shared todo behavior](../../specs/todo-behavior.md).

## Run

From this directory:

```sh
uv sync
uv run python manage.py runserver 8000
```

Then `GET http://localhost:8000/todos`.

## Notes

- Storage is a process-local in-memory store, seeded empty. Data loss on
  restart is acceptable.
- No OpenAPI document is generated: DRF ships no OpenAPI generator in this
  setup, so this example is exempt from OpenAPI expectations (per
  `specs/json-api.md`, which only requires OpenAPI where the framework
  generates it).
- `DATABASES` is set to a dummy in-memory SQLite config because Django
  requires the setting at startup. It is never touched: there are no models,
  no migrations, and no ORM queries anywhere in this example.
- Django has no app-factory idiom, so there is no `create_app()`. The
  equivalent for contract tests: the views use the module-level singleton
  `app.repository.store`; call `app.repository.reset_store()` (or
  instantiate `InMemoryTodoRepository` directly) for fresh state per test,
  and drive requests with DRF's `APIClient` / Django's test `Client`.
