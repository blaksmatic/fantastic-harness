from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db import queries
from app.models.schemas import Goal

router = APIRouter()


class CreateGoalRequest(BaseModel):
    id: str
    description: str
    source: str = "human"


class UpdateGoalRequest(BaseModel):
    status: str | None = None
    description: str | None = None


@router.post("/goals", status_code=201)
async def create_goal(req: CreateGoalRequest):
    goal = Goal(id=req.id, description=req.description, source=req.source)
    await queries.create_goal(goal)
    return {"id": goal.id, "description": goal.description, "status": goal.status}


@router.get("/goals")
async def list_goals(status: str | None = None):
    return await queries.list_goals(status=status)


@router.patch("/goals/{goal_id}")
async def update_goal(goal_id: str, req: UpdateGoalRequest):
    goal = await queries.get_goal(goal_id)
    if not goal:
        raise HTTPException(404, "Goal not found")
    updates = {}
    if req.status:
        updates["status"] = req.status
        if req.status == "completed":
            updates["closed_at"] = datetime.utcnow().isoformat()
            updates["closed_by"] = "human"
    if req.description:
        updates["description"] = req.description
    await queries.update_goal(goal_id, **updates)
    return await queries.get_goal(goal_id)
