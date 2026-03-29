from fastapi import APIRouter

from app.db import queries

router = APIRouter()


@router.get("/journal")
async def list_journal(miles_id: str | None = None, since_id: int | None = None, limit: int = 100):
    return await queries.get_journal_entries(miles_id=miles_id, since_id=since_id, limit=limit)
