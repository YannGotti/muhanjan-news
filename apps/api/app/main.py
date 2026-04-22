from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import admin, attachments, auth, bot_ingest, monitoring, settings, stream
from app.core.config import settings as app_settings
from app.services.monitoring import get_health_snapshot

app = FastAPI(title=app_settings.app_name)

origins = [x.strip() for x in app_settings.cors_allow_origins.split(",") if x.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=app_settings.api_v1_prefix)
app.include_router(admin.router, prefix=app_settings.api_v1_prefix)
app.include_router(stream.router, prefix=app_settings.api_v1_prefix)
app.include_router(bot_ingest.router, prefix=app_settings.api_v1_prefix)
app.include_router(settings.router, prefix=app_settings.api_v1_prefix)
app.include_router(attachments.router, prefix=app_settings.api_v1_prefix)
app.include_router(monitoring.router, prefix=app_settings.api_v1_prefix)

app.mount("/uploads", StaticFiles(directory=app_settings.upload_dir), name="uploads")


@app.get("/health")
def health() -> dict:
    snapshot = get_health_snapshot()
    return {
        "status": snapshot["status"],
        "ready": snapshot["ready"],
    }


@app.get("/health/live")
def health_live() -> dict:
    return {"status": "ok"}


@app.get("/health/ready")
def health_ready():
    snapshot = get_health_snapshot()
    status_code = 200 if snapshot["ready"] else 503
    return JSONResponse(status_code=status_code, content=snapshot)
