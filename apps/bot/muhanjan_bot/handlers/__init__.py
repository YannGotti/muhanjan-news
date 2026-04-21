from aiogram import Router

from .errors import router as errors_router
from .menu import router as menu_router
from .profile import router as profile_router
from .submissions import router as submission_router


def setup_routers() -> Router:
    root = Router(name="root")
    root.include_router(profile_router)
    root.include_router(menu_router)
    root.include_router(submission_router)
    root.include_router(errors_router)
    return root
