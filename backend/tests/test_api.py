import pytest


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_create_goal(client):
    resp = await client.post("/goals", json={"id": "g1", "description": "Build data pipeline", "source": "human"})
    assert resp.status_code == 201
    assert resp.json()["id"] == "g1"


@pytest.mark.asyncio
async def test_list_goals(client):
    await client.post("/goals", json={"id": "g2", "description": "Second goal", "source": "human"})
    resp = await client.get("/goals")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_close_goal(client):
    await client.post("/goals", json={"id": "g3", "description": "Closeable", "source": "human"})
    resp = await client.patch("/goals/g3", json={"status": "completed"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"


@pytest.mark.asyncio
async def test_list_agents(client):
    resp = await client.get("/agents")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_post_human_input(client):
    resp = await client.post("/input", json={"content": "Focus on data pipeline"})
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_list_events(client):
    resp = await client.get("/events")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_list_journal(client):
    resp = await client.get("/journal")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_list_succession(client):
    resp = await client.get("/succession")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
