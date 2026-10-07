from unittest.mock import patch

import mongomock
from pymongo.errors import PyMongoError
from rest_framework.test import APISimpleTestCase, APIClient

from .repository import TodoRepository
from .serializers import DEFAULT_PAGE_SIZE, MAX_DESCRIPTION_LENGTH, MAX_PAGE_SIZE
from .views import TodoListView


class TodoRepositoryTests(APISimpleTestCase):
    def setUp(self):
        self.db = mongomock.MongoClient()['test_db']
        self.repository = TodoRepository(self.db)

    def test_create_returns_serialized_todo(self):
        todo = self.repository.create('Learn Docker')
        self.assertEqual(todo['description'], 'Learn Docker')
        self.assertIn('id', todo)
        self.assertTrue(todo['created_at'].endswith('+00:00'))

    def test_list_all_returns_newest_first(self):
        self.repository.create('first')
        self.repository.create('second')
        descriptions = [t['description'] for t in self.repository.list_all(limit=10)]
        self.assertEqual(descriptions, ['second', 'first'])

    def test_list_all_is_empty_by_default(self):
        self.assertEqual(self.repository.list_all(limit=10), [])

    def test_list_all_respects_limit_and_offset(self):
        for name in ['a', 'b', 'c', 'd']:
            self.repository.create(name)  # newest first: d, c, b, a
        page = self.repository.list_all(limit=2, offset=1)
        self.assertEqual([t['description'] for t in page], ['c', 'b'])

    def test_list_all_creates_created_at_index(self):
        self.repository.list_all(limit=1)
        indexed_keys = [list(info['key'])[0][0] for info in self.db.todos.index_information().values()]
        self.assertIn('created_at', indexed_keys)


class TodoListViewTests(APISimpleTestCase):
    def setUp(self):
        repository = TodoRepository(mongomock.MongoClient()['test_db'])
        patcher = patch.object(TodoListView, 'repository', repository)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.client = APIClient()

    def _create(self, description):
        return self.client.post('/todos', {'description': description}, format='json')

    def test_get_returns_empty_list(self):
        response = self.client.get('/todos')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_post_creates_todo_and_get_returns_it(self):
        response = self._create('Learn React')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['description'], 'Learn React')

        listed = self.client.get('/todos').json()
        self.assertEqual([t['description'] for t in listed], ['Learn React'])

    def test_post_strips_whitespace(self):
        self.assertEqual(self._create('  padded  ').json()['description'], 'padded')

    def test_trailing_slash_is_accepted(self):
        response = self.client.post('/todos/', {'description': 'slash'}, format='json')
        self.assertEqual(response.status_code, 201)

    def test_post_rejects_invalid_descriptions(self):
        invalid_payloads = [
            {},
            {'description': ''},
            {'description': '   '},
            {'description': None},
            {'description': ['not', 'a', 'string']},
            {'description': 'x' * (MAX_DESCRIPTION_LENGTH + 1)},
        ]
        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                response = self.client.post('/todos', payload, format='json')
                self.assertEqual(response.status_code, 400)
                self.assertTrue(response.json()['error'].startswith('description:'))
        self.assertEqual(self.client.get('/todos').json(), [])

    def test_post_with_malformed_json_returns_error_key(self):
        response = self.client.post('/todos', 'not json', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_post_accepts_max_length_description(self):
        self.assertEqual(self._create('x' * MAX_DESCRIPTION_LENGTH).status_code, 201)

    def test_get_paginates_with_limit_and_offset(self):
        for i in range(5):
            self._create(f'todo {i}')
        page = self.client.get('/todos', {'limit': 2, 'offset': 1}).json()
        self.assertEqual([t['description'] for t in page], ['todo 3', 'todo 2'])

    def test_get_defaults_to_page_size(self):
        for i in range(DEFAULT_PAGE_SIZE + 1):
            self._create(f'todo {i}')
        self.assertEqual(len(self.client.get('/todos').json()), DEFAULT_PAGE_SIZE)

    def test_get_rejects_invalid_pagination(self):
        invalid_params = [
            {'limit': 0},
            {'limit': MAX_PAGE_SIZE + 1},
            {'limit': 'abc'},
            {'offset': -1},
        ]
        for params in invalid_params:
            with self.subTest(params=params):
                response = self.client.get('/todos', params)
                self.assertEqual(response.status_code, 400)
                self.assertIn('error', response.json())

    def test_get_returns_503_when_database_fails(self):
        with patch.object(TodoListView.repository, 'list_all', side_effect=PyMongoError):
            response = self.client.get('/todos')
        self.assertEqual(response.status_code, 503)

    def test_post_returns_503_when_database_fails(self):
        with patch.object(TodoListView.repository, 'create', side_effect=PyMongoError):
            response = self._create('x')
        self.assertEqual(response.status_code, 503)
