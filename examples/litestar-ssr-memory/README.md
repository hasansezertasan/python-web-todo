# litestar-ssr-memory

Todo server-rendered app built with Litestar, Jinja templates (via `litestar.contrib.jinja.JinjaTemplateEngine`), and in-memory storage. Implements the [server-rendered contract](../../specs/server-rendered.md) and [shared todo behavior](../../specs/todo-behavior.md).

## Run

From the repo root:

```sh
uv run --project examples/litestar-ssr-memory uvicorn app.main:app
```

Then open `http://localhost:8000/`.

## Notes

- Template engine: Litestar's contrib Jinja engine (`JinjaTemplateEngine`); templates live in `src/app/templates/` and are shipped in the wheel via a hatchling `force-include` rule (hatchling ships only `.py` files by default).
- `create_app(repo=None)` builds a fresh `Litestar` app with its own empty `InMemoryTodoRepository` (also reachable as `app.state.repo`); module-level `app` is the runnable instance.
- Empty titles re-render the list with status `400` and the error `Title must not be empty`; unknown ids answer `404`. Page wording matches the `flask-ssr-memory-jinja` sibling (`Todo List` heading, `done`/`not done` states, `Add` / `Mark done` / `Mark not done` / `Delete` controls, `No todos yet.` empty state).
