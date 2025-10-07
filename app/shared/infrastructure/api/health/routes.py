from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession

from app.shared.containers.main import Container

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
def live():
    return {"status": "ok"}


@router.get("/ready")
@inject
async def ready(
    session: AsyncSession = Depends(Provide(Container.persistence.session)),
):
    await session.exec(text("SELECT 1"))
    return {"status": "ok"}
