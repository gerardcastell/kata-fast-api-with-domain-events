from dependency_injector.wiring import inject, Provide
from sqlalchemy import text

from fastapi import APIRouter, Depends

from app.shared.containers.main import Container
from worker.tasks.unstable_task import unstable_task

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
def live():
    return {"status": "ok"}


@router.get("/ready")
@inject
async def ready(
    session_factory=Depends(Provide(Container.database.provided.session_factory)),
):
    async with session_factory() as session:
        await session.exec(text("SELECT 1"))
    return {"status": "ok"}


@router.get("/test-celery")
async def run_task(x: int):
    unstable_task.delay(x)
    return {"success": "sisi"}
