
from fastapi import APIRouter
from backend.core.audit import read_audit_logs, verify_audit_logs

router = APIRouter(prefix="/logs", tags=["Audit Logs"])


@router.get("/")
def get_audit_logs():
    return {
        "total_events": len(read_audit_logs()),
        "events": read_audit_logs()
    }


@router.get("/verify")
def verify_logs():
    return verify_audit_logs()
