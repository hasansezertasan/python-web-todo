"""Server-rendered todo app with Flask, Jinja, and in-memory storage."""

from flask import Flask, Response, abort, redirect, render_template, request, url_for

from .repository import InMemoryTodoRepository

ERROR_EMPTY_TITLE = "Title must not be empty"


def create_app(repo: InMemoryTodoRepository | None = None) -> Flask:
    repo = repo or InMemoryTodoRepository()
    app = Flask(__name__)

    @app.get("/")
    def index() -> str:
        return render_template("index.html", todos=repo.list(), error=None)

    @app.post("/todos")
    def add_todo() -> tuple[str, int] | Response:
        title = (request.form.get("title") or "").strip()
        if not title:
            return (
                render_template(
                    "index.html", todos=repo.list(), error=ERROR_EMPTY_TITLE
                ),
                400,
            )
        repo.create(title=title)
        return redirect(url_for("index"))

    @app.post("/todos/<int:todo_id>/toggle")
    def toggle_todo(todo_id: int) -> Response:
        try:
            repo.toggle(todo_id)
        except KeyError:
            abort(404)
        return redirect(url_for("index"))

    @app.post("/todos/<int:todo_id>/delete")
    def delete_todo(todo_id: int) -> Response:
        try:
            repo.delete(todo_id)
        except KeyError:
            abort(404)
        return redirect(url_for("index"))

    return app


app = create_app()


def main() -> None:
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
