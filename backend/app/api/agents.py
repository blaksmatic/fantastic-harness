from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db import queries

router = APIRouter()


class UpdateAgentConfig(BaseModel):
    config: dict | None = None


@router.get("/agents")
async def list_agents(layer: str | None = None, status: str | None = None):
    return await queries.list_agents(layer=layer, status=status)


@router.patch("/agents/{agent_id}/config")
async def update_agent_config(agent_id: str, req: UpdateAgentConfig):
    agent = await queries.get_agent(agent_id)
    if not agent:
        raise HTTPException(404, "Agent not found")
    if req.config is not None:
        await queries.update_agent(agent_id, config=req.config)
    return await queries.get_agent(agent_id)
