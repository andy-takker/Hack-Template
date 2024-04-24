from http import HTTPStatus

from aiohttp.test_utils import TestClient

API_URL = "/api/v1/monitoring/ping"


async def test_ping_ok(api_client: TestClient):
    response = await api_client.get(API_URL)
    assert response.status == HTTPStatus.OK
    assert await response.json() == {"db": True}
