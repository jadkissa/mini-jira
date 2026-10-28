from fastapi import FastAPI

from app.api.v1 import api_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    openapi_tags=[
        {"name": "health", "description": "Liveness check. No token required."},
        {"name": "auth", "description": "Login and refresh. No token required."},
        {"name": "users", "description": "Register is public. Other user routes need an access token."},
        {"name": "teams", "description": "Teams, members, and project creation."},
        {"name": "projects", "description": "Projects the current user can see."},
        {"name": "tasks", "description": "Tasks on those projects."},
        {"name": "comments", "description": "Comments on a task. Any team member."},
        {"name": "labels", "description": "Project labels. Managers create them. Members attach them."},
        {"name": "activity", "description": "What changed on a task."},
    ],
)

app.include_router(api_router)

@app.get("/health", tags=["health"])
def health_check():
    """Report that the API is running and which environment it is in."""
    return {"status": "ok", "environment": settings.environment}

