"""Todo JSON API with Lona and in-memory storage.

Lona is an aiohttp-based full-stack framework. Plain JSON endpoints use its
idiomatic escape hatch: ``http_pass_through`` views, where ``handle_request``
receives the raw aiohttp request and may return ``lona.responses.JsonResponse``
(or a raw aiohttp response, which the server passes through untouched).
"""

import os

from aiohttp.web import Response as AiohttpResponse
from lona import MATCH_ALL, App as LonaApp, JsonResponse, View

from .models import todo_to_dict
from .repository import InMemoryTodoRepository


def _not_found() -> JsonResponse:
    return JsonResponse(data={"detail": "Todo not found"}, status=404)


def _invalid_title() -> JsonResponse:
    return JsonResponse(
        data={"detail": "title must be a non-empty string"}, status=422
    )


def _method_not_allowed() -> JsonResponse:
    return JsonResponse(data={"detail": "Method not allowed"}, status=405)


def _parse_id(raw: str) -> int | None:
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


async def _read_json(request) -> object:
    try:
        return await request.json()
    except Exception:
        return None


def create_app(repo: InMemoryTodoRepository | None = None) -> LonaApp:
    """Build a fresh Lona app with its own empty in-memory store."""
    repo = repo or InMemoryTodoRepository()
    app = LonaApp(__file__)

    @app.route("/todos", http_pass_through=True)
    class TodoCollectionView(View):
        async def handle_request(self, request):
            if request.method == "GET":
                return JsonResponse(
                    data=[todo_to_dict(todo) for todo in repo.list()]
                )

            if request.method == "POST":
                body = await _read_json(request)
                title = body.get("title") if isinstance(body, dict) else None
                if not isinstance(title, str) or not title.strip():
                    return _invalid_title()
                todo = repo.create(title=title)
                return JsonResponse(data=todo_to_dict(todo), status=201)

            return _method_not_allowed()

    @app.route("/todos/<todo_id>", http_pass_through=True)
    class TodoItemView(View):
        async def handle_request(self, request):
            # Lona's router matches the path but the raw aiohttp request
            # carries no route params, so the id is parsed off the path.
            todo_id = _parse_id(request.path.rsplit("/", 1)[-1])
            if todo_id is None:
                return _not_found()

            if request.method == "GET":
                try:
                    todo = repo.get(todo_id)
                except KeyError:
                    return _not_found()
                return JsonResponse(data=todo_to_dict(todo))

            if request.method == "PATCH":
                body = await _read_json(request)
                if not isinstance(body, dict):
                    return _invalid_title()
                title = body.get("title")
                done = body.get("done")
                if title is not None and (
                    not isinstance(title, str) or not title.strip()
                ):
                    return _invalid_title()
                if done is not None and not isinstance(done, bool):
                    return JsonResponse(
                        data={"detail": "done must be a boolean"}, status=422
                    )
                try:
                    todo = repo.update(todo_id, title=title, done=done)
                except KeyError:
                    return _not_found()
                return JsonResponse(data=todo_to_dict(todo))

            if request.method == "DELETE":
                try:
                    repo.delete(todo_id)
                except KeyError:
                    return _not_found()
                return AiohttpResponse(status=204)

            return _method_not_allowed()

    @app.route(MATCH_ALL, http_pass_through=True)
    class FallbackView(View):
        async def handle_request(self, request):
            return JsonResponse(data={"detail": "Not found"}, status=404)

    return app


app = create_app()


def main() -> None:
    import asyncio

    # Lona's runner calls asyncio.get_event_loop(), which raises on Python
    # 3.14 with no current loop; provide one explicitly before handing over.
    asyncio.set_event_loop(asyncio.new_event_loop())

    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, parse_command_line=False)


if __name__ == "__main__":
    main()
