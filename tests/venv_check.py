"""Run API checks inside examples' OWN venvs (repo root).

Usage: ``uv run python tests/venv_check.py <example> [...]``

For frameworks that cannot live in the shared root venv (dependency pins)
or need their own test client, checks execute via ``uv run --project`` in
the example's own pinned environment. Extra test-only packages that are
not example dependencies come via ``--with``.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

WITH = {
    "blacksheep-api-memory": ["starlette", "httpx"],
    "responder-api-memory": ["starlette", "httpx"],
    "view-api-memory": ["starlette", "httpx"],
    "sanic-api-memory": ["sanic-testing"],
    "bottle-api-memory": ["webtest"],
    "cherrypy-api-memory": ["webtest"],
    "pycnic-api-memory": ["webtest"],
    "morepath-api-memory": ["webtest"],
    "pyramid-ssr-memory": ["webtest"],
    "turbogears-ssr-memory": ["webtest"],
    "quixote-api-memory": ["webtest"],
    "wheezy-web-api-memory": ["webtest"],
}


def main() -> int:
    failed = []
    for example in sys.argv[1:]:
        cmd = ["uv", "run", "--project", f"examples/{example}"]
        for dep in WITH.get(example, []):
            cmd += ["--with", dep]
        cmd += ["python", "tests/_in_venv.py", example]
        print(f"== {example}: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=ROOT)
        if result.returncode != 0:
            failed.append(example)
    if failed:
        print(f"FAILED: {', '.join(failed)}")
        return 1
    print("all venv checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
