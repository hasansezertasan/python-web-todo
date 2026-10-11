"""Todo model (Django ORM, SQLite storage)."""

from django.db import models


class Todo(models.Model):
    title = models.CharField(max_length=500)
    done = models.BooleanField(default=False)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return f"Todo(id={self.id}, title={self.title!r}, done={self.done})"
