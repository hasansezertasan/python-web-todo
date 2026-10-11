"""Contract checks executed inside an example's OWN venv.

Run via tests/venv_check.py (repo root), which invokes this file with
``uv run --project`` so the example's own pinned environment applies.
Imports the shared pure-python checks; only the client construction is
framework-specific. Each check gets a fresh app.
"""

import json
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = sys.argv[1]
sys.path.insert(0, str(ROOT / "tests" / "contracts"))

from app.main import create_app  # noqa: E402  (the example's installed package)
from checks_api import (  # noqa: E402
    check_crud_flow,
    check_list_starts_empty,
    check_openapi,
    check_unknown_id,
    check_validation_errors,
)
from checks_ssr import (  # noqa: E402
    check_add_flow,
    check_delete_flow,
    check_empty_title_rejected,
    check_list_page,
    check_toggle_flow,
)
from checks_ssr import (  # noqa: E402
    check_unknown_id as check_ssr_unknown_id,
)

CHECKS = [
    check_list_starts_empty,
    check_crud_flow,
    check_validation_errors,
    check_unknown_id,
]
SSR_CHECKS = [
    check_list_page,
    check_add_flow,
    check_toggle_flow,
    check_delete_flow,
    check_empty_title_rejected,
    check_ssr_unknown_id,
]
OPENAPI = {"blacksheep-api-memory": "/openapi.json", "flama-api-memory": "/schema/"}


class R:
    """Uniform response: status_code + json()/text."""

    def __init__(self, status_code, payload, text=""):
        self.status_code = status_code
        self._payload = payload
        self._text = text

    def json(self):
        return self._payload

    @property
    def text(self):
        return self._text


def _payload(response):
    """Best-effort parsed body across client shapes (.json method or property)."""
    try:
        candidate = response.json
    except Exception:
        return None
    try:
        return candidate() if callable(candidate) else candidate
    except Exception:
        return None


def _text(response):
    text = getattr(response, "text", "")
    return text() if callable(text) else (text or "")


class SanicClient:
    """sanic-testing sync client returns (request, response) tuples."""

    def __init__(self, app):
        self._client = app.test_client

    def _call(self, method, path, **kwargs):
        _, response = getattr(self._client, method)(path, **kwargs)
        return R(response.status, _payload(response), _text(response))

    def get(self, path, **kwargs):
        return self._call("get", path, **kwargs)

    def post(self, path, **kwargs):
        return self._call("post", path, **kwargs)

    def patch(self, path, **kwargs):
        return self._call("patch", path, **kwargs)

    def delete(self, path, **kwargs):
        return self._call("delete", path, **kwargs)


class FalconClient:
    """falcon.testing.TestClient speaks simulate_*."""

    def __init__(self, app):
        from falcon import testing as falcon_testing

        self._client = falcon_testing.TestClient(app)

    def _call(self, method, path, **kwargs):
        response = getattr(self._client, f"simulate_{method}")(path, **kwargs)
        return R(response.status_code, _payload(response), _text(response))

    def get(self, path, **kwargs):
        return self._call("get", path, **kwargs)

    def post(self, path, **kwargs):
        return self._call("post", path, **kwargs)

    def patch(self, path, **kwargs):
        return self._call("patch", path, **kwargs)

    def delete(self, path, **kwargs):
        return self._call("delete", path, **kwargs)


class WebTestClient:
    """webtest.TestApp; status='*' accepts error statuses without raising."""

    def __init__(self, app):
        from webtest import TestApp

        self._client = TestApp(app)

    def get(self, path, **kwargs):
        response = self._client.get(path, status="*", **kwargs)
        return R(response.status_int, _payload(response), response.text)

    def post(self, path, json=None, data=None, **kwargs):
        if data is not None:
            response = self._client.post(path, params=data, status="*", **kwargs)
        else:
            response = self._client.post_json(path, json, status="*", **kwargs)
        return R(response.status_int, _payload(response), response.text)

    def patch(self, path, json=None, data=None, **kwargs):
        if data is not None:
            response = self._client.patch(path, params=data, status="*", **kwargs)
        else:
            response = self._client.patch_json(path, json, status="*", **kwargs)
        return R(response.status_int, _payload(response), response.text)

    def delete(self, path, **kwargs):
        response = self._client.delete(path, status="*", **kwargs)
        return R(response.status_int, _payload(response), response.text)


BottleClient = WebTestClient


