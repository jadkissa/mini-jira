# Roadmap

Learning plan for Mini Jira. The [README](README.md) describes the project as it is today.

Rules for every phase:

- Tests are written alongside the code. A phase is not done without them.
- Each phase ends with something you can demo and explain without notes.
- Each phase is delivered through feature branches and pull requests.
- Important choices get 3 lines in `DECISIONS.md`.

## Phase 0: Foundation and tooling

*Learn: project setup, Git workflow, configuration.*

- [x] Repo, `.gitignore`, virtual environment, `requirements.txt`
- [x] Ruff lint configured (`backend/ruff.toml`) and run in CI
- [ ] Ruff format
- [x] Settings loaded from environment variables (`pydantic-settings`), `.env.example`
- [x] `GET /health` endpoint
- [x] pytest configured with the first test (for `/health`)
- [x] README scope and tech stack finalized

## Phase 1: FastAPI fundamentals

*Learn: routing, path/query parameters, Pydantic validation, status codes, error handling, dependency injection basics.*

Persistence moved earlier, so there was no long-lived in-memory store.

- [x] Projects CRUD with Pydantic schemas
- [x] Tasks CRUD under projects, status as enum
- [x] Consistent error responses (404, 422)
- [x] Routers separated from schemas, versioned under `/api/v1`
- [ ] Tests for every endpoint (success and failure cases)

## Phase 2: Persistence

*Learn: relational modeling, ORM, migrations, the repository pattern, containers for local services.*

- [x] Data model for projects and tasks
- [x] Docker Compose with PostgreSQL (+ API image)
- [x] SQLAlchemy 2.0 models and Alembic migrations
- [x] Repository layer + services layer
- [x] Pagination, filtering and sorting on list endpoints
- [x] Separate test database and fixtures; tests still pass

## Phase 3: Authentication

*Learn: password hashing, JWT, securing endpoints, dependencies.*

- [x] Users table and migration
- [x] Register with hashed passwords (argon2)
- [x] Login with hashed passwords
- [x] JWT access and refresh tokens
- [x] `get_current_user` dependency protecting all endpoints
- [x] `reporter_id` set from the authenticated user; `assignee_id` added
- [x] Tests for auth flows and unauthorized access

## Phase 4: Teams and authorization

*Learn: many-to-many relations, role-based access control, data isolation.*

- [x] Teams and team members, migration
- [x] Projects belong to teams
- [x] Role-based permissions (owner / admin / member)
- [x] Team-level data isolation (users only see their teams' data)
- [x] Permission tests for every role on every sensitive endpoint
- [x] Users can only edit or delete themselves; superuser with full permissions
- [x] `is_active` enforced on login, refresh, and every authenticated request

## Phase 5: Domain completion

*Learn: more relations, query design, auditing.*

- [x] Comments
- [x] Labels and task labels
- [x] Activity log
- [x] Swagger docs cleaned up, Postman collection exported
- [x] Tests for the new endpoints

## Phase 6: Quality and CI

*Learn: containerizing an app, automated pipelines, coverage.*

- [x] Dockerfile for the API, Docker Compose (API + DB)
- [x] Coverage report. Local run: 51 tests, 94% (target was 70%+). `pytest-cov` is in `requirements.txt`
- [x] GitHub Actions: lint, test, and build the image on every push and pull request
- [ ] CI still runs `pytest -q`. It does not fail the job when coverage drops under 70%
- [ ] README "Getting started" works from a clean clone

After Phase 6 the project is solid enough to put on a CV. Later phases make it stand out.

## Phase 7: Background jobs

*Learn: message brokers, workers, scheduled tasks, why work leaves the request cycle.*

- [ ] Redis and Celery worker added to Docker Compose
- [ ] Notification task when a task is assigned
- [ ] Due-date reminders with Celery beat
- [ ] Tests for tasks (eager mode) and retry behavior

## Phase 8: Performance and reliability

*Learn: measuring before optimizing.*

- [ ] Indexes based on real queries (check with `EXPLAIN`)
- [ ] Fix N+1 queries
- [ ] Redis caching for heavy endpoints, with invalidation rules
- [ ] Rate limiting
- [ ] Load test (locust or k6); before/after numbers recorded here
- [ ] (Optional) Migrate database access to async, documented as a decision

## Phase 9: Deployment and observability

*Learn: delivery, operations, monitoring.*

- [ ] CD: deploy automatically on merge to `main` (VPS or AWS)
- [ ] Structured logging and health checks
- [ ] Basic metrics (Prometheus)
- [ ] Kubernetes manifests (Deployment, Service, ConfigMap, Secret)

## Phase 10: Optional extras

- [ ] OAuth login (Google / GitHub)
- [ ] GraphQL read endpoint
- [ ] WebSockets for live updates
- [ ] Architecture diagram and screenshots in the README
