from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from sqlalchemy import text

from app.shared.containers.main import Container

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
