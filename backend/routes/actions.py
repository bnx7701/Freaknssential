
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.database.db import get_db
from backend.models.db_models import (
    Agent,
    Approval,
    UsedNonce,
    AuditEvent as AuditEventModel,
)
from backend.models.schemas import ActionRequest
from backend.core.security import evaluate_action
from backend.core.signatures import verify_action_signature
from backend.core.audit import record_event

router = APIRouter(prefix="/actions", tags=["Actions"])


@router.post("/submit")
def submit_action(request: ActionRequest, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(
        Agent.agent_id == request.agent_id
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent is not registered")

    action_data = {
        "agent_id": request.agent_id,
        "action": request.action,
        "resource": request.resource,
        "nonce": request.nonce,
    }

    signature_valid = verify_action_signature(
        action_data,
        request.signature,
        agent.public_key,
    )

    if signature_valid:
        db.add(UsedNonce(
            agent_id=request.agent_id,
            nonce=request.nonce,
        ))

        try:
            db.flush()
        except IntegrityError:
            db.rollback()

            result = {
                "status": "blocked",
                "reason": "Replay detected: nonce already used",
            }

            db.add(AuditEventModel(
                agent_id=request.agent_id,
                action=request.action,
                resource=request.resource,
                status=result["status"],
                reason=result["reason"],
            ))

            db.commit()
            record_event(action_data, result)

            return {
                "agent_id": request.agent_id,
                "action": request.action,
                "resource": request.resource,
                **result,
            }

    result = evaluate_action(
        action=action_data,
        signature=request.signature,
        public_key=agent.public_key,
        allowed_actions=agent.allowed_actions,
    )

    if result["status"] == "pending_approval":
        db.add(Approval(
            action_id=result["action_id"],
            agent_id=request.agent_id,
            action_data=action_data,
            status="pending",
        ))

    db.add(AuditEventModel(
        agent_id=request.agent_id,
        action=request.action,
        resource=request.resource,
        status=result["status"],
        reason=result["reason"],
    ))

    db.commit()
    record_event(action_data, result)

    return {
        "agent_id": request.agent_id,
        "action": request.action,
        "resource": request.resource,
        **result,
    }
