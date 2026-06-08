import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_register():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/auth/register", json={"email": "test@example.com", "password": "pass", "tenant_id": 1})
        assert response.status_code == 200