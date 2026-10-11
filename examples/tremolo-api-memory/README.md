# tremolo-api-memory

Todo JSON API built with Tremolo and in-memory storage. Plain-JSON example for the [JSON API contract](../../specs/json-api.md) and [shared todo behavior](../../specs/todo-behavior.md). Exempt from OpenAPI expectations (Tremolo generates no OpenAPI).

Tremolo is a zero-dependency, stream-oriented async HTTP server + microframework. Routes are registered with `@app.route`; per-method dispatch uses class-based views (`get`/`post`/`patch`/`delete` methods on the routed class). There is no app-factory idiom beyond constructing `Application()` — `create_app(repo=None)` in `src/app/main.py` builds a fresh `Application` with a fresh (or injected) in-memory store, so each call yields isolated state.

## Run

From the repo root:

```sh
uv run --project examples/tremolo-api-memory python -m app.main
```

Then `GET http://localhost:8000/todos`. `PORT` env var overrides the port (default `8000`):

```sh
PORT=8001 uv run --project examples/tremolo-api-memory python -m app.main
```

## Notes

- No test client ships with Tremolo; the app is exercised over live HTTP against the booted server.
- Unknown ids (including non-numeric `/todos/{id}` segments) return `404` with a JSON body; missing/empty `title` returns `422` with a JSON body.
