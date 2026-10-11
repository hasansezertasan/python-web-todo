"""Server-rendered todo app with Pyramid, Chameleon, and in-memory storage."""

from pathlib import Path

from chameleon import PageTemplateFile
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.router import Router

from .models import Todo
from .repository import InMemoryTodoRepository

ERROR_EMPTY_TITLE = "Title must not be empty"

_template = PageTemplateFile(
    str(Path(__file__).resolve().parent / "templates" / "index.pt")
)


def _page(todos: list[Todo], error: str | None = None, status: int = 200) -> Response:
    return Response(_template(todos=todos, error=error), status=status)


def create_app(repo: InMemoryTodoRepository | None = None) -> Router:
    """Configurator factory returning the WSGI router with a fresh store."""
    repo = repo or InMemoryTodoRepository()

    def index(request: Request) -> Response:
        return _page(repo.list())

    def add_todo(request: Request) -> Response:
        title = (request.POST.get("title") or "").strip()
        if not title:
            return _page(repo.list(), error=ERROR_EMPTY_TITLE, status=400)
        repo.create(title=title)
        return HTTPFound(location="/")

    def toggle_todo(request: Request) -> Response:
        try:
            repo.toggle(int(request.matchdict["todo_id"]))
        except KeyError:
            raise HTTPNotFound from None
        return HTTPFound(location="/")

    def delete_todo(request: Request) -> Response:
        try:
            repo.delete(int(request.matchdict["todo_id"]))
        except KeyError:
            raise HTTPNotFound from None
        return HTTPFound(location="/")

    config = Configurator()
    config.add_route("index", "/")
    config.add_view(index, route_name="index", request_method="GET")
    config.add_route("add", "/todos")
    config.add_view(add_todo, route_name="add", request_method="POST")
    config.add_route("toggle", r"/todos/{todo_id:\d+}/toggle")
    config.add_view(toggle_todo, route_name="toggle", request_method="POST")
    config.add_route("delete", r"/todos/{todo_id:\d+}/delete")
    config.add_view(delete_todo, route_name="delete", request_method="POST")
    return config.make_wsgi_app()
