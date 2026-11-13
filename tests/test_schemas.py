
import pytest
from pydantic import ValidationError

from backend.models.schemas import (
    AgentRegistration,
    ActionRequest,
)


def test_agent_registration():
    agent = AgentRegistration(
        agent_id="agent_001",
        public_key="test-public-key",
        allowed_actions=["read"],
    )

    assert agent.agent_id == "agent_001"
    assert "read" in agent.allowed_actions


def test_valid_action_request():
    action = ActionRequest(
        agent_id="agent_001",
        action="read_file",
        resource="report.txt",
        signature="test-signature",
    )

    assert action.action == "read_file"


def test_invalid_action_is_rejected():
    with pytest.raises(ValidationError):
        ActionRequest(
            agent_id="agent_001",
            action="execute_malware",
            resource="system",
            signature="test-signature",
        )


def test_extra_fields_are_rejected():
    with pytest.raises(ValidationError):
        ActionRequest(
            agent_id="agent_001",
            action="read_file",
            resource="report.txt",
            signature="test-signature",
            admin=True,
        )
