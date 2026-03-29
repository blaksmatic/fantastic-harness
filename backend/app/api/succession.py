from fastapi import APIRouter

from app.db import queries

router = APIRouter()


@router.get("/succession")
async def list_succession():
    return await queries.list_successions()
