# django-ssr-memory-jinja

Todo server-rendered app built with Django and Jinja2 templates with in-memory
storage. Implements the [server-rendered contract](../../specs/server-rendered.md)
and [shared todo behavior](../../specs/todo-behavior.md). Jinja2 sibling of
`django-ssr-memory-native` (DTL): same flows, same page text and controls,
idiomatic Jinja2 templates.

Template backend choice: Django's built-in Jinja2 backend
(`django.template.backends.jinja2.Jinja2`) with the `jinja2` package — no
`django-jinja` dependency. URL reversing inside templates goes through a small
`todos.jinja2.environment` that exposes Django's `reverse` as the `url`
global, so `{{ url('todo-toggle', args=[todo.id]) }}` renders the same
`action` attributes as the DTL sibling's `{% url %}` tags.

## Run

From the example directory:

```sh
uv run python manage.py runserver
```

Then open `http://localhost:8000/`.

From the repo root:

```sh
uv run --project examples/django-ssr-memory-jinja python examples/django-ssr-memory-jinja/manage.py runserver
```

## Flows

- `GET /` renders the list page (titles, done/not-done state, add form, one
  toggle and one delete control per item).
- `POST /todos` with a `title` field adds an item, then redirects to `/`.
  An empty title re-renders the list with an error message and creates nothing.
- `POST /todos/{id}/toggle` flips the item state, then redirects to `/`.
- `POST /todos/{id}/delete` removes the item, then redirects to `/`.
- Unknown ids answer `404`.

## Fresh state for tests

Django has no app-factory idiom, so the equivalent is the shared store object:
`todos.store.store` (views use this singleton) plus `todos.store.reset_store()`,
which clears it back to the initial empty state. A test harness gets fresh
state per test by calling `reset_store()` (or `store.clear()`), e.g. in an
autouse fixture with `DJANGO_SETTINGS_MODULE=config.settings`.

## Deviations

- `manage.py` lives at the example root: framework-mandated entry point
  (allowed by the `src` layout rule); it wires `src/` onto `sys.path` and all
  other code lives under `src/config/` and `src/todos/`.
- `DATABASES` uses `django.db.backends.dummy`: Django requires the setting to
  exist, but this example never touches the ORM — any accidental ORM use fails
  loudly instead of creating a database. No database, ORM models, or
  migrations are shipped.
- No CSRF middleware: keeps plain form POSTs working without tokens for this
  local in-memory demo.
