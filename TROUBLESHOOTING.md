# Troubleshooting

Problems hit while building Mini Jira, and what fixed them.

## `pytest` cannot import `app`

**Symptom:** `ModuleNotFoundError: No module named 'app'`.

**Why:** pytest 9 does not put the current directory on `sys.path`. The app is imported as `app` only when the command runs from `backend/`.

**Fix:** `backend/pytest.ini` contains `pythonpath = .`. Run pytest from `backend/`.

## `app` has no `dependency_overrides`

**Symptom:** `AttributeError: module 'app' has no attribute 'dependency_overrides'` in `tests/conftest.py`.

**Why:** `from app.main import app` binds the name `app` to the FastAPI instance. A later `import app.models...` rebinds that name to the `app` package.

**Fix:** import the models before `from app.main import app`, or do not import them in `conftest.py`. Loading `app.main` already imports the models through the routers.

## The users migration was empty

**Symptom:** Alembic generated a revision whose `upgrade()` was only `pass`, and the `users` table was never created.

**Why:** Alembic only sees models imported in `backend/alembic/env.py`. `User` was missing, so autogenerate had nothing to add. That empty revision was already applied.

**Fix:** import every model in `env.py`, then add a new revision for the real table. Leave the empty revision in place. Do not edit a revision that has already run.

## PyJWT warns that the key is too short

**Symptom:** `InsecureKeyLengthWarning` during login or tests.

**Why:** HS256 needs a secret of at least 32 bytes. `dev-secret-change-me` is 20 bytes.

**Fix:** use a secret of at least 32 bytes. The default in `backend/app/core/config.py` and `backend/.env.example` is `dev-secret-change-me-use-at-least-32-bytes`.

## A missing token returns 403

**Symptom:** a request with no `Authorization` header returns 403. The tests expect 401.

**Why:** `HTTPBearer()` reports a missing header as 403.

**Fix:** `HTTPBearer(auto_error=False)` in `backend/app/core/deps.py`, then raise 401 when `credentials` is `None`.

## Tests cannot connect to `mini_jira_test`

**Symptom:** pytest fails with a connection error for database `mini_jira_test`.

**Why:** Postgres creates only the database named in `POSTGRES_DB`, which is `mini_jira`. The tests use a separate database so they can drop tables safely.

**Fix:** create it once:

```bash
docker exec -it mini-jira-db psql -U mini_jira -c "CREATE DATABASE mini_jira_test;"
```

GitHub Actions does the same thing in the test job, because the Postgres service starts empty of that database.

## GitHub rejects the workflow file

**Symptom:** the Actions tab shows "Invalid workflow file" before any step runs.

**Why:** a step must be a list item under `steps`. `uses` runs an action. `name` is only a label. Keys under `with:` must be indented further than `with`. `cache-dependency-path` is spelled with a `c`.

**Fix:** each step starts with `-` at the same column. Checkout is `- uses: actions/checkout@v4`.

## CI fails at `ruff check` with import and `Depends` errors

**Symptom:** the lint step exits 1. The log includes `I001` and `B008`, plus a count such as `Found 118 errors`.

**Why:** Ruff 0.17 checks import order and forbids function calls in argument defaults. FastAPI uses `Depends()` and `Query()` as defaults on purpose. The other findings were unsorted imports, `Union[...]` instead of `|`, and a few unused imports.

**Fix:** `backend/ruff.toml` ignores `B008` and marks `app` and `tests` as first-party. From `backend/`, `ruff check --fix .` rewrites the rest. Run `ruff check .` and expect `All checks passed` before pushing.

## `TypeError: 'function' object is not subscriptable` while importing the app

**Symptom:** importing `LabelService` fails on a return type written as `list[Label]`.

**Why:** a method named `list` is already defined on the class. The next annotation looks up `list` and finds that method, not the builtin.

**Fix:** put `from __future__ import annotations` at the top of the file so annotations are not evaluated while the class body runs.

## `ModuleNotFoundError: No module named 'backend'`

**Symptom:** the API fails on `from backend.app...` or `from db.session import ...`.

**Why:** `uvicorn app.main:app` is started from `backend/`, so the import root is `backend/`, not the repo root.

**Fix:** import with `from app...`.

## `GET /users/me` is treated as a user id

**Symptom:** `GET /api/v1/users/me` returns 422 because `"me"` fails integer parsing.

**Why:** `GET /users/{user_id}` matches first when it is declared above `/users/me`.

**Fix:** declare `GET /users/me` before `GET /users/{user_id}`.
