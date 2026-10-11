"""DRF views for the Todo JSON API (in-memory store, no ORM)."""

from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
)
from rest_framework.views import APIView

from . import repository
from .serializers import TodoCreateSerializer, TodoReadSerializer, TodoUpdateSerializer

NOT_FOUND = {"error": "Todo not found"}


class TodoListCreateView(APIView):
    def get(self, request):
        data = TodoReadSerializer(repository.store.list(), many=True).data
        return Response(data, status=HTTP_200_OK)

    def post(self, request):
        serializer = TodoCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=HTTP_422_UNPROCESSABLE_ENTITY)
        validated = serializer.validated_data
        todo = repository.store.create(title=validated["title"])
        if validated.get("done", False):
            todo = repository.store.update(todo.id, done=True)
        return Response(TodoReadSerializer(todo).data, status=HTTP_201_CREATED)


class TodoDetailView(APIView):
    def get(self, request, todo_id: int):
        try:
            todo = repository.store.get(todo_id)
        except KeyError:
            return Response(NOT_FOUND, status=HTTP_404_NOT_FOUND)
        return Response(TodoReadSerializer(todo).data, status=HTTP_200_OK)

    def patch(self, request, todo_id: int):
        try:
            repository.store.get(todo_id)
        except KeyError:
            return Response(NOT_FOUND, status=HTTP_404_NOT_FOUND)
        serializer = TodoUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=HTTP_422_UNPROCESSABLE_ENTITY)
        validated = serializer.validated_data
        todo = repository.store.update(
            todo_id, title=validated.get("title"), done=validated.get("done")
        )
        return Response(TodoReadSerializer(todo).data, status=HTTP_200_OK)

    def delete(self, request, todo_id: int):
        try:
            repository.store.delete(todo_id)
        except KeyError:
            return Response(NOT_FOUND, status=HTTP_404_NOT_FOUND)
        return Response(status=HTTP_204_NO_CONTENT)
