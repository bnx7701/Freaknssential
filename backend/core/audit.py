
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

AUDIT_FILE = Path(__file__).resolve().parents[2] / "audit_logs.jsonl"

GENESIS_HASH = "0" * 64


def calculate_hash(event: dict) -> str:
    """Calculate SHA-256 hash of an event."""
    event_data = {
        key: value
        for key, value in event.items()
        if key != "hash"
    }

    canonical_data = json.dumps(
        event_data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    )

    return hashlib.sha256(canonical_data.encode("utf-8")).hexdigest()


def verify_audit_logs() -> dict:
    """Verify the integrity of the hash-chained audit log."""
    if not AUDIT_FILE.exists():
        return {
            "valid": True,
            "total_events": 0,
            "message": "No audit logs found"
        }

    previous_hash = GENESIS_HASH
    total_events = 0

    with AUDIT_FILE.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                return {
                    "valid": False,
                    "line": line_number,
                    "message": "Invalid JSON in audit log"
                }

            stored_hash = event.get("hash")

            if event.get("previous_hash") != previous_hash:
                return {
                    "valid": False,
                    "line": line_number,
                    "message": "Previous hash mismatch"
                }

            calculated_hash = calculate_hash(event)

            if stored_hash != calculated_hash:
                return {
                    "valid": False,
                    "line": line_number,
                    "message": "Event hash mismatch"
                }

            previous_hash = stored_hash
            total_events += 1

    return {
        "valid": True,
        "total_events": total_events,
        "message": "Audit log integrity verified"
    }


def record_event(action: dict, result: dict) -> dict:
    """Record an event linked to the previous audit entry."""

    verification = verify_audit_logs()

    if not verification["valid"]:
        raise ValueError(
            "Audit log integrity check failed. "
            "New events cannot be appended."
        )

    previous_hash = GENESIS_HASH

    if AUDIT_FILE.exists():
        with AUDIT_FILE.open("r", encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    previous_hash = json.loads(line)["hash"]

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent_id": action.get("agent_id", "unknown"),
        "action": action.get("action", "unknown"),
        "resource": action.get("resource", "unknown"),
        "status": result.get("status", "unknown"),
        "reason": result.get(
            "reason",
            result.get("result", "unknown")
        ),
        "previous_hash": previous_hash
    }

    event["hash"] = calculate_hash(event)

    with AUDIT_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event, ensure_ascii=False) + "\n")

    return event


def read_audit_logs() -> list[dict]:
    if not AUDIT_FILE.exists():
        return []

    events = []

    with AUDIT_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                events.append(json.loads(line))

    return events
