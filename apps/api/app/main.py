from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import auth, admin, stream, bot_ingest, settings
from app.core.config import settings as app_settings
from app.db.session import engine
from app.db.base import Base

Base.metadata.create_all(bind=engine)

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

app.mount("/uploads", StaticFiles(directory=app_settings.upload_dir), name="uploads")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
