# emmett-api-memory

Todo JSON API built with [Emmett](https://emmett.sh) (async framework) and in-memory storage.
Implements the [JSON API contract](../../specs/json-api.md)
and [shared todo behavior](../../specs/todo-behavior.md).

JSON is served with Emmett's idiomatic `@service.json` pipes on async route
handlers; statuses are set via `response.status` (Emmett has no exception-based
HTTP-error idiom that preserves a JSON body, and its default error pages are
HTML, so handlers return `{"detail": ...}` dicts with explicit 404/422
statuses instead). Bodies are read with `await request.body_params`, which
parses `application/json` request bodies.

## Run

From the repo root (port defaults to 8000; set `PORT` to override, which the
shared live harness uses to boot examples on ephemeral ports):

```sh
PORT=8001 uv run --project examples/emmett-api-memory python -m app.main
```

Then `GET http://localhost:8001/todos`. The server is
[Granian](https://github.com/emmett-framework/granian) (Emmett's own server
backend) serving the app over ASGI; `src/app/main.py:main()` reads `$PORT` at
runtime with a default of `8000`.

## Notes

- OpenAPI: EXEMPT — Emmett generates no OpenAPI documentation (per
  `specs/json-api.md`, plain-JSON examples without a generator are exempt).
- Testable entry point: `create_app(repo=None)` in `src/app/main.py` returns a
  fresh `emmett.App` with its own empty `InMemoryTodoRepository`; a
  module-level `app = create_app()` is also exposed for serving.
- Harness driving (two supported paths):
  - Live server (required proof): boot `python -m app.main` with `PORT=<free>`
    from the repo root via `uv run --project examples/emmett-api-memory`,
    wait for `/todos` to answer, then drive plain HTTP with
    `Content-Type: application/json` bodies.
  - In-process sync test client (no awaiting — handlers stay async inside the
    app, the client drives the loop itself): `client = create_app().test_client()`,
    then `client.get/post/patch/delete(path, ...)` returning a
    `ClientResponse` with `.status` (int, **not** `.status_code`), `.data`
    (str) and `.json()` (method). JSON bodies must be passed as
    `data=json.dumps(payload)` **plus** `headers=[("Content-Type",
    "application/json")]` — the `content_type=` kwarg is silently dropped by
    an emmett-core bug (`Headers.get` calls `name.lower` without parentheses,
    so it always returns the default and the scope is built without a
    content type; the server then sees `text/plain` and `body_params` is
    empty). Passing the header explicitly works.
- Status mapping is done in the example: unknown integer ids → 404 with a JSON
  body; missing/empty/non-string title → 422 with a JSON body (a present but
  wrongly-typed `done` is also 422); create → 201; delete → 204.
- Minor deviation: non-integer ids (e.g. `/todos/abc`) never reach a handler —
  Emmett's router answers 404 with a `text/plain` body. The shared contract
  checks only use integer unknown ids (`/todos/9999`), which return JSON 404s.

## What won't be there

- No database, ORM, migrations, templates, auth, or OpenAPI surface — JSON
  endpoints over an in-memory store only, per the `emmett-api-memory` folder
  name.
