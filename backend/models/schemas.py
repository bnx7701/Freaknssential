
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


class AgentRegistration(BaseModel):
    agent_id: str = Field(min_length=1, max_length=100)
    public_key: str = Field(min_length=1)
    allowed_actions: list[str] = Field(default_factory=list)


class ActionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_id: str
    action: Literal[
        "read_file",
        "write_file",
        "delete_file",
        "send_email",
        "access_database",
    ]
    resource: str = Field(min_length=1, max_length=500)
    nonce: str = Field(min_length=32, max_length=128)
    signature: str = Field(min_length=1)

    
class ActionResponse(BaseModel):
    status: Literal[
        "authorized",
        "blocked",
        "pending_approval",
    ]
    reason: str
    action_id: str | None = None


class ApprovalResponse(BaseModel):
    action_id: str
    status: Literal["approved", "rejected", "not_found"]


class AuditEvent(BaseModel):
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    agent_id: str
    action: str
    resource: str
    status: str
    reason: str
