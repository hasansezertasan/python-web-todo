"""URL configuration for the todos app."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.todo_list, name="todo-list"),
    path("todos", views.todo_add, name="todo-add"),
    path("todos/<int:todo_id>/toggle", views.todo_toggle, name="todo-toggle"),
    path("todos/<int:todo_id>/delete", views.todo_delete, name="todo-delete"),
]
