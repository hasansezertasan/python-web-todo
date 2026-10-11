# flask-api-sqlite-sqlalchemy

Todo JSON API built with Flask, SQLite storage, and plain SQLAlchemy 2.0-style ORM.
Implements the [JSON API contract](../../specs/json-api.md) and [shared todo behavior](../../specs/todo-behavior.md).
Exempt from OpenAPI expectations (no generator — plain Flask JSON).

Plain (standalone) SQLAlchemy is used instead of Flask-SQLAlchemy so the ORM
usage stays comparable with the non-Flask examples.

## Run

From the repo root:

```sh
uv run --project examples/flask-api-sqlite-sqlalchemy flask --app app.main run
```

Then `GET http://localhost:5000/todos`.

The default SQLite file is `todos.db` inside this example directory
(resolved from `__file__`, not the current working directory).
`create_app()` accepts an optional `db_url` (e.g. `sqlite:///:memory:`)
so tests get an isolated database; tables are created in `create_app()`.
