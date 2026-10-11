# tornado-api-memory

Todo JSON API built with Tornado and in-memory storage. Implements the [JSON API contract](../../specs/json-api.md) and [shared todo behavior](../../specs/todo-behavior.md).

Tornado generates no OpenAPI documentation, so this example is exempt from OpenAPI expectations.

## Run

From this directory:

```sh
uv run python -m app.main
```

Then `GET http://localhost:8000/todos`.

To listen on a different port (the shared harness boots examples on ephemeral ports):

```sh
PORT=8123 uv run python -m app.main
```
