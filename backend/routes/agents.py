
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.db import get_db
from backend.models.db_models import Agent, AuditEvent
from backend.models.schemas import AgentRegistration

router = APIRouter(prefix="/agents", tags=["Agents"])


# =========================================================
# AGENT RISK SCORING
# =========================================================

def calculate_agent_risk(db: Session, agent_id: str):

    events = db.query(AuditEvent).filter(
        AuditEvent.agent_id == agent_id
    ).all()

    risk_score = 0
    permission_violations = 0
    invalid_signatures = 0
    replay_attacks = 0

    for event in events:

        reason = (event.reason or "").lower()

        if "permission denied" in reason:
            risk_score += 20
            permission_violations += 1

        elif "invalid digital signature" in reason:
            risk_score += 30
            invalid_signatures += 1

        elif "replay detected" in reason:
            risk_score += 25
            replay_attacks += 1

    risk_score = min(risk_score, 100)

    if risk_score >= 70:
        risk_level = "CRITICAL"
    elif risk_score >= 40:
        risk_level = "HIGH"
    elif risk_score >= 20:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "security_events": {
            "permission_violations": permission_violations,
            "invalid_signatures": invalid_signatures,
            "replay_attacks": replay_attacks,
        },
    }


# =========================================================
# REGISTER AGENT
# =========================================================

@router.post("/register", status_code=201)
def register_agent(
    agent_data: AgentRegistration,
    db: Session = Depends(get_db),
):

    existing_agent = db.query(Agent).filter(
        Agent.agent_id == agent_data.agent_id
    ).first()

    if existing_agent:
        raise HTTPException(
            status_code=409,
            detail="Agent already registered",
        )

    new_agent = Agent(
        agent_id=agent_data.agent_id,
        public_key=agent_data.public_key,
        allowed_actions=agent_data.allowed_actions,
    )

    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)

    return {
        "message": "Agent registered successfully",
        "agent_id": new_agent.agent_id,
        "allowed_actions": new_agent.allowed_actions,
    }


# =========================================================
# GET SINGLE AGENT
# =========================================================

@router.get("/{agent_id}")
def get_agent(
    agent_id: str,
    db: Session = Depends(get_db),
):

    agent = db.query(Agent).filter(
        Agent.agent_id == agent_id
    ).first()

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found",
        )

    risk = calculate_agent_risk(db, agent_id)

    return {
        "agent_id": agent.agent_id,
        "allowed_actions": agent.allowed_actions,
        "public_key": agent.public_key,
        **risk,
    }


# =========================================================
# GET ALL AGENTS WITH RISK SCORES
# =========================================================

@router.get("/")
def get_all_agents(db: Session = Depends(get_db)):

    agents = db.query(Agent).all()

    results = []

    for agent in agents:

        risk = calculate_agent_risk(
            db,
            agent.agent_id,
        )

        results.append({
            "agent_id": agent.agent_id,
            "allowed_actions": agent.allowed_actions,
            "created_at": agent.created_at,
            **risk,
        })

    return results
