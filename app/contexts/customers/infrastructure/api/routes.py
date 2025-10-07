from typing import List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from app.contexts.customers.application.customer_creator import CustomerCreator
from app.contexts.customers.application.customer_searcher import CustomerSearcher
from app.contexts.customers.domain.entities.customer import Customer
from app.shared.containers.main import Container

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post(
    "/", response_model=Customer, status_code=status.HTTP_201_CREATED
)
@inject
def create_customer(
    name: str,
    email: str,
    id: Optional[str] = None,
    activePoliciesCount: Optional[int] = 0,
    customer_creator: CustomerCreator = Depends(Provide(Container.customer_services.customer_creator)),
):
    try:
        return customer_creator.create(
            id=id, name=name, email=email, activePoliciesCount=activePoliciesCount
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[Customer])
@inject
def list_customers(
    customer_searcher: CustomerSearcher = Depends(Provide(Container.customer_services.customer_searcher)),
):
    try:
        return customer_searcher.search_all()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{customer_id}", response_model=Customer)
@inject
def get_customer(
    customer_id: str,
    customer_searcher: CustomerSearcher = Depends(Provide(Container.customer_services.customer_searcher)),
):
    customer = customer_searcher.search_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer
