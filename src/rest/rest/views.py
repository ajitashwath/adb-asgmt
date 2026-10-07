import logging
import os

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .repository import TodoRepository
from .serializers import PaginationSerializer, TodoInputSerializer

logger = logging.getLogger(__name__)

mongo_uri = 'mongodb://' + os.environ["MONGO_HOST"] + ':' + os.environ["MONGO_PORT"]
db = MongoClient(mongo_uri)['test_db']

class TodoListView(APIView):
    repository = TodoRepository(db)

    def get(self, request):
        params = PaginationSerializer(data=request.query_params)
        if not params.is_valid():
            return self._validation_error(params)

        try:
            todos = self.repository.list_all(**params.validated_data)
        except PyMongoError:
            logger.exception("Failed to fetch todos")
            return self._db_error()
        return Response(todos, status=status.HTTP_200_OK)

    def post(self, request):
        body = TodoInputSerializer(data=request.data)
        if not body.is_valid():
            return self._validation_error(body)

        try:
            todo = self.repository.create(body.validated_data['description'])
        except PyMongoError:
            logger.exception("Failed to create todo")
            return self._db_error()
        return Response(todo, status=status.HTTP_201_CREATED)

    @staticmethod
    def _validation_error(serializer):
        """Report the first validation error as {"error": "<field>: <message>"}."""
        field, messages = next(iter(serializer.errors.items()))
        return Response({'error': f'{field}: {messages[0]}'}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def _db_error():
        return Response({'error': 'Database unavailable.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
