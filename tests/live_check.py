"""Boot live servers on ephemeral ports and run API checks over real HTTP.

Usage (repo root): ``uv run python tests/live_check.py <example> [...]``

For standalone frameworks with no usable in-process test client. Each
example must honor the ``PORT`` env var (see skills/new-example). Fresh
state comes from the fresh server process per example.
"""

import json
import os
import socket
import subprocess
import sys
import time
import traceback
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests" / "contracts"))

from checks_api import (  # noqa: E402
    check_crud_flow,
    check_list_starts_empty,
    check_openapi,
    check_unknown_id,
    check_validation_errors,
)

CHECKS = [
    check_list_starts_empty,
    check_crud_flow,
    check_validation_errors,
    check_unknown_id,
]

LIVE = {
    "tornado-api-memory": {"argv": ["python", "-m", "app.main"]},
    "twisted-api-memory": {"argv": ["python", "-m", "app.main"]},
    "robyn-api-memory": {
        "argv": ["python", "-m", "app.main"],
        "openapi": ("/openapi.json", "/todos/{id}"),
    },
    "rsgi-api-memory": {"argv": ["python", "-m", "app.main"]},
    "socketify-api-memory": {"argv": ["python", "-m", "app.main"]},
    "tremolo-api-memory": {"argv": ["python", "-m", "app.main"]},
    "lona-api-memory": {"argv": ["python", "-m", "app.main"]},
    "baize-api-memory": {"argv": ["python", "-m", "app.main"]},
    "circuits-api-memory": {"argv": ["python", "-m", "app.main"]},
    "klein-api-memory": {"argv": ["python", "-m", "app.main"]},
}


class R:
    def __init__(self, status_code, payload, text=""):
        self.status_code = status_code
        self._payload = payload
        self._text = text

    def json(self):
        return self._payload

    @property
    def text(self):
        return self._text


class HttpClient:
    def __init__(self, base):
        self._base = base

    def _request(self, method, path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        request = urllib.request.Request(
            self._base + path,
            data=data,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                raw = response.read().decode()
                status = response.status
        except urllib.error.HTTPError as error:
            raw = error.read().decode()
            status = error.code
        try:
            payload = json.loads(raw) if raw else None
        except ValueError:
            payload = None
        return R(status, payload, raw)

    def get(self, path, **kwargs):
        return self._request("GET", path)

    def post(self, path, json=None, **kwargs):
        return self._request("POST", path, body=json)

    def patch(self, path, json=None, **kwargs):
        return self._request("PATCH", path, body=json)

    def delete(self, path, **kwargs):
        return self._request("DELETE", path)


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _wait_ready(base: str, timeout: float = 30.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(base + "/todos", timeout=2) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.5)
    message = f"server at {base} never became ready"
    raise RuntimeError(message)


def check_example(example: str) -> int:
    spec = LIVE[example]
    port = _free_port()
    env = dict(os.environ, PORT=str(port))
    env.pop("ROBYN_PORT", None)
    cmd = ["uv", "run", "--project", f"examples/{example}", *spec["argv"]]
    print(f"== {example}: PORT={port} {' '.join(cmd)}")
    process = subprocess.Popen(
        cmd,
        cwd=ROOT,
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    failures = 0
    try:
        _wait_ready(f"http://127.0.0.1:{port}")
        client = HttpClient(f"http://127.0.0.1:{port}")
        for check in CHECKS:
            try:
                check(client)
            except AssertionError:
                failures += 1
                print(f"FAIL {example}::{check.__name__}")
                traceback.print_exc()
            else:
                print(f"ok {example}::{check.__name__}")
        if "openapi" in spec:
            schema_path, item_path = spec["openapi"]
            try:
                check_openapi(client, schema_path, item_path)
            except AssertionError:
                failures += 1
                print(f"FAIL {example}::check_openapi")
                traceback.print_exc()
            else:
                print(f"ok {example}::check_openapi")
    except RuntimeError as error:
        failures += 1
        print(f"FAIL {example}::boot: {error}")
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)
    total = len(CHECKS) + ("openapi" in spec)
    print(f"{example}: {total - failures}/{total} checks passed")
    return 1 if failures else 0


def main() -> int:
    failed = [ex for ex in sys.argv[1:] if check_example(ex)]
    if failed:
        print(f"FAILED: {', '.join(failed)}")
        return 1
    print("all live checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
