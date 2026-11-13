
from pathlib import Path


# All demo file operations stay inside this directory.
WORKSPACE = (
    Path(__file__).resolve().parents[2] / "agent_workspace"
).resolve()

WORKSPACE.mkdir(parents=True, exist_ok=True)


def resolve_resource(resource: str) -> Path:
    """
    Resolve a resource safely inside the agent workspace.
    Reject absolute paths and path traversal.
    """
    requested = Path(resource)

    if requested.is_absolute():
        raise ValueError("Absolute paths are not allowed")

    target = (WORKSPACE / requested).resolve()

    if not target.is_relative_to(WORKSPACE):
        raise ValueError("Access outside agent workspace is forbidden")

    if target == WORKSPACE:
        raise ValueError("A file resource is required")

    return target


def execute_action(action_data: dict) -> dict:
    """
    Execute only explicitly supported, restricted demo actions.
    """

    action = action_data.get("action")
    resource = action_data.get("resource")

    try:
        if not isinstance(resource, str) or not resource.strip():
            raise ValueError("Invalid resource")

        if action == "read_file":
            target = resolve_resource(resource)

            if not target.is_file():
                raise FileNotFoundError("File not found")

            return {
                "status": "executed",
                "result": target.read_text(encoding="utf-8"),
            }

        elif action == "write_file":
            target = resolve_resource(resource)
            target.parent.mkdir(parents=True, exist_ok=True)

            # Demo content only; no agent-supplied arbitrary payload.
            target.write_text(
                "Written securely by Freaknssential demo executor.",
                encoding="utf-8",
            )

            return {
                "status": "executed",
                "result": "Demo file written successfully",
            }

        elif action == "delete_file":
            target = resolve_resource(resource)

            if not target.is_file():
                raise FileNotFoundError("File not found")

            target.unlink()

            return {
                "status": "executed",
                "result": "Demo file deleted successfully",
            }

        elif action == "send_email":
            return {
                "status": "simulated",
                "result": "Email sending is disabled in demo mode",
            }

        elif action == "access_database":
            return {
                "status": "simulated",
                "result": "Database access is disabled in demo mode",
            }

        else:
            return {
                "status": "blocked",
                "reason": "Unsupported action",
            }

    except (ValueError, OSError) as error:
        return {
            "status": "execution_failed",
            "reason": str(error),
        }
