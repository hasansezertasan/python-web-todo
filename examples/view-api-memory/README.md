# view-api-memory

Todo JSON API built with [view.py](https://github.com/ZeroIntensity/view.py) (ZeroIntensity's modern ASGI framework) and in-memory storage.
Implements the [JSON API contract](../../specs/json-api.md) and [shared todo behavior](../../specs/todo-behavior.md).

## Run

From the repo root:

```sh
uv run --project examples/view-api-memory python -m app.main
```

Then `GET http://localhost:8000/todos`.

## PORT override

The server listens on port `8000` by default. Set the `PORT` environment variable to change it:

```sh
PORT=8001 uv run --project examples/view-api-memory python -m app.main
```

`main()` reads `PORT` (default `8000`) and passes it explicitly to `app.run(host="0.0.0.0", port=...)` (view.py's built-in runner, served via uvicorn).

## API

| Method | Path | Success |
| ------ | ---- | ------- |
| `GET` | `/todos` | `200` + JSON array |
| `POST` | `/todos` | `201` + created item |
| `GET` | `/todos/{id}` | `200` + item, or `404` |
| `PATCH` | `/todos/{id}` | `200` + item, or `404` |
| `DELETE` | `/todos/{id}` | `204`, or `404` |

Validation is manual (view.py does not validate plain `request.json()` bodies): missing/empty `title` returns `422` with a JSON body, unknown ids (including non-integer ids) return `404` with a JSON body. `PATCH` accepts `title` and/or `done`; a non-boolean `done` returns `422`.

## OpenAPI

view.py generates no OpenAPI, so this example is **exempt** from OpenAPI expectations
(like other plain-JSON examples).

## App factory and test-harness notes

`src/app/main.py` exposes `create_app(repo=None) -> App`, mirroring the reference factory: each call builds a fresh view.py `App` over a fresh (or injected) `InMemoryTodoRepository`.

view.py idioms used: zero-argument route views (`RouteView = Callable[[], ...]`) registered with `@app.get/post/patch/delete`; the current request is read via `app.current_request()` (`request.path_parameters` for `{todo_id}`, `await request.json()` for bodies); responses are `JSONResponse.from_content(..., status_code=...)`; delete returns an empty-body `Response` with status `204`.

Known upstream bug (documented deviation): `view.run.asgi.headers_to_asgi` iterates the header map instead of its items, so any response carrying headers raises `ValueError: too many values to unpack` and becomes a `500` over real HTTP. Responses therefore carry no explicit `content-type` header; bodies are still JSON and parse without it. The contract only asserts status codes plus a JSON body, so this stays compliant.

The app is ASGI: `app.asgi()` returns a standard `(scope, receive, send)` callable, verified working with `starlette.testclient.TestClient(app.asgi())` (HTTP 200 on `GET /todos`). The supported harness approaches are **in-process ASGI** (`TestClient(app.asgi())` on a `create_app()` instance for fresh state) or **subprocess boot + HTTP** (`python -m app.main` with a `PORT` env var).

## Dependency note

`view-py` is pinned to a git URL (`view-py @ git+https://github.com/ZeroIntensity/view.py`, as the upstream README recommends installing from source): the published PyPI wheels (`view-py 1.0.0a10`) ship no `cp314` ABI and no `macOS arm64` platform tag, so a versioned PyPI requirement cannot resolve on this toolchain. Verified installing and importing cleanly on Python 3.14 from source.
