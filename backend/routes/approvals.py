
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.db import get_db
from backend.models.db_models import (
    Approval,
    AuditEvent as AuditEventModel,
)
from backend.core.executor import execute_action
from backend.core.audit import record_event
from backend.core.auth import get_current_admin

router = APIRouter(prefix="/approvals", tags=["Approvals"])


@router.get("/pending")
def get_pending_approvals(
    db: Session = Depends(get_db),
    admin: str = Depends(get_current_admin),
):
    approvals = (
        db.query(Approval)
        .filter(Approval.status == "pending")
        .all()
    )

    return [
        {
            "action_id": approval.action_id,
            "agent_id": approval.agent_id,
            "action_data": approval.action_data,
            "status": approval.status,
            "created_at": approval.created_at,
        }
        for approval in approvals
    ]


@router.post("/{action_id}/approve")
def approve_request(
    action_id: str,
    db: Session = Depends(get_db),
    admin: str = Depends(get_current_admin),
):
    approval = (
        db.query(Approval)
        .filter(Approval.action_id == action_id)
        .first()
    )

    if not approval:
        raise HTTPException(
            status_code=404,
            detail="Approval request not found",
        )

    if approval.status != "pending":
        raise HTTPException(
            status_code=409,
            detail="Approval request already processed",
        )

    # Record the authenticated admin's decision.
    approval.status = "approved"
    approval.approved_by = admin
    approval.processed_at = datetime.now(timezone.utc)

    db.commit()

    # Execute only after approval.
    execution_result = execute_action(approval.action_data)

    db_event = AuditEventModel(
        agent_id=approval.agent_id,
        action=approval.action_data.get("action", "unknown"),
        resource=approval.action_data.get("resource", "unknown"),
        status=execution_result.get("status", "unknown"),
        reason=execution_result.get(
            "reason",
            execution_result.get("result", "No details"),
        ),
    )

    db.add(db_event)

    record_event(approval.action_data, execution_result)

    db.commit()

    return {
        "action_id": action_id,
        "status": "approved",
        "approved_by": admin,
        "processed_at": approval.processed_at,
        "execution": execution_result,
    }


@router.post("/{action_id}/reject")
def reject_request(
    action_id: str,
    db: Session = Depends(get_db),
    admin: str = Depends(get_current_admin),
):
    approval = (
        db.query(Approval)
        .filter(Approval.action_id == action_id)
        .first()
    )

    if not approval:
        raise HTTPException(
            status_code=404,
            detail="Approval request not found",
        )

    if approval.status != "pending":
        raise HTTPException(
            status_code=409,
            detail="Approval request already processed",
        )

    # Record the authenticated admin's rejection.
    approval.status = "rejected"
    approval.rejected_by = admin
    approval.processed_at = datetime.now(timezone.utc)

    db_event = AuditEventModel(
        agent_id=approval.agent_id,
        action=approval.action_data.get("action", "unknown"),
        resource=approval.action_data.get("resource", "unknown"),
        status="rejected",
        reason="Human approval rejected",
    )

    db.add(db_event)

    record_event(
        approval.action_data,
        {
            "status": "rejected",
            "reason": "Human approval rejected",
        },
    )

    db.commit()

    return {
        "action_id": action_id,
        "status": "rejected",
        "rejected_by": admin,
        "processed_at": approval.processed_at,
        "message": "Action was rejected and not executed",
    }
