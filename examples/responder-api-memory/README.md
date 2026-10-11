# responder-api-memory

Todo JSON API built with Responder (function-based endpoints with `req`/`resp`, one
function per method) and in-memory storage.
Implements the [JSON API contract](../../specs/json-api.md) and [shared todo behavior](../../specs/todo-behavior.md).

## Run

From the repo root:

```sh
uv run --project examples/responder-api-memory uvicorn app.main:app
```

Then `GET http://localhost:8000/todos`. OpenAPI schema (YAML) at
`http://localhost:8000/schema.yml`.

## Test isolation

`create_app(repo=None)` builds a fresh `responder.API` app with its own empty
`InMemoryTodoRepository`; module-level `app` is the runnable instance.
Responder is Starlette-based ASGI, so the shared harness can drive it directly
with `starlette.testclient.TestClient(app)` (equivalently, the app's own cached
client via `app.requests`).

## Notes

- OpenAPI is generated: `API(openapi="3.0.2")` exposes all five operations with
  the `TodoRead` item schema (`id`, `title`, `done`) at `/schema.yml`. The docs UI
  is not enabled (no `/docs/` route), only the schema file.
- Status-code mapping is done in the example: missing/empty title (or an
  unreadable JSON body) returns `422` with a JSON body, unknown ids return `404`
  with a JSON body — Responder's own body-parse errors would otherwise be `400`.
- One function endpoint per method: registering `GET`+`POST` on a single function
  makes plain `GET` requests fail body parsing, so each method gets its own
  function on the same path.
- `requires-python` is `>=3.11` (not `>=3.10` like older examples) because
  Responder 9 requires Python 3.11+.
- `httpx` is a runtime dependency so `starlette.testclient.TestClient` works out
  of the box.
