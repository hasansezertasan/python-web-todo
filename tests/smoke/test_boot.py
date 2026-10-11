"""Smoke checks: each example boots and serves its listing endpoint."""

import pytest

from conftest import load_client

# (example, probe path, expected status)
SMOKE_TARGETS = [
    ("fastapi-api-memory", "/todos", 200),
    ("flask-api-memory", "/todos", 200),
    ("starlette-api-memory", "/todos", 200),
    ("muffin-api-memory", "/todos", 200),
    ("connexion-api-memory", "/todos", 200),
]


@pytest.mark.parametrize("example,path,expected", SMOKE_TARGETS)
def test_example_serves(example, path, expected):
    assert load_client(example).get(path).status_code == expected
