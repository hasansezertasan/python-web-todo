"""Jinja2 environment for Django's built-in Jinja2 backend.

Django's Jinja2 backend has no ``{% url %}`` tag, so this exposes URL
reversing as the ``url`` global: ``{{ url('todo-toggle', args=[todo.id]) }}``.
"""

from django.urls import reverse
from jinja2 import Environment


def environment(**options) -> Environment:
    options.setdefault("autoescape", True)
    env = Environment(**options)  # noqa: S701 — Django supplies autoescape; default secured above
    env.globals.update({"url": reverse})
    return env
