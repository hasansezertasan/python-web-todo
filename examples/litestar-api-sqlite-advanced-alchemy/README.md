# litestar-api-sqlite-advanced-alchemy

Todo JSON API built with Litestar and SQLite storage via advanced-alchemy. Implements the [JSON API contract](../../specs/json-api.md) and [shared todo behavior](../../specs/todo-behavior.md).

## Run

From the repo root:

```sh
uv run --project examples/litestar-api-sqlite-advanced-alchemy uvicorn app.main:app
```

Then `GET http://localhost:8000/todos`. OpenAPI JSON at `http://localhost:8000/schema/openapi.json` (Swagger UI at `http://localhost:8000/schema/swagger`).

Data persists in `todos.db` inside this example directory by default.

## Test entry point

`create_app()` in `src/app/main.py`:

```python
from app.main import create_app

app = create_app()  # file DB in this example dir
app = create_app(db_url="sqlite+aiosqlite:////tmp/test.db")  # fresh DB per test
```

The `db_url` parameter takes precedence, then the `TODO_DB_URL` environment variable, then the default `todos.db` file resolved from `__file__` (never the cwd). Tables are auto-created at startup (`create_all=True`). Use Litestar's `TestClient` (or `AsyncTestClient`) as a context manager so lifespan — and therefore table creation — runs:

```python
from litestar.testing import TestClient

with TestClient(app) as client:
    assert client.get("/todos").json() == []
```

## Notes and deviations

- Validation errors (missing/empty `title`, wrong types) return Litestar's idiomatic `400` with a JSON body instead of the contract's `422`. Status-code-tolerant checks accepting 422-or-400 pass.
- Unknown ids return `404` with a JSON body via advanced-alchemy's `NotFoundError` and the Litestar plugin's default exception handler.
- Request/response bodies use msgspec Structs (Litestar-native); persistence uses `SQLAlchemyAsyncRepository` with auto-commit and request-scoped sessions from `SQLAlchemyInitPlugin`.
