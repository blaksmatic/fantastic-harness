import asyncio
import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.db.connection import close_db, get_db, init_db


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_db(tmp_path) -> AsyncGenerator[str, None]:
    db_path = str(tmp_path / "test.db")
    os.environ["HARNESS_DB_PATH"] = db_path
    from app.config import Settings
    import app.config
    app.config.settings = Settings(db_path=db_path)
    await init_db()
    yield db_path
    await close_db()


@pytest_asyncio.fixture
async def client(test_db) -> AsyncGenerator[AsyncClient, None]:
    from app.main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
