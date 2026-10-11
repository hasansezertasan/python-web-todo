# fastapi-api-memory

Todo JSON API built with FastAPI and in-memory storage. Reference example for the [JSON API contract](../../specs/json-api.md) and [shared todo behavior](../../specs/todo-behavior.md).

## Run

From this directory:

```sh
uv run uvicorn app.main:app
```

Then `GET http://localhost:8000/todos`. Interactive docs at `http://localhost:8000/docs`.
