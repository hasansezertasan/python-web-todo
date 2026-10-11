# fastapi-api-sqlite-sqlalchemy

Todo JSON API built with FastAPI and SQLite storage via SQLAlchemy. Implements the [JSON API contract](../../specs/json-api.md) and [shared todo behavior](../../specs/todo-behavior.md).

## Run

From the repo root:

```sh
uv run --project examples/fastapi-api-sqlite-sqlalchemy uvicorn app.main:app
```

Then `GET http://localhost:8000/todos`. Interactive docs at `http://localhost:8000/docs`.

Data persists in `examples/fastapi-api-sqlite-sqlalchemy/todos.db` (resolved from the source file location, not the working directory). Delete that file to reset state.

## Isolation

`create_app()` accepts an optional `db_url` parameter (defaults to the file above). Contract tests pass `sqlite:///:memory:` for a fresh isolated database per test.
