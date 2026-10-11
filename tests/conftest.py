import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Any, Self

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"


_FACTORIES: dict[str, Any] = {}


def _safe_name(example: str) -> str:
    return "examples_" + example.replace("-", "_")


def load_app_factory(example: str) -> Any:
    """Import `create_app` from a flat example folder.

    Every factory-based example keeps its code under `src/` and ships its
    own `app` package. Packages load under a unique synthetic name per
    example (``examples_<example>.app...``), so identically-named modules
    from different examples never shadow each other in `sys.modules` —
    which matters for frameworks resolving handlers or type hints by
    module name. Factories are imported once per example; fresh state per
    test comes from calling the factory, not from re-importing it.

    Exception: connexion resolves `operationId`s like ``app.handlers.x``
    with a plain absolute import at app-build time, so its `src/` stays on
    `sys.path` and its `app` package keeps its natural top-level name.
    """
    if example not in _FACTORIES:
        if example == "connexion-api-memory":
            src = str(EXAMPLES_DIR / example / "src")
            sys.path.insert(0, src)
            from app.main import create_app

            _FACTORIES[example] = create_app
        else:
            safe = _safe_name(example)
            spec = importlib.util.spec_from_loader(safe, loader=None, origin="examples")
            package = importlib.util.module_from_spec(spec)
            package.__path__ = [str(EXAMPLES_DIR / example / "src")]
            sys.modules[safe] = package
            main = importlib.import_module(f"{safe}.app.main")
            _FACTORIES[example] = main.create_app
    return _FACTORIES[example]


def client_kwargs(example: str, tmp_path: Path) -> dict[str, str]:
    """Extra factory kwargs per example (storage isolation for SQLite)."""
    if example == "litestar-api-sqlite-advanced-alchemy":
        # File DB per test: :memory: does not survive across async connections.
        return {"db_url": f"sqlite+aiosqlite:///{tmp_path}/todos.db"}
    if example in ("fastapi-api-sqlite-sqlalchemy", "flask-api-sqlite-sqlalchemy"):
        return {"db_url": "sqlite:///:memory:"}
    return {}


class _Response:
    """Uniform test response: status_code + json()/text/headers."""

    def __init__(
        self,
        status_code: int,
        payload: Any = None,
        text: str = "",
        headers: dict | None = None,
    ) -> None:
        self.status_code = status_code
        self._payload = payload
        self._text = text
        self.headers = headers or {}

    def json(self) -> Any:
        return self._payload

    @property
    def text(self) -> str:
        return self._text


class _FlaskClient:
    """Wrap a Flask test client to match the get/post/patch/delete shape."""

    def __init__(self, raw: Any) -> None:
        self._raw = raw

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> bool:
        return False

    def _call(self, method: str, path: str, **kwargs: Any) -> _Response:
        response = getattr(self._raw, method)(path, **kwargs)
        return _Response(
            response.status_code,
            response.get_json(silent=True),
            response.get_data(as_text=True),
            dict(response.headers),
        )

    def get(self, path: str, **kwargs: Any) -> _Response:
        return self._call("get", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> _Response:
        return self._call("post", path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> _Response:
        return self._call("patch", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> _Response:
        return self._call("delete", path, **kwargs)


def load_client(example: str, **kwargs: Any) -> Any:
    """Build a uniform test client for a factory-based example."""
    app = load_app_factory(example)(**kwargs)
    module = type(app).__module__.split(".")[0]
    if module == "flask":
        return _FlaskClient(app.test_client())
    if module == "litestar":
        from litestar.testing import TestClient as LitestarTestClient

        return LitestarTestClient(app=app)

    from fastapi.testclient import TestClient

    return TestClient(app)
