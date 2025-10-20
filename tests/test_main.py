import pytest
from httpx import AsyncClient

from fastapi.testclient import TestClient


@pytest.mark.unit
def test_health_live(test_client: TestClient):
    """Test health live endpoint."""
    response = test_client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.unit
def test_health_ready(test_client: TestClient):
    """Test health ready endpoint."""
    response = test_client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
@pytest.mark.unit
async def test_health_live_async(async_test_client: AsyncClient):
    """Test health live endpoint with async client."""
    response = await async_test_client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
@pytest.mark.unit
async def test_health_ready_async(async_test_client: AsyncClient):
    """Test health ready endpoint with async client."""
    response = await async_test_client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
