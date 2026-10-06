from unittest.mock import patch

import mongomock
from pymongo.errors import PyMongoError
from rest_framework.test import APISimpleTestCase, APIClient

from .repository import TodoRepository
from .views import MAX_DESCRIPTION_LENGTH, TodoListView


class TodoRepositoryTests(APISimpleTestCase):
    def setUp(self):
        self.repository = TodoRepository(mongomock.MongoClient()['test_db'])

    def test_create_returns_serialized_todo(self):
        todo = self.repository.create('Learn Docker')
        self.assertEqual(todo['description'], 'Learn Docker')
        self.assertIn('id', todo)
        self.assertIn('created_at', todo)

    def test_list_all_returns_oldest_first(self):
        self.repository.create('first')
        self.repository.create('second')
        descriptions = [t['description'] for t in self.repository.list_all()]
        self.assertEqual(descriptions, ['first', 'second'])

    def test_list_all_is_empty_by_default(self):
        self.assertEqual(self.repository.list_all(), [])


class TodoListViewTests(APISimpleTestCase):
    def setUp(self):
        repository = TodoRepository(mongomock.MongoClient()['test_db'])
        patcher = patch.object(TodoListView, 'repository', repository)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.client = APIClient()

    def test_get_returns_empty_list(self):
        response = self.client.get('/todos')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_post_creates_todo_and_get_returns_it(self):
        response = self.client.post('/todos', {'description': 'Learn React'}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['description'], 'Learn React')

        listed = self.client.get('/todos').json()
        self.assertEqual([t['description'] for t in listed], ['Learn React'])

    def test_post_strips_whitespace(self):
        response = self.client.post('/todos', {'description': '  padded  '}, format='json')
        self.assertEqual(response.json()['description'], 'padded')

    def test_trailing_slash_is_accepted(self):
        response = self.client.post('/todos/', {'description': 'slash'}, format='json')
        self.assertEqual(response.status_code, 201)

    def test_post_rejects_invalid_descriptions(self):
        invalid_payloads = [
            {},
            {'description': ''},
            {'description': '   '},
            {'description': 123},
            {'description': 'x' * (MAX_DESCRIPTION_LENGTH + 1)},
        ]
        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                response = self.client.post('/todos', payload, format='json')
                self.assertEqual(response.status_code, 400)
                self.assertIn('error', response.json())
        self.assertEqual(self.client.get('/todos').json(), [])

    def test_get_returns_503_when_database_fails(self):
        with patch.object(TodoRepository, 'list_all', side_effect=PyMongoError):
            response = self.client.get('/todos')
        self.assertEqual(response.status_code, 503)

    def test_post_returns_503_when_database_fails(self):
        with patch.object(TodoRepository, 'create', side_effect=PyMongoError):
            response = self.client.post('/todos', {'description': 'x'}, format='json')
        self.assertEqual(response.status_code, 503)
