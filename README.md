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
git clone https://github.com/ajitashwath/adb-asgmt
cd adb-asgmt
export ADBREW_CODEBASE_PATH="$(pwd)/src"
docker-compose up -d --build
```

On Windows, run these in Git Bash (or set `ADBREW_CODEBASE_PATH` to the absolute path of `src`). The first build takes a few minutes, and the `app` container needs a little longer to install its dependencies on first start (`docker logs -f app` to follow).

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
Returns a page of TODOs, newest first.

| Query param | Default | Rules |
|-------------|---------|-------|
| `limit` | `50` | integer, 1 to 100 |
| `offset` | `0` | integer, 0 or more |

Example: `GET /todos?limit=10&offset=10` returns the second page of 10.

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
| `400` | `description` is missing, null, not a string, blank, or longer than 200 characters; or the body is not valid JSON |
| `503` | MongoDB is unavailable |

`GET` returns `400` for an invalid `limit` or `offset`, and `503` if MongoDB is unavailable.

Every error is returned as `{"error": "<message>"}`, e.g. `{"error": "description: This field is required."}`. The trailing slash is optional (`/todos` and `/todos/` both work).

## Code layout

**Backend** (`src/rest/rest`)
- `views.py`: `TodoListView` handles HTTP and maps failures to status codes (400 / 503).
- `serializers.py`: DRF serializers that validate the request body and the pagination query params, plus the limits (max description length, page sizes).
- `repository.py`: `TodoRepository` is the only code that talks to Mongo, so storage can be swapped or mocked without touching the view. It sorts newest first and creates an index on `created_at` the first time the list is read (not at startup, so the API can start before Mongo is reachable).
- `exceptions.py`: DRF exception handler so framework errors such as malformed JSON use the same `{"error": ...}` format.
- `tests.py`: repository and API tests (17), using `mongomock`.

**Frontend** (`src/app/src`)
- `api.js`: thin `fetch` wrapper that turns error responses into exceptions. The API URL can be overridden with `REACT_APP_API_URL`.
- `App.js`: function component using `useState`, `useEffect` and `useCallback`. It loads TODOs on mount (the API returns the 50 newest, shown newest first) and reloads after each successful submit. The submit button is disabled while the input is blank or a request is in flight, and errors are shown in a banner.
- `App.css`: card-style layout (form on top, list below, empty-state message); colours are CSS variables at the top of the file.
- `App.test.js`: component tests with the API module mocked (listing, create + refresh, load error).

## Tests

```bash
# Backend (uses mongomock, so no real Mongo is needed)
docker exec api bash -c "cd /src/rest && python manage.py test"

# Frontend
docker exec app bash -c "cd /src/app && CI=true yarn test"
```

## Configuration

Settings read these environment variables (the defaults suit local development only):

| Variable | Default | Purpose |
|----------|---------|---------|
| `DJANGO_SECRET_KEY` | insecure placeholder | Django secret key. Set it anywhere that isn't local. |
| `DJANGO_DEBUG` | `true` | Set to `false` outside local development. |
| `MONGO_HOST`, `MONGO_PORT` | set in the `Dockerfile` | Where the API finds MongoDB. |
| `REACT_APP_API_URL` | `http://localhost:8000` | Frontend only: base URL of the API. |

CORS only allows the frontend origins `http://localhost:3000` and `http://127.0.0.1:3000`.

## Docker notes

- The base image is pinned to `python:3.8-bullseye`. The floating `python:3.8` tag moved to a newer Debian, where the `libssl1.1` dependency of MongoDB 4.4 can't be installed.
- Bullseye is end-of-life, so apt's security repository is pointed at `archive.debian.org`.
- `CHOKIDAR_USEPOLLING=true` is set on the `app` service so hot reload works on Windows/macOS, where file-change events don't pass through Docker bind mounts.
- Don't run `npm install` inside `src/app`: it rewrites `yarn.lock`. Dependencies are installed by `yarn` in the container.
- Mongo data is persisted in `src/db` (gitignored). To reset it, run `docker-compose down` and delete `src/db`.
