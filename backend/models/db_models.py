
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    UniqueConstraint,
)

from backend.database.db import Base


class Agent(Base):
    __tablename__ = "agents"

    agent_id = Column(String(100), primary_key=True)
    public_key = Column(Text, nullable=False)
    allowed_actions = Column(JSON, nullable=False, default=list)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class Approval(Base):
    __tablename__ = "approvals"

    action_id = Column(String(100), primary_key=True)
    agent_id = Column(
        String(100),
        ForeignKey("agents.agent_id"),
        nullable=False,
    )
    action_data = Column(JSON, nullable=False)
    status = Column(String(30), nullable=False, default="pending")

    # Admin decision tracking
    approved_by = Column(String(100), nullable=True)
    rejected_by = Column(String(100), nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)
    resource = Column(Text, nullable=False)
    status = Column(String(30), nullable=False)
    reason = Column(Text, nullable=False)
    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class UsedNonce(Base):
    __tablename__ = "used_nonces"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String(100), ForeignKey("agents.agent_id"), nullable=False)
    nonce = Column(String(128), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("agent_id", "nonce", name="uq_used_nonce_agent"),
    )