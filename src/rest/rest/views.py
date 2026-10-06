import logging
import os

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .repository import TodoRepository

logger = logging.getLogger(__name__)

mongo_uri = 'mongodb://' + os.environ["MONGO_HOST"] + ':' + os.environ["MONGO_PORT"]
db = MongoClient(mongo_uri)['test_db']

MAX_DESCRIPTION_LENGTH = 200


class TodoListView(APIView):
    repository = TodoRepository(db)

    def get(self, request):
        try:
            return Response(self.repository.list_all(), status=status.HTTP_200_OK)
        except PyMongoError:
            logger.exception("Failed to fetch todos")
            return self._db_error()

    def post(self, request):
        description = request.data.get('description')
        error = self._validate(description)
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            todo = self.repository.create(description.strip())
        except PyMongoError:
            logger.exception("Failed to create todo")
            return self._db_error()
        return Response(todo, status=status.HTTP_201_CREATED)

    @staticmethod
    def _validate(description):
        if not isinstance(description, str) or not description.strip():
            return 'description is required.'
        if len(description.strip()) > MAX_DESCRIPTION_LENGTH:
            return f'description must be at most {MAX_DESCRIPTION_LENGTH} characters.'
        return None

    @staticmethod
    def _db_error():
        return Response({'error': 'Database unavailable.'},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE)
