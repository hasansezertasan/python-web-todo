"""URL routes for the todo JSON API (no trailing slashes, per contract)."""

from django.urls import path, re_path

from . import views

urlpatterns = [
    path("todos", views.TodoListCreateView.as_view()),
    path("todos/<int:pk>", views.TodoDetailView.as_view()),
    # Non-integer ids (e.g. /todos/abc) and anything else: JSON 404, not HTML.
    re_path(r"^todos/.*$", views.json_404),
    re_path(r"^.*$", views.json_404),
]
