# pycnic-api-memory

Todo JSON API built with Pycnic and in-memory storage. Plain-JSON example for the [JSON API contract](../../specs/json-api.md) and [shared todo behavior](../../specs/todo-behavior.md). Exempt from OpenAPI expectations (Pycnic generates no OpenAPI).

Idioms: `Handler` subclasses with `get`/`post`/`patch`/`delete` methods, routes as `(regex, handler)` pairs on a `WSGI` subclass. Pycnic ships no 422 error type, so validation failures set `self.response.status_code = 422` directly and return a JSON error body.

## Run

From the repo root:

```sh
uv run --project examples/pycnic-api-memory python -m app.main
```

Then `GET http://localhost:5000/todos`. `PORT` env var overrides the port.

## Test entry point

`create_app()` in `src/app/main.py` returns a fresh `WSGI` subclass with its own empty store (the class itself is the WSGI callable). Drive it with WebTest:

```python
from webtest import TestApp
from app.main import create_app

client = TestApp(create_app())
```

Non-numeric ids (e.g. `/todos/abc`) match no route, so Pycnic answers `404` with a JSON body automatically.
