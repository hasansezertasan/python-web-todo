"""JSON API contract checks (see specs/json-api.md)."""

import pytest

from checks_api import (
    OPENAPI_PATHS,
    check_crud_flow,
    check_list_starts_empty,
    check_openapi,
    check_unknown_id,
    check_validation_errors,
)
from conftest import client_kwargs, load_client

API_EXAMPLES = [
    "fastapi-api-memory",
    "fastapi-api-sqlite-sqlalchemy",
    "flask-api-memory",
    "flask-api-sqlite-sqlalchemy",
    "litestar-api-memory",
    "litestar-api-sqlite-advanced-alchemy",
    "starlette-api-memory",
    "muffin-api-memory",
    "connexion-api-memory",
]


@pytest.fixture(params=API_EXAMPLES)
def client(request, tmp_path):
    with load_client(request.param, **client_kwargs(request.param, tmp_path)) as c:
        yield c


def test_list_starts_empty(client):
    check_list_starts_empty(client)


def test_crud_flow(client):
    check_crud_flow(client)


def test_validation_errors(client):
    check_validation_errors(client)


def test_unknown_id_is_404_json(client):
    check_unknown_id(client)


@pytest.fixture(params=sorted(OPENAPI_PATHS))
def openapi_case(request, tmp_path):
    name = request.param
    with load_client(name, **client_kwargs(name, tmp_path)) as c:
        yield c, OPENAPI_PATHS[name]


def test_openapi_exposes_todo_operations(openapi_case):
    client, schema_path = openapi_case
    check_openapi(client, schema_path)
