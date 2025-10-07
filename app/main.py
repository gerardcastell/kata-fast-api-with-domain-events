from contextlib import asynccontextmanager

import uvicorn
from fastapi import Depends, FastAPI
from sqlmodel import SQLModel

from app.contexts.customers.infrastructure.api import routes as customer_module
from app.shared.containers.main import Container
from app.shared.infrastructure.api.health import routes as health_module

from .dependencies import get_query_token


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    container: Container = app.container
    if container.core.config.database.create_tables_on_startup():
        async with container.persistence.engine().begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
    yield
    # Shutdown (if needed)


def create_app(config_path: str):
    container = Container()
    container.core.config_path.override(config_path)
    container.core.config.from_dict(container.core.config_loader())

    app = FastAPI(
        title="Insurance API",
        dependencies=[Depends(get_query_token)],
        lifespan=lifespan,
    )
    app.container = container

    # Optional gzip
    if container.core.config.api.compression.gzip():
        from starlette.middleware.gzip import GZipMiddleware

        app.add_middleware(GZipMiddleware, minimum_size=500)

    # Wire and include the routers
    modules = [customer_module, health_module]
    container.wire(modules=modules)

    for module in modules:
        app.include_router(module.router)

    return app


app = create_app("app/config/default.yml")
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)