import asyncio
import json

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from app.db import queries

router = APIRouter()


@router.get("/events")
async def list_events(limit: int = 50, since_id: int | None = None, type: str | None = None):
    return await queries.list_events(limit=limit, since_id=since_id, event_type=type)


@router.get("/events/stream")
async def event_stream():
    async def generate():
        last_id = 0
        while True:
            events = await queries.list_events(since_id=last_id, limit=10)
            for event in reversed(events):
                last_id = max(last_id, event["id"])
                yield {"event": "message", "data": json.dumps(event)}
            await asyncio.sleep(2)
    return EventSourceResponse(generate())