class ClasticClient:
    """Clastic's own local client (proper Response objects)."""

    def __init__(self, app):
        self._client = app.get_local_client()

    def _call(self, method, path, **kwargs):
        response = getattr(self._client, method)(path, **kwargs)
        try:
            payload = json.loads(response.get_data(as_text=True) or "null")
        except ValueError:
            payload = None
        return R(response.status_code, payload, response.get_data(as_text=True))

    def get(self, path, **kwargs):
        return self._call("get", path, **kwargs)

    def post(self, path, **kwargs):
        return self._call("post", path, **kwargs)

    def patch(self, path, **kwargs):
        return self._call("patch", path, **kwargs)

    def delete(self, path, **kwargs):
        return self._call("delete", path, **kwargs)


class StarletteClient:
    """Sync Starlette TestClient without lifespan (e.g. BlackSheep's ASGI app)."""

    def __init__(self, app):
        from starlette.testclient import TestClient

        self._client = TestClient(app, raise_server_exceptions=False)

    def _call(self, method, path, **kwargs):
        response = getattr(self._client, method)(path, **kwargs)
        return R(response.status_code, _payload(response), response.text)

    def get(self, path, **kwargs):
        return self._call("get", path, **kwargs)

    def post(self, path, **kwargs):
        return self._call("post", path, **kwargs)

    def patch(self, path, **kwargs):
        return self._call("patch", path, **kwargs)

    def delete(self, path, **kwargs):
        return self._call("delete", path, **kwargs)


class QuartClient:
    """Quart's async test client (every call awaits)."""

    def __init__(self, app):
        self._client = app.test_client()

    async def _call(self, method, path, **kwargs):
        response = await getattr(self._client, method)(path, **kwargs)
        return R(response.status_code, await response.get_json())

    async def get(self, path, **kwargs):
        return await self._call("get", path, **kwargs)

    async def post(self, path, **kwargs):
        return await self._call("post", path, **kwargs)

    async def patch(self, path, **kwargs):
        return await self._call("patch", path, **kwargs)

    async def delete(self, path, **kwargs):
        return await self._call("delete", path, **kwargs)


class AiohttpClient:
    """aiohttp TestClient/TestServer; started and closed per check."""

    def __init__(self, raw):
        self._raw = raw

    async def _call(self, method, path, **kwargs):
        response = await getattr(self._raw, method)(path, **kwargs)
        try:
            payload = await response.json()
        except Exception:
            payload = None
        return R(response.status, payload, await response.text())

    async def get(self, path, **kwargs):
        return await self._call("get", path, **kwargs)

    async def post(self, path, **kwargs):
        return await self._call("post", path, **kwargs)

    async def patch(self, path, **kwargs):
        return await self._call("patch", path, **kwargs)

    async def delete(self, path, **kwargs):
        return await self._call("delete", path, **kwargs)


async def acheck_list_starts_empty(client):
    response = await client.get("/todos")
    assert response.status_code == 200, response.status_code
    assert response.json() == []


async def acheck_crud_flow(client):
    created = await client.post("/todos", json={"title": "Buy milk"})
    assert created.status_code == 201, created.status_code
    item = created.json()
    assert item["title"] == "Buy milk"
    assert item["done"] is False

    todo_id = item["id"]
    assert (await client.get(f"/todos/{todo_id}")).json() == item

    updated = await client.patch(f"/todos/{todo_id}", json={"done": True})
    assert updated.status_code == 200, updated.status_code
    assert updated.json()["done"] is True

    assert (await client.delete(f"/todos/{todo_id}")).status_code == 204
    assert (await client.get(f"/todos/{todo_id}")).status_code == 404


async def acheck_validation_errors(client):
    for payload in ({"title": ""}, {}):
        response = await client.post("/todos", json=payload)
        assert response.status_code == 422, (payload, response.status_code)
        assert response.json() is not None

    created = (await client.post("/todos", json={"title": "x"})).json()
    bad = await client.patch(f"/todos/{created['id']}", json={"title": ""})
    assert bad.status_code == 422, bad.status_code
    assert bad.json() is not None


async def acheck_unknown_id(client):
    for response in (
        await client.get("/todos/9999"),
        await client.patch("/todos/9999", json={"done": True}),
        await client.delete("/todos/9999"),
    ):
        assert response.status_code == 404, response.status_code
        assert response.json() is not None


ASYNC_CHECKS = [
    acheck_list_starts_empty,
    acheck_crud_flow,
    acheck_validation_errors,
    acheck_unknown_id,
]


class EmmettClient:
    """Emmett's sync test client: .status int, .json() method.

    JSON bodies go as data=json.dumps(...) plus an explicit
    Content-Type header (the content_type kwarg is dropped upstream).
    """

    def __init__(self, app):
        self._client = app.test_client()

    def _call(self, method, path, **kwargs):
        json_body = kwargs.pop("json", None)
        if json_body is not None:
            response = getattr(self._client, method)(
                path,
                data=json.dumps(json_body),
                headers=[("Content-Type", "application/json")],
            )
        else:
            response = getattr(self._client, method)(path, **kwargs)
        try:
            payload = response.json()
        except Exception:
            payload = None
        return R(response.status, payload, response.data)

    def get(self, path, **kwargs):
        return self._call("get", path, **kwargs)

    def post(self, path, **kwargs):
        return self._call("post", path, **kwargs)

    def patch(self, path, **kwargs):
        return self._call("patch", path, **kwargs)

    def delete(self, path, **kwargs):
        return self._call("delete", path, **kwargs)


