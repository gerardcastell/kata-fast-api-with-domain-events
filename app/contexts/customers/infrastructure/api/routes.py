from typing import List, Optional

from dependency_injector.wiring import inject, Provide

from fastapi import APIRouter, Depends, HTTPException, status

from app.contexts.customers.application.customer_creator import CustomerCreator
from app.contexts.customers.application.customer_searcher import CustomerSearcher
from app.contexts.customers.domain.entities.customer import Customer
from app.shared.containers.main import Container

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("/", response_model=Customer, status_code=status.HTTP_201_CREATED)
@inject
async def create_customer(
    name: str,
    email: str,
    id: Optional[str] = None,
    activePoliciesCount: Optional[int] = None,
    customer_creator: CustomerCreator = Depends(
        Provide[Container.customer_services.customer_creator]
    ),
):
    try:
        # Only pass id if it's not None, let the entity generate it if needed
        return await customer_creator.create(id=id, name=name, email=email, activePoliciesCount=activePoliciesCount )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[Customer])
@inject
async def list_customers(
    customer_searcher: CustomerSearcher = Depends(
        Provide[Container.customer_services.customer_searcher]
    ),
):
    try:
        return await customer_searcher.search_all()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{customer_id}", response_model=Customer)
@inject
async def get_customer(
    customer_id: str,
    customer_searcher: CustomerSearcher = Depends(
        Provide[Container.customer_services.customer_searcher]
    ),
):
    customer = await customer_searcher.search_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer
