
import json

from backend.core import audit


def test_record_and_read_audit_log(tmp_path, monkeypatch):
    test_file = tmp_path / "audit_logs.jsonl"

    monkeypatch.setattr(audit, "AUDIT_FILE", test_file)

    action = {
        "agent_id": "agent_001",
        "action": "delete_file",
        "resource": "important.txt",
    }

    result = {
        "status": "blocked",
        "reason": "Permission denied",
    }

    event = audit.record_event(action, result)

    assert event["status"] == "blocked"
    assert event["agent_id"] == "agent_001"

    logs = audit.read_audit_logs()

    assert len(logs) == 1
    assert logs[0]["reason"] == "Permission denied"


def test_audit_file_contains_valid_json(tmp_path, monkeypatch):
    test_file = tmp_path / "audit_logs.jsonl"

    monkeypatch.setattr(audit, "AUDIT_FILE", test_file)

    audit.record_event(
        {"agent_id": "agent_002", "action": "read_file"},
        {"status": "authorized", "reason": "Checks passed"},
    )

    with test_file.open(encoding="utf-8") as file:
        event = json.loads(file.readline())

    assert event["agent_id"] == "agent_002"
    assert event["status"] == "authorized"
