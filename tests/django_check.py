"""Per-example Django contract runner: one Django settings module per process.

Usage (from the repo root): ``uv run python tests/django_check.py <example>``

Runs the API or SSR checks (picked from the example name) with a fresh
Django setup and exits nonzero on the first failure. Factory-based
examples are covered by pytest instead; Django examples need their own
process because each ships its own settings module.
"""

import json
import sys
import tempfile
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = sys.argv[1]
KIND = "api" if "-api-" in EXAMPLE else "ssr"

sys.path.insert(0, str(ROOT / "examples" / EXAMPLE / "src"))
sys.path.insert(0, str(ROOT / "tests" / "contracts"))

if EXAMPLE == "django-api-sqlite-drf":
    tmp = tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False)
    tmp.close()
    DB_PATH = tmp.name
    from app.main import create_app

    create_app(db_path=DB_PATH)
else:
    import os

    SETTINGS = {
        "django-ssr-memory-native": "config.settings",
        "django-ssr-memory-jinja": "config.settings",
        "django-api-memory-drf": "app.settings",
    }[EXAMPLE]
    os.environ["DJANGO_SETTINGS_MODULE"] = SETTINGS
    import django

    django.setup()

from django.test import Client  # noqa: E402

if KIND == "api":
    from checks_api import (  # noqa: E402
        check_crud_flow,
        check_list_starts_empty,
        check_unknown_id,
        check_validation_errors,
    )

    CHECKS = [
        check_list_starts_empty,
        check_crud_flow,
        check_validation_errors,
        check_unknown_id,
    ]
else:
    from checks_ssr import (  # noqa: E402
        check_add_flow,
        check_delete_flow,
        check_empty_title_rejected,
        check_list_page,
        check_toggle_flow,
        check_unknown_id,
    )

    CHECKS = [
        check_list_page,
        check_add_flow,
        check_toggle_flow,
        check_delete_flow,
        check_empty_title_rejected,
        check_unknown_id,
    ]


class _Response:
    def __init__(self, raw):
        self.status_code = raw.status_code
        self._raw = raw
        self.headers = dict(raw.headers)

    def json(self):
        try:
            return json.loads(self._raw.content.decode())
        except ValueError:
            return None

    @property
    def text(self):
        return self._raw.content.decode()


class DjangoClient:
    """Uniform adapter over django.test.Client (form data= or json= posts)."""

    def __init__(self, raw):
        self._raw = raw

    def get(self, path, **kwargs):
        return _Response(self._raw.get(path, **kwargs))

    def _write(self, method, path, json_body=None, **kwargs):
        if json_body is not None:
            kwargs.setdefault("content_type", "application/json")
            return _Response(
                getattr(self._raw, method)(path, data=json.dumps(json_body), **kwargs)
            )
        return _Response(getattr(self._raw, method)(path, **kwargs))

    def post(self, path, json=None, **kwargs):  # noqa: A002
        return self._write("post", path, json_body=json, **kwargs)

    def patch(self, path, json=None, **kwargs):  # noqa: A002
        return self._write("patch", path, json_body=json, **kwargs)

    def delete(self, path, **kwargs):
        return _Response(self._raw.delete(path, **kwargs))


if EXAMPLE in ("django-ssr-memory-native", "django-ssr-memory-jinja"):
    from todos.store import reset_store  # noqa: E402

    def reset():
        reset_store()
elif EXAMPLE == "django-api-memory-drf":
    from app.repository import reset_store  # noqa: E402

    def reset():
        reset_store()
else:

    def reset():
        from app.models import Todo  # noqa: E402
        from django.db import connection  # noqa: E402

        Todo.objects.all().delete()
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM sqlite_sequence WHERE name=%s", [Todo._meta.db_table]
            )


def main() -> int:
    client = DjangoClient(Client())
    failures = 0
    for check in CHECKS:
        reset()
        try:
            check(client)
        except AssertionError:
            failures += 1
            print(f"FAIL {EXAMPLE}::{check.__name__}")
            traceback.print_exc()
        else:
            print(f"ok {EXAMPLE}::{check.__name__}")
    print(f"{EXAMPLE}: {len(CHECKS) - failures}/{len(CHECKS)} checks passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
