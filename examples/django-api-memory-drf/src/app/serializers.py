"""DRF serializers for the Todo JSON API."""

from rest_framework import serializers


class TodoReadSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField()
    done = serializers.BooleanField()


class TodoCreateSerializer(serializers.Serializer):
    title = serializers.CharField()
    done = serializers.BooleanField(required=False, default=False)

    def validate_title(self, value: object) -> str:
        if not isinstance(value, str) or not value:
            raise serializers.ValidationError("title must be a non-empty string")
        return value


class TodoUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(required=False)
    done = serializers.BooleanField(required=False)

    def validate_title(self, value: object) -> str:
        if not isinstance(value, str) or not value:
            raise serializers.ValidationError("title must be a non-empty string")
        return value
