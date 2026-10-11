"""Server-rendered contract checks (see specs/server-rendered.md)."""

import pytest

from checks_ssr import (
    check_add_flow,
    check_delete_flow,
    check_empty_title_rejected,
    check_list_page,
    check_toggle_flow,
    check_unknown_id,
)
from conftest import load_client

SSR_EXAMPLES = [
    "flask-ssr-memory-jinja",
    "litestar-ssr-memory",
]


@pytest.fixture(params=SSR_EXAMPLES)
def ssr_client(request):
    with load_client(request.param) as client:
        yield client


def test_list_page(ssr_client):
    check_list_page(ssr_client)


def test_add_flow(ssr_client):
    check_add_flow(ssr_client)


def test_toggle_flow(ssr_client):
    check_toggle_flow(ssr_client)


def test_delete_flow(ssr_client):
    check_delete_flow(ssr_client)


def test_empty_title_rejected(ssr_client):
    check_empty_title_rejected(ssr_client)


def test_unknown_id_is_404(ssr_client):
    check_unknown_id(ssr_client)
