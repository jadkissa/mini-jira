# Mini Jira

A task and project management backend (a simplified Jira/Trello) built with **FastAPI** and **PostgreSQL**.
Teams create projects, break them into tasks, assign them, comment, and track progress.

The goal of this project is to practice and demonstrate production-style backend engineering:
clean layered architecture, secure authentication, automated tests, background jobs, performance work,
and a full CI/CD pipeline.

> **Status:** Phase 0 (foundation). Progress is tracked in the [Roadmap](#roadmap).

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

**Core**
- User registration and login (JWT access + refresh tokens)
- Teams with members and roles
- Projects belonging to a team
- Tasks with status, priority, assignee, due date and labels
- Comments on tasks
- Filtering, sorting and pagination on list endpoints

**Advanced**
- Background jobs: notification on task assignment, due-date reminders
- Redis caching for heavy read endpoints
- Rate limiting
- Activity log (who changed what, and when)

**Optional**
- OAuth login (Google / GitHub)
- GraphQL endpoint for read queries
- WebSockets for live board updates

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

The code is split into layers so that each one has a single job:

- **Routers**: HTTP only. Parse the request, call a service, return a response.
- **Services**: business logic and permission rules. No HTTP and no SQL.
- **Repositories**: all database queries live here.
- **Models**: SQLAlchemy tables.
- **Schemas**: Pydantic models for request and response bodies.

Target layout (it grows phase by phase, not all at once):

```
mini-jira/
├── app/
│   ├── main.py
│   ├── core/            # config, security, dependencies
│   ├── db/              # session, base
│   ├── models/
│   ├── schemas/
│   ├── repositories/
│   ├── services/
│   ├── routers/
│   └── workers/         # Celery tasks
├── tests/
│   ├── unit/
│   └── integration/
├── alembic/
├── docker-compose.yml
├── Dockerfile
├── .github/workflows/
├── .env.example
├── DECISIONS.md
└── README.md
```

Request flow:

```
Client -> Router -> Service -> Repository -> PostgreSQL
                       |
                       +-> Celery task (via Redis) for slow work
```

---

## Data model

Initial draft. Each table is added in the phase that needs it.

| Table | Main fields | Phase |
|---|---|---|
| projects | id, name, description, created_at | 1-2 |
| tasks | id, project_id, title, description, status, priority, due_date, created_at, updated_at | 1-2 |
| users | id, email (unique), hashed_password, full_name, is_active, created_at | 3 |
| teams | id, name, owner_id, created_at | 4 |
| team_members | team_id, user_id, role (owner / admin / member) | 4 |
| comments | id, task_id, author_id, body, created_at | 5 |
| labels, task_labels | label: id, project_id, name, color; join table task_id + label_id | 5 |
| activity_log | id, task_id, actor_id, action, old_value, new_value, created_at | 5 |

Columns added later by migration: `tasks.assignee_id`, `tasks.reporter_id` (Phase 3), `projects.team_id` (Phase 4).

`tasks.status` is an enum: `todo`, `in_progress`, `done`.

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

---

## API overview

All routes live under `/api/v1`.

| Group | Endpoints |
|---|---|
| Health | `GET /health` |
| Projects | `POST /projects`, `GET /projects`, `GET /projects/{id}`, `PATCH /projects/{id}`, `DELETE /projects/{id}` |
| Tasks | `POST /projects/{id}/tasks`, `GET /projects/{id}/tasks`, `GET /tasks/{id}`, `PATCH /tasks/{id}`, `DELETE /tasks/{id}` |
| Auth | `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`, `GET /users/me` |
| Teams | `POST /teams`, `GET /teams`, `GET /teams/{id}`, `POST /teams/{id}/members`, `DELETE /teams/{id}/members/{user_id}` |
| Comments | `POST /tasks/{id}/comments`, `GET /tasks/{id}/comments` |
| Labels | `POST /projects/{id}/labels`, `GET /projects/{id}/labels` |

List endpoints support: `?page=1&page_size=20&status=todo&assignee_id=5&sort=-due_date`.

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
- [ ] Repo, `.gitignore`, virtual environment, `requirements.txt` (or `pyproject.toml`)
- [ ] Ruff configured (lint + format)
- [ ] Settings loaded from environment variables (`pydantic-settings`), `.env.example`
- [ ] `GET /health` endpoint
- [ ] pytest configured with the first test (for `/health`)
- [ ] README scope and tech stack finalized

### Phase 1: FastAPI fundamentals (in-memory storage)
*Learn: routing, path/query parameters, Pydantic validation, status codes, error handling, dependency injection basics.*
- [ ] Projects CRUD with Pydantic schemas (list in memory)
- [ ] Tasks CRUD under projects, status as enum
- [ ] Consistent error responses (404, 422, custom exceptions)
- [ ] Routers separated from schemas, versioned under `/api/v1`
- [ ] Tests for every endpoint (success and failure cases)

### Phase 2: Persistence
*Learn: relational modeling, ORM, migrations, the repository pattern, containers for local services.*
- [ ] Final data model (ERD) for projects and tasks on paper
- [ ] Docker Compose with PostgreSQL
- [ ] SQLAlchemy 2.0 models and the first Alembic migration
- [ ] Repository layer replaces the in-memory store; services layer introduced
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
- [ ] Dockerfile for the API, full Docker Compose (API + DB)
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

_To be filled in as the project takes shape (target: Phase 6)._ Expected experience:

```
git clone <repo-url>
cd mini-jira
cp .env.example .env
docker compose up --build
```

Then open `http://localhost:8000/docs`.

---

## Testing

_To be filled in during Phase 1 and extended every phase._ Planned commands:

```
pytest
pytest --cov=app
```

---

## Design decisions

A running log lives in `DECISIONS.md`. For each important choice write three lines:
what was chosen, what the alternatives were, and why.
Examples: why a repository layer, why JWT over sessions, why Celery over FastAPI background tasks, why a given index.