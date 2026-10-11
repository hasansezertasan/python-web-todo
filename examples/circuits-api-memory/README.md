# circuits-api-memory

Todo JSON API built with [circuits.web](https://circuitsframework.com/) (circuits' event-driven component framework) and in-memory storage. Implements the [JSON API contract](../../specs/json-api.md) and [shared todo behavior](../../specs/todo-behavior.md).

circuits.web generates no OpenAPI documentation, so this example is exempt from OpenAPI expectations.

## Run

From the repo root:

```sh
uv run --project examples/circuits-api-memory python -m app.main
```

Then `GET http://localhost:8000/todos`.

To listen on a different port (the shared harness boots examples as subprocesses on ephemeral ports):

```sh
PORT=8123 uv run --project examples/circuits-api-memory python -m app.main
```

`PORT` defaults to `8000` when unset.

## Design

- `src/app/controllers.py`: a `TodosController(Component + Controller)` bound to the `/todos` channel with one handler per HTTP verb (`GET`/`POST`/`PATCH`/`DELETE`). The `Controller` metaclass auto-exposes each verb method, and the default `Dispatcher` routes requests on this channel to the matching handler, passing the todo id path segment as an argument. Responses are JSON (`Content-Type: application/json`); statuses are set on `self.response` (`201` on create, `204` on delete, `404` with a JSON body for unknown ids, `422` with a JSON body for empty/missing titles).
- `src/app/repository.py`: process-local `InMemoryTodoRepository`, seeded empty.
- `src/app/main.py`: `create_app(store=None, host="0.0.0.0", port=8000)` is the factory equivalent — circuits has no separate app object, so it returns a bound `Server` with a `TodosController` registered; call `.run()` to serve. Each boot (fresh subprocess) starts with an empty store, which is how the shared harness gets test isolation. `main()` honors the `PORT` env var (default `8000`).
