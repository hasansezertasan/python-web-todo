"""Views for the server-rendered todo flows."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from .store import store


def todo_list(request: HttpRequest) -> HttpResponse:
    return render(request, "todos/index.html", {"todos": store.list()})


def todo_add(request: HttpRequest) -> HttpResponse:
    if request.method != "POST":
        return redirect("todo-list")
    title = (request.POST.get("title") or "").strip()
    if not title:
        return render(
            request,
            "todos/index.html",
            {"todos": store.list(), "error": "Title must not be empty"},
        )
    store.create(title=title)
    return redirect("todo-list")


def todo_toggle(request: HttpRequest, todo_id: int) -> HttpResponse:
    if request.method != "POST":
        return redirect("todo-list")
    try:
        store.toggle(todo_id)
    except KeyError:
        return HttpResponse("Todo not found", status=404)
    return redirect("todo-list")


def todo_delete(request: HttpRequest, todo_id: int) -> HttpResponse:
    if request.method != "POST":
        return redirect("todo-list")
    try:
        store.delete(todo_id)
    except KeyError:
        return HttpResponse("Todo not found", status=404)
    return redirect("todo-list")
