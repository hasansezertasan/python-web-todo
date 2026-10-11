# quixote-api-memory

Todo JSON API built with Quixote and in-memory storage. Implements the [JSON API contract](../../specs/json-api.md) and [shared todo behavior](../../specs/todo-behavior.md).

Quixote generates no OpenAPI documentation, so this example is exempt from OpenAPI expectations.

Quixote notes: routing is a `Publisher` rooted at a `Directory` tree (`RootDirectory` → `TodosDirectory` via `_q_traverse`/`_q_lookup`); HTTP methods are dispatched on `request.get_method()` inside the handlers; the stock `QWIP` adapter exposes the publisher as a WSGI app. The default `allowed_methods` config (GET/HEAD/POST only) is extended with PATCH/DELETE to satisfy the contract, and the publisher is marked thread-safe (the store is lock-protected) so multi-threaded WSGI servers and clients work.

## Run

From the repo root:

```sh
uv run --project examples/quixote-api-memory python -m app.main
```

Then `GET http://localhost:8000/todos`.

To listen on a different port (the shared harness boots examples on ephemeral ports):

```sh
PORT=8123 uv run --project examples/quixote-api-memory python -m app.main
```

`PORT` overrides the listen port; the default is `8000`.
