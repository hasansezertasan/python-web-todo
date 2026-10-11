"""Todo server-rendered app with Litestar, Jinja templates, and in-memory storage."""

from pathlib import Path

from litestar import Litestar, Request, get, post
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.exceptions import NotFoundException
from litestar.response import Redirect, Template
from litestar.template.config import TemplateConfig

from .repository import InMemoryTodoRepository

TEMPLATES_DIR = Path(__file__).parent / "templates"

ERROR_EMPTY_TITLE = "Title must not be empty"


def _repo(request: Request) -> InMemoryTodoRepository:
    return request.app.state["repo"]


def _list_context(repo: InMemoryTodoRepository, error: str | None = None) -> dict:
    return {"todos": repo.list(), "error": error}


@get("/")
async def index(request: Request) -> Template:
    return Template(template_name="index.html", context=_list_context(_repo(request)))


@post("/todos")
async def add_todo(request: Request) -> Redirect | Template:
    repo = _repo(request)
    form = await request.form()
    raw_title = form.get("title")
    title = raw_title.strip() if isinstance(raw_title, str) else ""
    if not title:
        return Template(
            template_name="index.html",
            context=_list_context(repo, error=ERROR_EMPTY_TITLE),
            status_code=400,
        )
    repo.create(title=title)
    return Redirect(path="/", status_code=303)


@post("/todos/{todo_id:int}/toggle")
async def toggle_todo(request: Request, todo_id: int) -> Redirect:
    try:
        _repo(request).toggle(todo_id)
    except KeyError:
        raise NotFoundException(detail="Todo not found") from None
    return Redirect(path="/", status_code=303)


@post("/todos/{todo_id:int}/delete")
async def delete_todo(request: Request, todo_id: int) -> Redirect:
    try:
        _repo(request).delete(todo_id)
    except KeyError:
        raise NotFoundException(detail="Todo not found") from None
    return Redirect(path="/", status_code=303)


def create_app(repo: InMemoryTodoRepository | None = None) -> Litestar:
    repo = repo or InMemoryTodoRepository()
    return Litestar(
        route_handlers=[index, add_todo, toggle_todo, delete_todo],
        template_config=TemplateConfig(
            directory=TEMPLATES_DIR, engine=JinjaTemplateEngine
        ),
        state={"repo": repo},
    )


app = create_app()
