from datetime import datetime
from pydantic import BaseModel, Field


class Goal(BaseModel):
    id: str
    description: str
    status: str = "active"
    source: str = "human"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: datetime | None = None
    closed_by: str | None = None


class Agent(BaseModel):
    id: str
    name: str
    role: str
    layer: str
    model: str
    status: str = "idle"
    config: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    retired_at: datetime | None = None


class JournalEntry(BaseModel):
    id: int | None = None
    miles_id: str
    type: str
    content: str
    context: str | None = None
    goal_id: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Task(BaseModel):
    id: str
    goal_id: str | None = None
    assigned_to: str | None = None
    validator: str | None = None
    description: str
    status: str = "pending"
    result: str | None = None
    summary: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None


class Feedback(BaseModel):
    id: str
    author: str
    type: str
    raw_content: str
    external_validator_summary: str | None = None
    miles_response: str | None = None
    goal_id: str | None = None
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AuditRecord(BaseModel):
    id: str
    auditor_id: str
    miles_id: str
    scope: str
    findings: str | None = None
    miles_response: str | None = None
    status: str = "running"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None


class ScoutingMission(BaseModel):
    id: str
    hunter_id: str
    source: str
    topic: str
    raw_findings: str | None = None
    summary: str | None = None
    validator: str | None = None
    goal_id: str | None = None
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None


class SuccessionRecord(BaseModel):
    id: int | None = None
    retired_id: str
    promoted_id: str
    new_shadow_id: str
    compaction: str | None = None
    journal_start: int | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Event(BaseModel):
    id: int | None = None
    agent_id: str
    type: str
    content: str
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
