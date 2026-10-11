"""Server-rendered todo app with TurboGears, Genshi, and in-memory storage."""

from tg import TGController, abort, expose, redirect, request, response
from tg.configuration import AppConfig

from .repository import InMemoryTodoRepository

ERROR_EMPTY_TITLE = "Title must not be empty"


class TodoItemController(TGController):
    """Handles ``/todos/{id}/toggle`` and ``/todos/{id}/delete``."""

    def __init__(self, repo: InMemoryTodoRepository, todo_id: int) -> None:
        self._repo = repo
        self._todo_id = todo_id

    @expose()
    def toggle(self):
        try:
            self._repo.toggle(self._todo_id)
        except KeyError:
            abort(404)
        redirect("/")

    @expose()
    def delete(self):
        try:
            self._repo.delete(self._todo_id)
        except KeyError:
            abort(404)
        redirect("/")


class TodosController(TGController):
    """Handles ``/todos`` (add) and dispatches ``/todos/{id}/*``."""

    def __init__(self, repo: InMemoryTodoRepository) -> None:
        self._repo = repo

    @expose()
    def _lookup(self, todo_id, *remainder):
        try:
            parsed_id = int(todo_id)
        except ValueError:
            abort(404)
        return TodoItemController(self._repo, parsed_id), remainder

    @expose("app.templates.index")
    def index(self):
        if request.method == "POST":
            title = (request.POST.get("title") or "").strip()
            if not title:
                response.status = 400
                return {"todos": self._repo.list(), "error": ERROR_EMPTY_TITLE}
            self._repo.create(title=title)
            redirect("/")
        redirect("/")


class RootController(TGController):
    def __init__(self, repo: InMemoryTodoRepository) -> None:
        self._repo = repo
        self.todos = TodosController(repo)

    @expose("app.templates.index")
    def index(self):
        return {"todos": self._repo.list(), "error": None}


def create_app(repo: InMemoryTodoRepository | None = None):
    """Application factory returning the WSGI app with a fresh store."""
    repo = repo or InMemoryTodoRepository()
    config = AppConfig(minimal=True, root_controller=RootController(repo))
    config.renderers = ["genshi"]
    config.default_renderer = "genshi"
    return config.make_wsgi_app()
