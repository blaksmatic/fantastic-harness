from fastapi import APIRouter
from pydantic import BaseModel

from app.db import queries
from app.models.schemas import Event

router = APIRouter()


class TriggerRequest(BaseModel):
    name: str = "maurissa"


@router.post("/adversaries/trigger", status_code=202)
async def trigger_adversary(req: TriggerRequest):
    event = Event(agent_id="human", type="human_input",
                  content=f"TRIGGER_ADVERSARY:{req.name}",
                  metadata={"trigger": True, "adversary": req.name})
    await queries.create_event(event)
    return {"status": "queued", "adversary": req.name}
