from fastapi import APIRouter
from .auth import router as auth_router
from .health import router as health_router
from .goals import router as goals_router
from .tasks import router as tasks_router
from .achievements import router as achievements_router
from .users import router as users_router
from .stats import router as stats_router
from .insights import router as insights_router
from .admin import router as admin_router
from .notifications import router as notifications_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(health_router)
router.include_router(goals_router)
router.include_router(tasks_router)
router.include_router(achievements_router)
router.include_router(users_router)
router.include_router(stats_router)
router.include_router(insights_router)
router.include_router(admin_router)
router.include_router(notifications_router)

