# robyn-api-memory

Todo JSON API built with [Robyn](https://robyn.tech/) (Rust-powered runtime) and in-memory storage. Implements the [JSON API contract](../../specs/json-api.md) and [shared todo behavior](../../specs/todo-behavior.md).

## Run

From the repo root:

```sh
uv run --project examples/robyn-api-memory python -m app.main
```

Then `GET http://localhost:8000/todos`.

## PORT override

The server listens on port `8000` by default. Set the `PORT` environment variable to change it:

```sh
PORT=8001 uv run --project examples/robyn-api-memory python -m app.main
```

`main()` reads `PORT` (default `8000`) and passes it explicitly to `app.start(host="0.0.0.0", port=...)`. Note: Robyn itself also honors a `ROBYN_PORT` env var which takes precedence over the passed port inside `app.start()`; leave `ROBYN_PORT` unset so `PORT` controls the binding.

## API

| Method | Path | Success |
| ------ | ---- | ------- |
| `GET` | `/todos` | `200` + JSON array |
| `POST` | `/todos` | `201` + created item |
| `GET` | `/todos/{id}` | `200` + item, or `404` |
| `PATCH` | `/todos/{id}` | `200` + item, or `404` |
| `DELETE` | `/todos/{id}` | `204`, or `404` |

Validation is manual (Robyn does not validate plain `request.json()` bodies): missing/empty `title` returns `422` with a JSON body, unknown ids (including non-integer ids) return `404` with a JSON body. `PATCH` accepts `title` and/or `done`; a non-boolean `done` returns `422`.

## OpenAPI

Robyn **does** generate OpenAPI by default in this setup (robyn 0.88.0): `GET /openapi.json` (OpenAPI 3.1.0, served by the app) and Swagger UI at `GET /docs`. The spec exposes all five operations above with item schemas containing `id`, `title`, and `done` (via `response_model=TodoRead` / `list[TodoRead]` on the routes, plus `status_code=201` on `POST` and `status_code=204` on `DELETE`).

## App factory and test-harness notes

`src/app/main.py` exposes `create_app(repo=None) -> Robyn`, mirroring the reference factory: each call builds a fresh `Robyn` app over a fresh (or injected) `InMemoryTodoRepository`.

However, a test harness **cannot** drive Robyn in-process the way ASGI apps are driven: `app.start()` blocks and hands routes to a Rust (actix) runtime via `run_processes(...)` (multiprocess pickling). There is no supported ASGI-style in-process test client for route handlers. The expected harness approach is **subprocess boot + HTTP**: start `python -m app.main` with a `PORT` env var in a subprocess, poll `GET /todos` until ready, run HTTP assertions, then terminate the process. One live server process per run (default single worker).
