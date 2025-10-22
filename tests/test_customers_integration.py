"""Integration tests for customer functionality."""

import uuid

import pytest
from httpx import AsyncClient, QueryParams
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contexts.customers.infrastructure.persistence.models.customer import (
    CustomerModel,
)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_customer_integration(
    async_test_client: AsyncClient, test_db_session: AsyncSession
):
    """Test creating a customer through the API with database integration."""
    customer_data = QueryParams(
        {"name": "John Doe", "email": "john.doe@example.com", "activePoliciesCount": 0}
    )

    # Create customer via API
    response = await async_test_client.post("/customers/", params=customer_data)
    if response.status_code != 201:
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
    assert response.status_code == 201

    customer_response = response.json()
    assert customer_response["name"] == customer_data["name"]
    assert customer_response["email"] == customer_data["email"]
    assert customer_response["activePoliciesCount"] == customer_data["activePoliciesCount"]
    assert "id" in customer_response

    # Verify customer was saved to database

    result = await test_db_session.execute(
        select(CustomerModel).where(CustomerModel.id == customer_response["id"])
    )
    db_customer = result.scalar_one_or_none()

    assert db_customer is not None
    assert db_customer.name == customer_data["name"]
    assert db_customer.email == customer_data["email"]
    assert db_customer.activePoliciesCount == customer_data["activePoliciesCount"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_customer_integration(
    async_test_client: AsyncClient, test_db_session: AsyncSession
):
    """Test retrieving a customer through the API with database integration."""
    # First create a customer in the database
    customer = CustomerModel(
        id=str(uuid.uuid4()),
        name="Jane Smith",
        email="jane.smith@example.com",
        activePoliciesCount=0,
    )
    test_db_session.add(customer)
    await test_db_session.commit()
    await test_db_session.refresh(customer)

    # Retrieve customer via API
    response = await async_test_client.get(f"/customers/{customer.id}")
    assert response.status_code == 200

    customer_response = response.json()
    assert customer_response["id"] == customer.id
    assert customer_response["name"] == customer.name
    assert customer_response["email"] == customer.email
    assert customer_response["activePoliciesCount"] == customer.activePoliciesCount


@pytest.mark.integration
@pytest.mark.asyncio
async def test_list_customers_integration(
    async_test_client: AsyncClient, test_db_session: AsyncSession
):
    """Test listing customers through the API with database integration."""
    # Create multiple customers in the database
    customers_data = [
        {"name": "Customer 1", "email": "customer1@example.com", "activePoliciesCount": 0},
        {"name": "Customer 2", "email": "customer2@example.com", "activePoliciesCount": 1},
        {"name": "Customer 3", "email": "customer3@example.com", "activePoliciesCount": 2},
    ]

    for customer_data in customers_data:
        customer = CustomerModel(
            id=str(uuid.uuid4()),
            name=customer_data["name"],
            email=customer_data["email"],
            activePoliciesCount=customer_data["activePoliciesCount"],
        )
        test_db_session.add(customer)

    await test_db_session.commit()

    # Retrieve customers via API
    response = await async_test_client.get("/customers/")
    assert response.status_code == 200

    customers_response = response.json()
    assert len(customers_response) >= len(customers_data)

    # Verify all created customers are in the response
    customer_names = [c["name"] for c in customers_response]
    for customer_data in customers_data:
        assert customer_data["name"] in customer_names
