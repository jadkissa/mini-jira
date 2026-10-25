from fastapi import APIRouter
from app.routers import activity, auth, comments, labels, projects, tasks, teams, users

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(projects.router)
api_router.include_router(tasks.router)
api_router.include_router(users.router)
api_router.include_router(auth.router)
api_router.include_router(teams.router)
api_router.include_router(comments.router)
api_router.include_router(labels.router)
api_router.include_router(activity.router)
