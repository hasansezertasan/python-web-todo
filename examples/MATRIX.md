# Examples matrix

One folder per example under `examples/`. Run commands assume the repo root as working directory unless the example README says otherwise.

| Example | Interface | Rendering | Storage | Status | Run |
| ------- | --------- | --------- | ------- | ------ | --- |
| `django-ssr-memory-native` | Server-rendered | Django templates | In-memory | Done | `uv run --project examples/django-ssr-memory-native python examples/django-ssr-memory-native/manage.py runserver` |
| `django-ssr-memory-jinja` | Server-rendered | Jinja | In-memory | Done | `uv run --project examples/django-ssr-memory-jinja python examples/django-ssr-memory-jinja/manage.py runserver` |
| `django-api-memory-drf` | JSON API | — | In-memory | Done | `uv run --project examples/django-api-memory-drf python examples/django-api-memory-drf/manage.py runserver` |
| `django-api-sqlite-drf` | JSON API | — | SQLite | Done | `uv run --project examples/django-api-sqlite-drf python examples/django-api-sqlite-drf/manage.py runserver` |
| `flask-api-memory` | JSON API | — | In-memory | Done | `uv run --project examples/flask-api-memory flask --app app.main run` |
| `flask-api-sqlite-sqlalchemy` | JSON API | — | SQLite | Done | `uv run --project examples/flask-api-sqlite-sqlalchemy flask --app app.main run` |
| `flask-ssr-memory-jinja` | Server-rendered | Jinja | In-memory | Done | `uv run --project examples/flask-ssr-memory-jinja flask --app app.main run` |
| `fastapi-api-memory` | JSON API | — | In-memory | Done | `uv run --project examples/fastapi-api-memory uvicorn app.main:app` |
| `fastapi-api-sqlite-sqlalchemy` | JSON API | — | SQLite | Done | `uv run --project examples/fastapi-api-sqlite-sqlalchemy uvicorn app.main:app` |
| `litestar-api-memory` | JSON API | — | In-memory | Done | `uv run --project examples/litestar-api-memory uvicorn app.main:app` |
| `litestar-api-sqlite-advanced-alchemy` | JSON API | — | SQLite | Done | `uv run --project examples/litestar-api-sqlite-advanced-alchemy uvicorn app.main:app` |
| `litestar-ssr-memory` | Server-rendered | Jinja | In-memory | Done | `uv run --project examples/litestar-ssr-memory uvicorn app.main:app` |
| `starlette-api-memory` | JSON API | — | In-memory | Done | `uv run --project examples/starlette-api-memory uvicorn app.main:app` |
| `blacksheep-api-memory` | JSON API | — | In-memory | Done | `uv run --project examples/blacksheep-api-memory uvicorn app.main:app` |
| `sanic-api-memory` | JSON API | — | In-memory | Done | `uv run --project examples/sanic-api-memory sanic app.main:app --host=0.0.0.0 --port=8000` |
| `falcon-api-memory` | JSON API | — | In-memory | Done | `uv run --project examples/falcon-api-memory gunicorn app.main:app` |
| `bottle-api-memory` | JSON API | — | In-memory | Done | `uv run --project examples/bottle-api-memory python -m app.main` |
| `clastic-api-memory` | JSON API | — | In-memory | Done | `uv run --project examples/clastic-api-memory python -m app.main` |
| `connexion-api-memory` | JSON API | — | In-memory | Done | `uv run --project examples/connexion-api-memory uvicorn app.main:app` |
| `muffin-api-memory` | JSON API | — | In-memory | Done | `uv run --project examples/muffin-api-memory uvicorn app.main:app` |
| `cherrypy-api-memory` | JSON API | — | In-memory | Done | `uv run --project examples/cherrypy-api-memory python -m app.main` |
| `quart-api-memory` | JSON API | — | In-memory | Done | `uv run --project examples/quart-api-memory hypercorn app.main:app --bind 0.0.0.0:5000` |
| `pyramid-ssr-memory` | Server-rendered | Chameleon | In-memory | Done | `uv run --project examples/pyramid-ssr-memory pyramid-ssr-memory` |
| `pycnic-api-memory` | JSON API | — | In-memory | Done | `uv run --project examples/pycnic-api-memory python -m app.main` |
| `morepath-api-memory` | JSON API | — | In-memory | Done | `uv run --project examples/morepath-api-memory python -m app.main` |
| `aiohttp-api-memory` | JSON API | — | In-memory | Done | `uv run --project examples/aiohttp-api-memory python -m app.main` |
| `responder-api-memory` | JSON API | — | In-memory | Done | `uv run --project examples/responder-api-memory uvicorn app.main:app` |
| `tornado-api-memory` | JSON API | — | In-memory | Done | `uv run --project examples/tornado-api-memory python -m app.main` |
| `twisted-api-memory` | JSON API | — | In-memory | Done | `uv run --project examples/twisted-api-memory python -m app.main` |
| `robyn-api-memory` | JSON API | — | In-memory | Done | `uv run --project examples/robyn-api-memory python -m app.main` |
| `rsgi-api-memory` | JSON API | — | In-memory | Done | `uv run --project examples/rsgi-api-memory python -m app.main` |
| `socketify-api-memory` | JSON API | — | In-memory | Done | `uv run --project examples/socketify-api-memory python -m app.main` |
| `tremolo-api-memory` | JSON API | — | In-memory | Done | `uv run --project examples/tremolo-api-memory python -m app.main` |
| `lona-api-memory` | JSON API | — | In-memory | Done | `uv run --project examples/lona-api-memory python -m app.main` |
| `baize-api-memory` | JSON API | — | In-memory | Done | `uv run --project examples/baize-api-memory python -m app.main` |
| `circuits-api-memory` | JSON API | — | In-memory | Done | `uv run --project examples/circuits-api-memory python -m app.main` |
| `klein-api-memory` | JSON API | — | In-memory | Done | `uv run --project examples/klein-api-memory python -m app.main` |
| `quixote-api-memory` | JSON API | — | In-memory | Done | `uv run --project examples/quixote-api-memory python -m app.main` |
| `turbogears-ssr-memory` | Server-rendered | Genshi | In-memory | Done | `uv run --project examples/turbogears-ssr-memory turbogears-ssr-memory` |
| `wheezy-web-api-memory` | JSON API | — | In-memory | Done | `uv run --project examples/wheezy-web-api-memory python -m app.main` |
| `emmett-api-memory` | JSON API | — | In-memory | Done | `uv run --project examples/emmett-api-memory python -m app.main` |
| `flama-api-memory` | JSON API | — | In-memory | Done | `uv run --project examples/flama-api-memory python -m app.main` |
| `view-api-memory` | JSON API | — | In-memory | Done | `uv run --project examples/view-api-memory python -m app.main` |
