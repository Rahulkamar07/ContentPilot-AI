import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_liveness_probe(async_client: AsyncClient) -> None:
    """Verifies GET /api/v1/health/live returns 200 OK and HEALTHY status."""
    response = await async_client.get("/api/v1/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "service" in data


@pytest.mark.asyncio
async def test_version_endpoint(async_client: AsyncClient) -> None:
    """Verifies GET /api/v1/version returns 200 OK and version info."""
    response = await async_client.get("/api/v1/version")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "project" in data
    assert data["project"] == "ContentPilot AI"
