# TODO App

A small full-stack TODO app: a React frontend, a Django REST API and MongoDB, all run with Docker Compose.

## Architecture

| Container | Tech | Port | Code |
|-----------|------|------|------|
| `app` | React 17 (hooks only), dev server | 3000 | `src/app` |
| `api` | Django 3 + Django REST Framework | 8000 | `src/rest` |
| `mongo` | MongoDB 4.4 | 27017 | data in `src/db` |

All three containers are built from the same `Dockerfile`. `docker-compose.yml` mounts `src/` into each container at `/src`, so code changes are picked up without rebuilding. The API reaches Mongo through the `MONGO_HOST` and `MONGO_PORT` environment variables set in the `Dockerfile`. Django's ORM and SQLite are not used; all data lives in MongoDB (`test_db.todos`).

## Getting started

Requires Docker and Docker Compose.

```bash
git clone <this-repository-url>
cd <repository-directory>
export ADBREW_CODEBASE_PATH="$(pwd)/src"
docker-compose up -d --build
```

The first build takes a few minutes, and the `app` container needs a little longer to install its dependencies on first start (`docker logs -f app` to follow).

- Frontend: http://localhost:3000
- API: http://localhost:8000/todos

Useful commands:

```bash
docker logs -f --tail=100 api    # or app / mongo
docker exec -it api bash         # shell into a container
docker-compose down              # stop everything
```

## API

### `GET /todos`
Returns all TODOs, oldest first.

```json
[{"id": "65f1...", "description": "Learn Docker", "created_at": "2026-10-07T10:00:00+00:00"}]
```

### `POST /todos`
Creates a TODO.

```json
{"description": "Learn Docker"}
```

| Status | Meaning |
|--------|---------|
| `201` | Created; the body is the new TODO |
| `400` | `description` is missing, not a string, blank, or longer than 200 characters |
| `503` | MongoDB is unavailable |

Errors are returned as `{"error": "<message>"}`. The trailing slash is optional (`/todos` and `/todos/` both work).

## Code layout

**Backend** (`src/rest/rest`)
- `views.py`: `TodoListView` handles HTTP, validation and error mapping.
- `repository.py`: `TodoRepository` is the only code that talks to Mongo, so storage can be swapped or mocked without touching the view.
- `tests.py`: unit and API tests.

**Frontend** (`src/app/src`)
- `api.js`: thin `fetch` wrapper that turns error responses into exceptions. The API URL can be overridden with `REACT_APP_API_URL`.
- `App.js`: function component using `useState`, `useEffect` and `useCallback`. It loads TODOs on mount and reloads after each successful submit; errors are shown inline.
- `App.test.js`: component tests with the API module mocked.

## Tests

```bash
# Backend (uses mongomock, so no real Mongo is needed)
docker exec api bash -c "cd /src/rest && python manage.py test"

# Frontend
docker exec app bash -c "cd /src/app && CI=true yarn test"
```

## Docker notes

- The base image is pinned to `python:3.8-bullseye`. The floating `python:3.8` tag moved to a newer Debian, where the `libssl1.1` dependency of MongoDB 4.4 can't be installed.
- Bullseye is end-of-life, so apt's security repository is pointed at `archive.debian.org`.
- Mongo data is persisted in `src/db` (gitignored).
