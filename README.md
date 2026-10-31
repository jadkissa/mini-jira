# Mini Jira

A task and project management backend (a simplified Jira/Trello) built with **FastAPI** and **PostgreSQL**.
Teams create projects, break them into tasks, assign them, comment, and track progress.

The learning plan lives in [ROADMAP.md](ROADMAP.md).

## Features

- Projects and tasks. Tasks have a status (`todo`, `in_progress`, `done`), a priority, and an optional `duration_days`. `delivery_date` is computed from that duration.
- Teams with owner, admin, and member roles. A project belongs to a team. Users only see data for teams they belong to.
- Register and login. Passwords are stored as an argon2 hash. Login returns a JWT access token and a refresh token.
- New tasks store `reporter_id` from the logged-in user. `assignee_id` is optional.
- Comments on tasks, labels on projects, and an activity log for task changes.
- List endpoints accept `?page=1&page_size=20`. Task lists also accept `status` and `sort`.
- Health check and OpenAPI docs. A Postman collection is in `postman/mini-jira.postman_collection.json`.

Still planned: background jobs, Redis cache, rate limiting, and optional OAuth, GraphQL, and WebSockets. See the roadmap.

## Tech stack

| Area | Choice |
|---|---|
| Language | Python 3.12+ |
| Framework | FastAPI |
| Validation | Pydantic v2 |
| Database | PostgreSQL, SQLAlchemy 2.0, Alembic |
| Auth | JWT, argon2 |
| Tests | pytest, pytest-cov |
| Lint | Ruff |
| Containers | Docker, Docker Compose |
| CI | GitHub Actions |

## Architecture

- **Routers** handle HTTP. They parse the request, call a service, and return a response.
- **Services** hold business rules and permissions. No SQL.
- **Repositories** hold every database query.
- **Models** are SQLAlchemy tables. **Schemas** are Pydantic request and response bodies.

```
Client -> Router -> Service -> Repository -> PostgreSQL
```

```
mini-jira/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/v1.py
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routers/
│   │   ├── repositories/
│   │   └── services/
│   ├── alembic/
│   ├── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── ruff.toml
│   └── .env.example
├── .github/workflows/ci.yml
├── docker-compose.yml
├── postman/
├── DECISIONS.md
├── ROADMAP.md
├── TROUBLESHOOTING.md
└── README.md
```

## Data model

| Table | Main fields |
|---|---|
| users | id, email (unique), hashed_password, full_name, is_active, created_at |
| teams | id, name, owner_id, created_at |
| team_members | team_id, user_id, role (`owner`, `admin`, `member`) |
| projects | id, name, description, team_id, created_at, updated_at |
| tasks | id, project_id, title, description, status, priority, duration_days, delivery_date, reporter_id, assignee_id, created_at, updated_at |
| comments | id, task_id, author_id, body, created_at |
| labels | id, project_id, name, color |
| task_labels | task_id, label_id |
| activity_log | id, task_id, actor_id, action, old_value, new_value, created_at |

`delivery_date` is the UTC date of `created_at` plus `duration_days`, when a duration is set. Deleting a project cascades to its tasks. Timestamps are timezone-aware UTC.

## Roles

| Action | Member | Admin | Owner |
|---|---|---|---|
| View team projects and tasks | yes | yes | yes |
| Create and edit tasks | yes | yes | yes |
| Comment, and add or remove a label on a task | yes | yes | yes |
| Delete any task | no | yes | yes |
| Manage projects, including creating and deleting labels | no | yes | yes |
| Invite or remove members | no | yes | yes |
| Delete the team | no | no | yes |

An outsider gets 404. A member who lacks the role gets 403. An admin may invite members. Only the owner may invite an admin or delete the team.

## API

All app routes live under `/api/v1`. `GET /health` does not.

| Group | Endpoints |
|---|---|
| Health | `GET /health` |
| Auth | `POST /auth/login`, `POST /auth/refresh`, `GET /users/me` |
| Users | `POST /users`, `GET /users/{id}`, `PATCH /users/{id}`, `DELETE /users/{id}` |
| Teams | `POST /teams`, `GET /teams`, `GET /teams/{id}`, `DELETE /teams/{id}`, `POST /teams/{id}/members`, `DELETE /teams/{id}/members/{user_id}`, `POST /teams/{id}/projects` |
| Projects | `GET /projects`, `GET /projects/{id}`, `PATCH /projects/{id}`, `DELETE /projects/{id}` |
| Tasks | `POST /projects/{id}/tasks`, `GET /projects/{id}/tasks`, `GET /tasks/{id}`, `PATCH /tasks/{id}`, `DELETE /tasks/{id}` |
| Comments | `POST /tasks/{id}/comments`, `GET /tasks/{id}/comments` |
| Labels | `POST /projects/{id}/labels`, `GET /projects/{id}/labels`, `DELETE /projects/{id}/labels/{label_id}`, `GET /tasks/{id}/labels`, `POST /tasks/{id}/labels`, `DELETE /tasks/{id}/labels/{label_id}` |
| Activity | `GET /tasks/{id}/activity` |

`POST /users`, `POST /auth/login`, and `POST /auth/refresh` are public. Every other route needs `Authorization: Bearer <access_token>`.

Interactive docs: `/docs` and `/redoc`. Import `postman/mini-jira.postman_collection.json` to call the same routes from Postman. Run **Login** first. It stores the access token.

## Getting started

**1. Clone and env**

```bash
git clone <repo-url>
cd mini-jira
cp backend/.env.example backend/.env
```

**2. Start Postgres**

```bash
docker compose up -d db
```

**3. Backend venv and dependencies**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**4. Migrations**

```bash
alembic upgrade head
```

**5. Run the API**

```bash
uvicorn app.main:app --reload
```

Open the docs at http://127.0.0.1:8000/docs and the health check at http://127.0.0.1:8000/health.

`docker compose up --build` runs the API in Docker as well. Compose points `DATABASE_URL` at the `db` service.

## Testing

From `backend/`, with Postgres running and a database named `mini_jira_test`:

```bash
docker exec -it mini-jira-db psql -U mini_jira -c "CREATE DATABASE mini_jira_test;"
pytest
pytest --cov=app
```

Create `mini_jira_test` once. Each test builds and drops its own tables there. The latest local coverage run was 40 tests and 93%.

GitHub Actions lints the code, runs `pytest`, and builds the API image on every push and pull request. That job does not enforce the coverage number yet.

## Development

- One branch per feature, for example `feature/projects-crud`.
- Commit messages follow Conventional Commits: `feat: add task creation endpoint`, `fix: ...`, `test: ...`, `chore: ...`.
- Secrets stay local. Only `.env.example` is tracked.

Choices that are already settled are recorded in [DECISIONS.md](DECISIONS.md). Problems hit while building the project are in [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
