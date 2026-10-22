# Mini Jira

A task and project management backend (a simplified Jira/Trello) built with **FastAPI** and **PostgreSQL**.
Teams create projects, break them into tasks, assign them, comment, and track progress.

The goal of this project is to practice and demonstrate production-style backend engineering:
clean layered architecture, secure authentication, automated tests, background jobs, performance work,
and a full CI/CD pipeline.

> **Status:** Phase 2 in progress — projects & tasks CRUD on PostgreSQL (Alembic, Docker Compose).  
> Next: tests, services/repositories, pagination — then Phase 3 (auth).  
> Progress is tracked in the [Roadmap](#roadmap).

---

## Table of contents

1. [Features](#features)
2. [Tech stack](#tech-stack)
3. [Architecture](#architecture)
4. [Data model](#data-model)
5. [Roles and permissions](#roles-and-permissions)
6. [API overview](#api-overview)
7. [Roadmap](#roadmap)
8. [Development workflow](#development-workflow)
9. [Getting started](#getting-started)
10. [Testing](#testing)
11. [Design decisions](#design-decisions)

---

## Features

**Implemented now (Phase 2)**
- Projects CRUD
- Tasks CRUD nested under projects (`POST/GET /projects/{id}/tasks`)
- Task status (`todo` / `in_progress` / `done`) and priority
- `duration_days` + computed `delivery_date`
- Cascade delete: deleting a project removes its tasks
- Health check, OpenAPI docs at `/docs`

**Planned (later phases)**
- User registration and login (JWT access + refresh tokens)
- Teams with members and roles; projects belonging to a team
- Assignees, comments, labels
- Filtering, sorting and pagination on list endpoints
- Background jobs, Redis cache, rate limiting, activity log
- Optional: OAuth, GraphQL, WebSockets

---

## Tech stack

| Area             | Choice                                         | Introduced in |
| ---------------- | ---------------------------------------------- | ------------- |
| Language         | Python 3.12+                                   | Phase 0       |
| Framework        | FastAPI                                        | Phase 1       |
| Validation       | Pydantic v2                                    | Phase 1       |
| Tests            | pytest, httpx                                  | Phase 1       |
| Lint / format    | Ruff                                           | Phase 0       |
| Database         | PostgreSQL                                     | Phase 2       |
| ORM / migrations | SQLAlchemy 2.0 + Alembic                       | Phase 2       |
| Containers       | Docker, Docker Compose                         | Phase 2 (DB), Phase 6 (app) |
| Auth             | JWT, argon2 password hashing                   | Phase 3       |
| CI               | GitHub Actions                                 | Phase 6       |
| Cache / broker   | Redis                                          | Phase 7       |
| Background jobs  | Celery (worker + beat)                         | Phase 7       |
| CD / deployment  | GitHub Actions + VPS or AWS                    | Phase 9       |
| Later            | Kubernetes, Prometheus metrics                 | Phase 9       |

---

## Architecture

Target layers (services/repositories come next in Phase 2):

- **Routers**: HTTP only. Parse the request, call a service, return a response.
- **Services**: business logic and permission rules. No HTTP and no SQL.
- **Repositories**: all database queries live here.
- **Models**: SQLAlchemy tables.
- **Schemas**: Pydantic models for request and response bodies.

**Current flow (temporary):** `Client -> Router -> SQLAlchemy Session -> PostgreSQL`  
Target flow:

```
Client -> Router -> Service -> Repository -> PostgreSQL
                       |
                       +-> Celery task (via Redis) for slow work
```

Layout:

```
mini-jira/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/v1.py        # /api/v1 router mount
│   │   ├── core/            # config (pydantic-settings)
│   │   ├── db/              # session, base
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routers/
│   │   ├── repositories/    # Phase 2 (planned)
│   │   ├── services/        # Phase 2 (planned)
│   │   └── workers/         # Celery (Phase 7)
│   ├── alembic/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── docker-compose.yml       # api + Postgres
├── .env.example             # Compose vars (optional)
├── DECISIONS.md
└── README.md
```

---

## Data model

Each table is added in the phase that needs it.

| Table | Main fields | Phase |
|---|---|---|
| projects | id, name, description, created_at, updated_at | 1-2 |
| tasks | id, project_id, title, description, status, priority, duration_days, delivery_date, created_at, updated_at | 1-2 |
| users | id, email (unique), hashed_password, full_name, is_active, created_at | 3 |
| teams | id, name, owner_id, created_at | 4 |
| team_members | team_id, user_id, role (owner / admin / member) | 4 |
| comments | id, task_id, author_id, body, created_at | 5 |
| labels, task_labels | label: id, project_id, name, color; join table task_id + label_id | 5 |
| activity_log | id, task_id, actor_id, action, old_value, new_value, created_at | 5 |

Columns added later by migration: `tasks.assignee_id`, `tasks.reporter_id` (Phase 3), `projects.team_id` (Phase 4).

- `tasks.status`: `todo` | `in_progress` | `done`
- `tasks.priority`: `low` | `medium` | `high`
- `delivery_date` = `created_at.date() + duration_days` (when `duration_days` is set)
- Deleting a project **cascades** to its tasks (ORM + DB `ON DELETE CASCADE`)
- Timestamps use timezone-aware UTC (`timestamptz`)

Open questions to settle and record in `DECISIONS.md`:
- One assignee per task, or many?
- Soft delete or hard delete for tasks and projects?
- Which columns need indexes (think about filters and joins)?

---

## Roles and permissions

| Action | Member | Admin | Owner |
|---|---|---|---|
| View team projects and tasks | yes | yes | yes |
| Create and edit tasks | yes | yes | yes |
| Delete any task | no | yes | yes |
| Manage projects | no | yes | yes |
| Invite or remove members | no | yes | yes |
| Delete the team | no | no | yes |

Invariant: a user can only access data of teams they belong to.  
*(Enforced in Phase 4 — endpoints are open for now.)*

---

## API overview

All app routes live under `/api/v1` (except health).

| Group | Endpoints | Status |
|---|---|---|
| Health | `GET /health` | Done |
| Projects | `POST /projects`, `GET /projects`, `GET /projects/{id}`, `PATCH /projects/{id}`, `DELETE /projects/{id}` | Done |
| Tasks | `POST /projects/{id}/tasks`, `GET /projects/{id}/tasks`, `GET /tasks/{id}`, `PATCH /tasks/{id}`, `DELETE /tasks/{id}` | Done |
| Auth | `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`, `GET /users/me` | Phase 3 |
| Teams | `POST /teams`, `GET /teams`, `GET /teams/{id}`, `POST /teams/{id}/members`, `DELETE /teams/{id}/members/{user_id}` | Phase 4 |
| Comments | `POST /tasks/{id}/comments`, `GET /tasks/{id}/comments` | Phase 5 |
| Labels | `POST /projects/{id}/labels`, `GET /projects/{id}/labels` | Phase 5 |

List query params (planned): `?page=1&page_size=20&status=todo&assignee_id=5&sort=-delivery_date`.

Once teams exist (Phase 4), project creation moves under `POST /teams/{id}/projects`.

Interactive docs: `/docs` (Swagger) and `/redoc`.

---

## Roadmap

Rules for every phase:
- **Tests are written alongside the code**, not after it. A phase is not done without them.
- Each phase ends with something you can **demo and explain without notes**.
- Each phase is delivered through feature branches and pull requests.
- Important choices get 3 lines in `DECISIONS.md`.

### Phase 0: Foundation and tooling
*Learn: project setup, Git workflow, configuration.*
- [x] Repo, `.gitignore`, virtual environment, `requirements.txt`
- [ ] Ruff configured (lint + format)
- [x] Settings loaded from environment variables (`pydantic-settings`), `.env.example`
- [x] `GET /health` endpoint
- [ ] pytest configured with the first test (for `/health`)
- [x] README scope and tech stack finalized

### Phase 1: FastAPI fundamentals
*Learn: routing, path/query parameters, Pydantic validation, status codes, error handling, dependency injection basics.*  
*(We moved persistence earlier and skipped a long-lived in-memory store.)*
- [x] Projects CRUD with Pydantic schemas
- [x] Tasks CRUD under projects, status as enum
- [x] Consistent error responses (404, 422)
- [x] Routers separated from schemas, versioned under `/api/v1`
- [ ] Tests for every endpoint (success and failure cases)

### Phase 2: Persistence
*Learn: relational modeling, ORM, migrations, the repository pattern, containers for local services.*
- [x] Data model for projects and tasks
- [x] Docker Compose with PostgreSQL (+ API image)
- [x] SQLAlchemy 2.0 models and Alembic migrations
- [ ] Repository layer + services layer (logic still in routers)
- [ ] Pagination, filtering and sorting on list endpoints
- [ ] Separate test database and fixtures; tests still pass

### Phase 3: Authentication
*Learn: password hashing, JWT, securing endpoints, dependencies.*
- [ ] Users table and migration
- [ ] Register and login with hashed passwords (argon2)
- [ ] JWT access and refresh tokens
- [ ] `get_current_user` dependency protecting all endpoints
- [ ] `reporter_id` set from the authenticated user; `assignee_id` added
- [ ] Tests for auth flows and unauthorized access

### Phase 4: Teams and authorization
*Learn: many-to-many relations, role-based access control, data isolation.*
- [ ] Teams and team members, migration
- [ ] Projects belong to teams
- [ ] Role-based permissions (owner / admin / member)
- [ ] Team-level data isolation (users only see their teams' data)
- [ ] Permission tests for every role on every sensitive endpoint

### Phase 5: Domain completion
*Learn: more relations, query design, auditing.*
- [ ] Comments
- [ ] Labels and task labels
- [ ] Activity log
- [ ] Swagger docs cleaned up, Postman collection exported
- [ ] Tests for the new endpoints

### Phase 6: Quality and CI
*Learn: containerizing an app, automated pipelines, coverage.*
- [x] Dockerfile for the API, Docker Compose (API + DB)
- [ ] Coverage report (target 70%+)
- [ ] GitHub Actions: lint, test, build image on every push and pull request
- [ ] README "Getting started" works from a clean clone

> After Phase 6 the project is solid enough to put on a CV and apply with. Later phases make it stand out.

### Phase 7: Background jobs
*Learn: message brokers, workers, scheduled tasks, why work leaves the request cycle.*
- [ ] Redis and Celery worker added to Docker Compose
- [ ] Notification task when a task is assigned
- [ ] Due-date reminders with Celery beat
- [ ] Tests for tasks (eager mode) and retry behavior

### Phase 8: Performance and reliability
*Learn: measuring before optimizing.*
- [ ] Indexes based on real queries (check with `EXPLAIN`)
- [ ] Fix N+1 queries
- [ ] Redis caching for heavy endpoints, with invalidation rules
- [ ] Rate limiting
- [ ] Load test (locust or k6); before/after numbers recorded here
- [ ] (Optional) Migrate database access to async, documented as a decision

### Phase 9: Deployment and observability
*Learn: delivery, operations, monitoring.*
- [ ] CD: deploy automatically on merge to `main` (VPS or AWS)
- [ ] Structured logging and health checks
- [ ] Basic metrics (Prometheus)
- [ ] Kubernetes manifests (Deployment, Service, ConfigMap, Secret)

### Phase 10: Optional extras
- [ ] OAuth login (Google / GitHub)
- [ ] GraphQL read endpoint
- [ ] WebSockets for live updates
- [ ] Architecture diagram and screenshots in this README

---

## Development workflow

- No direct commits to `main`. One branch per feature, for example `feature/projects-crud`.
- Commit messages follow Conventional Commits: `feat: add task creation endpoint`, `fix: ...`, `test: ...`, `chore: ...`.
- Every change goes through a pull request, even when working alone.
- Secrets are never committed. Only `.env.example` is tracked.

---

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

**3. Backend venv + deps**

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

Open:
- Docs: http://127.0.0.1:8000/docs  
- Health: http://127.0.0.1:8000/health  

Optional: run API in Docker too with `docker compose up --build` (Compose sets `DATABASE_URL` host to `db`).

---

## Testing

Not set up yet. Planned:

```bash
cd backend
pytest
pytest --cov=app
```

---

## Design decisions

A running log lives in [`DECISIONS.md`](DECISIONS.md). For each important choice write three lines:
what was chosen, what the alternatives were, and why.
