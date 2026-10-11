# aiohttp-api-memory

Todo JSON API built with aiohttp and in-memory storage. Implements the [JSON API contract](../../specs/json-api.md) and [shared todo behavior](../../specs/todo-behavior.md).

## Run

From the repo root:

```sh
uv run --project examples/aiohttp-api-memory python -m app.main
```

Then `GET http://localhost:8000/todos`. The app listens on port 8000 via `web.run_app`.

## Notes

- Async aiohttp handlers (`async def`, `web.Application`, `app.router` routes, `web.json_response`).
- In-memory store starts empty; each `create_app()` call gets a fresh store.
- aiohttp generates no OpenAPI: exempt from OpenAPI expectations per `specs/json-api.md`.
