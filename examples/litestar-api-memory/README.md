# litestar-api-memory

Todo JSON API built with Litestar and in-memory storage. Implements the [JSON API contract](../../specs/json-api.md) and [shared todo behavior](../../specs/todo-behavior.md).

## Run

From this directory:

```sh
uv run uvicorn app.main:app --port 8000
```

Then `GET http://localhost:8000/todos`. OpenAPI JSON at `http://localhost:8000/schema/openapi.json` (interactive docs at `http://localhost:8000/schema/swagger`).

## Notes

- In-memory store starts empty; data is lost on restart.
- Empty or missing `title` returns `422` with a JSON body (Litestar request-validation errors default to `400`, so an exception handler maps them to `422` to match the contract).
- Unknown ids return `404` with a JSON body.
