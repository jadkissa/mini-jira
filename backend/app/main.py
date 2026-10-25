from fastapi import FastAPI
from app.core.config import get_settings
from app.api.v1 import api_router


settings = get_settings()

app = FastAPI(title=settings.app_name, description=settings.app_description)

app.include_router(api_router)

@app.get("/health")
def health_check():
    """Report that the API is running and which environment it is in."""
    return {"status": "ok", "environment": settings.environment}

