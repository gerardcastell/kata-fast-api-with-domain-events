from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from sqlmodel import SQLModel

from app.config.settings import settings
from app.contexts.customers.infrastructure.api import routes as customer_module
from app.shared.containers.main import Container
from app.shared.infrastructure.api.health import routes as health_module


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    container: Container = app.container
    if container.config.create_tables_on_startup():
        database = container.database()
        async with database._async_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
    # Hand control back to FastAPI while the app is running
    yield
    # Shutdown: ensure DB engine is cleanly disposed to avoid event loop warnings
    database = container.database()
    await database.dispose()


def create_app():
    container = Container()
    container.config.from_pydantic(settings)
    app = FastAPI(
        title=settings.app_title,
        debug=settings.debug,
        dependencies=[],
        lifespan=lifespan,
    )
    app.container = container

    # Wire and include the routers
    modules = [customer_module, health_module]
    container.wire(modules=modules)

    for module in modules:
        app.include_router(module.router)

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
