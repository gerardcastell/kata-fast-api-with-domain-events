from sqlmodel.ext.asyncio.session import AsyncSession


class SQLModelRepository:
    def __init__(self, session: AsyncSession):
        self._session = session
