from fastapi import APIRouter
from pydantic import BaseModel

from app.db import queries
from app.models.schemas import Event

router = APIRouter()


class HumanInput(BaseModel):
    content: str


@router.post("/input", status_code=201)
async def post_input(req: HumanInput):
    event = Event(agent_id="human", type="human_input", content=req.content)
    event_id = await queries.create_event(event)
    return {"event_id": event_id, "content": req.content}
