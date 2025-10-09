from typing import Annotated

from dependency_injector import containers, providers

from app.contexts.customers.container.customer_services import CustomerServices

from .core import Core
from .persistence import Persistence


class Container(containers.DeclarativeContainer):
    core = providers.Container(Core)
    persistence = providers.Container(Persistence, core=core)

    customer_services = providers.Container(CustomerServices, persistence=persistence)
    



