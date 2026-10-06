# NOTE: DO NOT FORK THIS REPOSITORY. CLONE AND SETUP A STANDALONE REPOSITORY.

# Adbrew Test!

Hello! This test is designed to specifically test your Python, React and web development skills. The task is unconventional and has a slightly contrived setup on purpose and requires you to learn basic concepts of Docker on the fly. 


# Structure

This repository includes code for a Docker setup with 3 containers:
* App: This is the React dev server and runs on http://localhost:3000. The code for this resides in src/app directory.
* API: This is the backend container that run a Django instance on http://localhost:8000. 
* Mongo: This is a DB instance running on port 27017. Django views already have code written to connect to this instance of Mongo.

We highly recommend you go through the setup in `Dockerfile` and `docker-compose.yml`. If you are able to understand and explain the setup, that will be a huge differentiator.

# Setup
1. Clone this repository (DO NOT FORK)
```
git clone https://github.com/adbrew/test.git
```
2. Change into the cloned directory and set the environment variable for the code path. Replace `path_to_repository` appropriately.
```
export ADBREW_CODEBASE_PATH="{path_to_repository}/test/src"
```
3. Build container (you only need to build containers for the first time or if you change image definition, i.e., `Dockerfile`). This step will take a good amount of time.
```
docker-compose build
```
4. Once the build is completed, start the containers:
```
docker-compose up -d
```
5. Once complete, `docker ps` should output something like this:
```
CONTAINER ID   IMAGE               COMMAND                  CREATED         STATUS         PORTS                      NAMES
e445be7efa61   adbrew_test_api     "bash -c 'cd /src/re…"   3 minutes ago   Up 2 seconds   0.0.0.0:8000->8000/tcp     api
0fd203f12d8a   adbrew_test_app     "bash -c 'cd /src/ap…"   4 minutes ago   Up 3 minutes   0.0.0.0:3000->3000/tcp     app
884cb9296791   adbrew_test_mongo   "/usr/bin/mongod --b…"   4 minutes ago   Up 3 minutes   0.0.0.0:27017->27017/tcp   mongo
```
6. Check that you are able to access http://localhost:3000 and http://localhost:8000/todos
7. If the containers in #5 or #6 are not up, we would like you to use your debugging skills to figure out the issue. Only reach out to us if you've exhausted all possible options. The `app` container may take a good amount of time to start since it will download all package dependencies.

# Tips
1. Once containers are up and running, you can view container logs by executing `docker logs -f --tail=100 {container_name}` Replace `container_name` with `app` or `api`(output of `docker ps`)
2. You can enter the container and inspect it by executing `docker exec -it {container_name} bash` Replace `{container_name}` with `app` or `api` (output of `docker ps`)
3. Shut all containers using `docker-compose down`
4. Restart a container using `docker restart {container_name}`


# Task

When you run `localhost:3000`, you would see 2 things:
1. A form with a TODO description textbox and a submit button. On this form submission, the app should interact with the Django backend (`POST http://localhost:8000/todos`) and create a TODO in MongoDB.
2. A list with hardcoded TODOs. This should be changed to reflect TODOs in the backend (`GET http://localhost:8000/todos`). 
3. When the form is submitted, the TODO list should refresh again and fetch latest list of TODOs from MongoDB.

# Instructions [IMPORTANT] 
1. All React code should be implemented using [React hooks](https://reactjs.org/docs/hooks-intro.html) and should not use traditional stateful React components and component lifecycle method.
2. Do not use Django's model, serializers or SQLite DB. Persist and retrieve all data from the mongo instance. A `db` instance is already present in `views.py`.
3. Do not bypass the Docker setup. Submissions that do not have proper docker setup will be rejected.
4. We are looking for developers who have strong fundamentals and can ramp up fast. We expect you to learn and grasp basic React Hooks/Mongo/Docker concepts on the fly.
5. Do not fork this repository or submit your solution as a PR since this is a public repo and there are other candidates taking the same test. Send us a link to your repo privately.
6. If you are able to complete the test, we will have a live walkthrough of your code and ask questions to check your understanding.
7. The code for the actual solution is pretty easy. The code quality in your solution should be production-ready - error handling, abstractions, well-maintainable and modular code. If you're not aware, we recommend reading a bit about software design principles and applying them (both JS and Python). Here are some reading resources to get you started:
   * https://kinsta.com/blog/python-object-oriented-programming/
   * https://realpython.com/solid-principles-python/
   * https://www.toptal.com/python/python-design-patterns


---

# Solution notes

**API** (`src/rest/rest`)
* `GET /todos` returns all todos (oldest first). `POST /todos` with `{"description": "..."}` creates one and returns `201`. The trailing slash is optional.
* `views.py` handles HTTP, validation (non-empty string, max 200 chars) and error mapping (`400` invalid input, `503` Mongo failure).
* `repository.py` (`TodoRepository`) is the only code that touches Mongo, so the storage layer can be swapped or mocked without touching the view.

**App** (`src/app/src`)
* `api.js` wraps `fetch` and turns error responses into exceptions; `App.js` uses hooks only (`useState`, `useEffect`, `useCallback`).
* The list is loaded on mount and reloaded after each successful submit. Errors are shown inline.
* Tests: `cd src/app && yarn test`.

**Docker changes**
* The base image is pinned to `python:3.8-bullseye`. The floating `python:3.8` tag moved to a newer Debian where Mongo 4.4's `libssl1.1` dependency can't be installed.
* Bullseye is EOL, so apt's security repo is pointed at `archive.debian.org`.
* Removed the deprecated `easy_install pip` step and the obsolete compose `version` key.
