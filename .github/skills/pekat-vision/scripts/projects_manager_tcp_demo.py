"""Projects Manager Simple TCP helper with read-only defaults."""
from __future__ import annotations

import socket

READ_ONLY_COMMANDS = {"status"}
MUTATING_COMMANDS = {"start", "stop", "switch"}


def build_command(action: str, project_path: str) -> str:
    action = action.strip().lower()
    if action not in READ_ONLY_COMMANDS | MUTATING_COMMANDS:
        raise ValueError(f"unsupported action: {action}")
    if not project_path.strip() or "\n" in project_path or "\r" in project_path:
        raise ValueError("project_path must be a non-empty single line")
    return f"{action}:{project_path}"


def send_command(
    host: str,
    port: int,
    action: str,
    project_path: str,
    *,
    allow_mutation: bool = False,
    timeout_s: float = 3.0,
    recv_bytes: int = 256,
) -> str:
    action = action.strip().lower()
    if action in MUTATING_COMMANDS and not allow_mutation:
        raise PermissionError(f"{action} requires allow_mutation=True and explicit operator approval")
    command = build_command(action, project_path)
    with socket.create_connection((host, int(port)), timeout=timeout_s) as sock:
        sock.settimeout(timeout_s)
        sock.sendall(command.encode("utf-8"))
        response = sock.recv(recv_bytes)
    if not response:
        raise RuntimeError("Projects Manager returned an empty response")
    return response.decode("utf-8", errors="strict").strip()
