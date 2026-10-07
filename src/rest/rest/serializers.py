from rest_framework import serializers

MAX_DESCRIPTION_LENGTH = 200
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 100


class TodoInputSerializer(serializers.Serializer):
    """Validates the body of POST /todos. Surrounding whitespace is trimmed."""
    description = serializers.CharField(max_length=MAX_DESCRIPTION_LENGTH)


class PaginationSerializer(serializers.Serializer):
    """Validates the query params of GET /todos."""
    limit = serializers.IntegerField(min_value=1, max_value=MAX_PAGE_SIZE, default=DEFAULT_PAGE_SIZE)
    offset = serializers.IntegerField(min_value=0, default=0)