class FlamaClient:
    """Flama's async client; response reading itself is sync."""

    def __init__(self, raw):
        self._raw = raw

    async def _call(self, method, path, **kwargs):
        response = await getattr(self._raw, method)(path, **kwargs)
        try:
            payload = response.json()
        except Exception:
            payload = None
        return R(response.status_code, payload)

    async def get(self, path, **kwargs):
        return await self._call("get", path, **kwargs)

    async def post(self, path, **kwargs):
        return await self._call("post", path, **kwargs)

    async def patch(self, path, **kwargs):
        return await self._call("patch", path, **kwargs)

    async def delete(self, path, **kwargs):
        return await self._call("delete", path, **kwargs)


BUILDERS = {
    "blacksheep-api-memory": StarletteClient,
    "sanic-api-memory": SanicClient,
    "falcon-api-memory": FalconClient,
    "bottle-api-memory": WebTestClient,
    "clastic-api-memory": ClasticClient,
    "cherrypy-api-memory": WebTestClient,
    "pycnic-api-memory": WebTestClient,
    "morepath-api-memory": WebTestClient,
    "pyramid-ssr-memory": WebTestClient,
    "turbogears-ssr-memory": WebTestClient,
    "quixote-api-memory": WebTestClient,
    "wheezy-web-api-memory": WebTestClient,
    "responder-api-memory": StarletteClient,
    "view-api-memory": StarletteClient,
    "emmett-api-memory": EmmettClient,
}
ASYNC_EXAMPLES = {"quart-api-memory", "aiohttp-api-memory", "flama-api-memory"}


def _make_app():
    app = create_app()
    if EXAMPLE == "view-api-memory":
        return app.asgi()
    return app


def _run_sync(build, checks):
    failures = 0
    for check in checks:
        try:
            check(build(_make_app()))
        except AssertionError:
            failures += 1
            print(f"FAIL {EXAMPLE}::{check.__name__}")
            traceback.print_exc()
        else:
            print(f"ok {EXAMPLE}::{check.__name__}")
    return failures, len(checks)


async def _run_async():
    failures = 0
    total = len(ASYNC_CHECKS)
    for check in ASYNC_CHECKS:
        try:
            if EXAMPLE == "aiohttp-api-memory":
                from aiohttp.test_utils import TestClient, TestServer

                raw = TestClient(TestServer(_make_app()))
                await raw.start_server()
                try:
                    await check(AiohttpClient(raw))
                finally:
                    await raw.close()
            elif EXAMPLE == "flama-api-memory":
                from flama.client import Client

                async with Client(app=_make_app()) as raw:
                    await check(FlamaClient(raw))
            else:
                await check(QuartClient(_make_app()))
        except AssertionError:
            failures += 1
            print(f"FAIL {EXAMPLE}::{check.__name__}")
            traceback.print_exc()
        else:
            print(f"ok {EXAMPLE}::{check.__name__}")
    if EXAMPLE in OPENAPI:
        from flama.client import Client

        try:
            async with Client(app=_make_app()) as raw:
                response = await raw.get(OPENAPI[EXAMPLE])
                assert response.status_code == 200, response.status_code
                paths = response.json()["paths"]
                assert "/todos" in paths
                assert "/todos/{todo_id}" in paths
        except AssertionError:
            failures += 1
            print(f"FAIL {EXAMPLE}::check_openapi")
            traceback.print_exc()
        else:
            print(f"ok {EXAMPLE}::check_openapi")
        total += 1
    return failures, total


def main() -> int:
    import asyncio

    if EXAMPLE in ASYNC_EXAMPLES:
        failures, total = asyncio.run(_run_async())
    else:
        build = BUILDERS[EXAMPLE]
        checks = SSR_CHECKS if EXAMPLE.endswith("-ssr-memory") else CHECKS
        failures, total = _run_sync(build, checks)
        if EXAMPLE in OPENAPI:
            try:
                check_openapi(build(_make_app()), OPENAPI[EXAMPLE])
            except AssertionError:
                failures += 1
                print(f"FAIL {EXAMPLE}::check_openapi")
                traceback.print_exc()
            else:
                print(f"ok {EXAMPLE}::check_openapi")
            total += 1
    print(f"{EXAMPLE}: {total - failures}/{total} checks passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
