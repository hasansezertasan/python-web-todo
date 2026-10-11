# rsgi-api-memory

Todo JSON API as a **bare RSGI app** served by [Granian](https://github.com/emmett-framework/granian),
with in-memory storage. Implements the [JSON API contract](../../specs/json-api.md)
and [shared todo behavior](../../specs/todo-behavior.md).

There is no framework here: routing and JSON handling are written directly
against the RSGI `async def app(scope, protocol)` interface
([RSGI spec](https://github.com/emmett-framework/granian/blob/master/docs/spec/RSGI.md)).

## Run

From the repo root (port defaults to 8000; set `PORT` to override):

```sh
PORT=8000
PORT=$PORT uv run --project examples/rsgi-api-memory granian --interface rsgi app.main:app --host 0.0.0.0 --port $PORT
```

(The two-step form matters: a `PORT=...` prefix on the same command line would
not be visible to that line's own `$PORT` expansion. `src/app/main.py:main()`
also reads `$PORT` at runtime, so this equivalent works too:
`PORT=8001 uv run --project examples/rsgi-api-memory python -m app.main`.)

Then `GET http://localhost:8000/todos`.

## Notes

- OpenAPI: EXEMPT — a bare RSGI callable has no OpenAPI generator
  (per `specs/json-api.md`, only framework generators are expected to expose it).
- Testable entry point: there is no app-object factory idiom for bare RSGI;
  `src/app/main.py` exposes `create_app()` (returns the RSGI callable, swaps/resets
  the module-level store) plus `reset_store()` for fresh state per test.
- Harness driving: boot Granian as a subprocess on an ephemeral port
  (`PORT=... granian --interface rsgi app.main:app ...`), wait for the port to
  accept connections, then drive plain HTTP against it. There is no in-process
  test client for bare RSGI.

## What won't be there

- No framework, ORM, database, templates, or OpenAPI surface — JSON endpoints
  over an in-memory store only, per the `rsgi-api-memory` folder name.
