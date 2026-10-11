"""DRF serializers for Todo items."""

from rest_framework import serializers

from .models import Todo


class TodoSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True, allow_blank=False, max_length=500)

    class Meta:
        model = Todo
        fields = ["id", "title", "done"]
        read_only_fields = ["id"]
        extra_kwargs = {"done": {"required": False}}

    def validate_title(self, value: str) -> str:
        title = value.strip()
        if not title:
            raise serializers.ValidationError("Title must be a non-empty string.")
        return title
