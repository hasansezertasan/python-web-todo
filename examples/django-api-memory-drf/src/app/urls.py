from django.urls import path

from .views import TodoDetailView, TodoListCreateView

urlpatterns = [
    path("todos", TodoListCreateView.as_view(), name="todo-list-create"),
    path("todos/<int:todo_id>", TodoDetailView.as_view(), name="todo-detail"),
]
