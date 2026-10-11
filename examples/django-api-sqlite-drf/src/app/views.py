"""DRF views for the todo JSON API."""

from typing import Any

from django.http import HttpRequest, JsonResponse
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from .models import Todo
from .serializers import TodoSerializer


def api_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """Map serializer validation 400s to the contract's 422 + JSON body."""
    response = drf_exception_handler(exc, context)
    if response is not None and response.status_code == status.HTTP_400_BAD_REQUEST:
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    return response


class TodoListCreateView(generics.ListCreateAPIView):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer


class TodoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer


def json_404(request: HttpRequest, exception: Exception | None = None) -> JsonResponse:
    """JSON 404 for unknown paths / non-integer ids (contract needs a body)."""
    return JsonResponse({"detail": "Not found."}, status=404)
