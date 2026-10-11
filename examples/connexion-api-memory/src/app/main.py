"""Todo JSON API with Connexion 3.x (OpenAPI-first) and in-memory storage."""

from __future__ import annotations

from pathlib import Path

from connexion import AsyncApp, problem
from connexion.exceptions import BadRequestProblem

from . import handlers
from .repository import InMemoryTodoRepository

SPEC_DIR = Path(__file__).resolve().parent


def _validation_error(request: object, exc: Exception) -> object:
    """Remap spec request-validation failures (400) to the contract's 422."""
    detail = getattr(exc, "detail", None) or "Request validation failed."
    return problem(status=422, title="Unprocessable Entity", detail=str(detail))


def create_app(repo: InMemoryTodoRepository | None = None) -> AsyncApp:
    """Build an app with a fresh in-memory store (or the given repository)."""
    handlers.use_store(repo or InMemoryTodoRepository())
    app = AsyncApp(__name__, specification_dir=str(SPEC_DIR))
    app.add_api("openapi.yaml")
    app.add_error_handler(BadRequestProblem, _validation_error)
    return app


app = create_app()


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
