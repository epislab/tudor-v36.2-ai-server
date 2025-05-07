import pytest
from httpx import AsyncClient
from app.main import app

@pytest.fixture
async def async_client():
    """비동기 클라이언트 픽스처"""
    async with AsyncClient(app=app, base_url="http://localhost:7000") as client:
        yield client

@pytest.mark.asyncio
async def test_read_test(async_client):
    """테스트 엔드포인트 테스트 - 비동기 방식"""
    response = await async_client.get("/test")
    assert response.status_code == 200
    assert response.json() == {"message": "테스트 파일입니다 3."}
