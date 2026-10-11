# connexion-api-memory

Todo JSON API built with Connexion 3.x (OpenAPI-first, Starlette-based ASGI) and in-memory storage. Implements the [JSON API contract](../../specs/json-api.md) and [shared todo behavior](../../specs/todo-behavior.md).

## Run

From the repo root:

```sh
uv run --project examples/connexion-api-memory uvicorn app.main:app
```

Then `GET http://localhost:8000/todos`. OpenAPI document at `http://localhost:8000/openapi.json`; Swagger UI at `http://localhost:8000/ui/`.

## Notes

- OpenAPI-first: the operations are defined in `src/app/openapi.yaml` first; the handler functions in `src/app/handlers.py` are wired via `operationId` (`app.handlers.*`).
- Validation is enforced twice: the spec requires a non-empty `title` (`required` + `minLength: 1`), and the handlers re-check so a missing/empty title always yields `422` with a JSON body. Connexion renders request-validation failures as `400` by default, so the app remaps those to the contract's `422` (see `src/app/main.py`).
- Unknown ids yield `404` with a JSON problem body; `DELETE` yields `204`.
- Test entry point: `create_app()` in `app.main` (accepts an optional repository for fresh state). Connexion 3.x `AsyncApp` is an ASGI app: use `app.test_client()` or `starlette.testclient.TestClient(app)`.
