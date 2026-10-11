# cherrypy-api-memory

Todo JSON API built with CherryPy and in-memory storage. Implements the [JSON API contract](../../specs/json-api.md) and [shared todo behavior](../../specs/todo-behavior.md). Exempt from OpenAPI expectations (CherryPy generates no OpenAPI).

Routing uses `cherrypy.dispatch.MethodDispatcher`, the idiomatic CherryPy way to serve REST: a single exposed `TodoResource` mounted at `/todos` maps `GET`/`POST`/`PATCH`/`DELETE` onto same-named methods, with leftover path segments (`{id}`) arriving as positional args. Validation is manual (empty/missing title → `422`, unknown id → `404`, both with a JSON body); `DELETE` returns `204` with an empty body.

## Run

From the repo root:

```sh
uv run --project examples/cherrypy-api-memory python -m app.main
```

Then `GET http://localhost:5000/todos`. `PORT` env var overrides the port.
