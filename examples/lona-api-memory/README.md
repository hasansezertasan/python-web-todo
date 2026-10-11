# lona-api-memory

Todo JSON API built with Lona and in-memory storage. Implements the [JSON API contract](../../specs/json-api.md) and [shared todo behavior](../../specs/todo-behavior.md).

## Run

From the repo root:

```sh
uv run --project examples/lona-api-memory python -m app.main
```

Then `GET http://localhost:8000/todos`.

To listen on another port, set `PORT` (default `8000`):

```sh
PORT=8001 uv run --project examples/lona-api-memory python -m app.main
```

## Test isolation

`create_app(repo=None)` builds a fresh Lona `App` with its own empty
`InMemoryTodoRepository`; module-level `app` is the runnable instance.

## Notes

- Lona idioms: `lona.App` + `@app.route(...)` with `View` subclasses, and
  `lona.responses.JsonResponse` for JSON bodies. Plain request/response
  handling uses the `http_pass_through=True` route mode, in which
  `handle_request` receives the raw aiohttp request; the empty `204` delete
  response is a raw aiohttp response, which Lona passes through untouched.
- Lona generates no OpenAPI, so this example is **exempt** from OpenAPI
  expectations (like other plain-JSON examples).
- Lona serves via aiohttp, not ASGI, so it cannot be driven with
  `starlette.testclient.TestClient`; verify via the live server instead.
- Lona natively defaults to port `8080` (`LONA_DEFAULT_PORT`); this example
  defaults to `8000` like the other examples and honors `PORT`.
- Python 3.14 note: Lona's runner calls the removed-behavior
  `asyncio.get_event_loop()`, so `main()` installs a fresh event loop first.
  Install and all request handling are otherwise clean on 3.14
  (tested with `lona==1.16.2`, `aiohttp==3.14.4`).
