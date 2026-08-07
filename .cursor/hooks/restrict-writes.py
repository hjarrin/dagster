#!/usr/bin/env python3
"""preToolUse: allow writes only under an allowed directory structure."""

import json
import sys
from pathlib import Path

# Chosen library for this contribution scope.
ALLOWED_LIBRARY = "dagster-dbt"

ALLOWLIST = [
    ".cursor/",
    "python_modules/dagster/dagster/",
    "python_modules/dagster/dagster_tests/",
    f"python_modules/libraries/{ALLOWED_LIBRARY}/",
    "docs/sphinx/sections/api/apidocs/",
]

WRITE_TOOLS = {
    "Write",
    "StrReplace",
    "Delete",
    "EditNotebook",
}

DENY_PREFIXES = ("js_modules/",)


def _normalize_rel(path: str, workspace_roots: list[str]) -> str:
    """Return a repo-relative path using forward slashes, with trailing logic intact."""
    raw = path.strip()
    if not raw:
        return ""

    p = Path(raw).expanduser()
    if not p.is_absolute():
        return p.as_posix().lstrip("./")

    resolved = p.resolve()
    for root in workspace_roots:
        root_path = Path(root).resolve()
        try:
            return resolved.relative_to(root_path).as_posix()
        except ValueError:
            continue

    # Fall back to absolute posix if outside known roots.
    return resolved.as_posix()


def _extract_paths(tool_name: str, tool_input: dict) -> list[str]:
    if tool_name == "EditNotebook":
        keys = ("target_notebook", "path", "file_path")
    else:
        keys = ("path", "file_path")

    paths: list[str] = []
    for key in keys:
        value = tool_input.get(key)
        if isinstance(value, str) and value.strip():
            paths.append(value)
    return paths


def _is_allowed(rel: str) -> bool:
    if not rel:
        return False
    if rel.startswith(DENY_PREFIXES):
        return False
    # Explicitly deny every library package except the chosen one.
    libraries_root = "python_modules/libraries/"
    if rel.startswith(libraries_root):
        allowed_lib_prefix = f"{libraries_root}{ALLOWED_LIBRARY}/"
        return rel.startswith(allowed_lib_prefix) or rel == f"{libraries_root}{ALLOWED_LIBRARY}"
    return any(
        rel.startswith(prefix) or rel.rstrip("/") == prefix.rstrip("/") for prefix in ALLOWLIST
    )


def _deny_message(attempted: str) -> str:
    allowlist_text = ", ".join(ALLOWLIST)
    return (
        f"Write blocked for path '{attempted}'. "
        f"Allowed write paths: {allowlist_text}. "
        f"js_modules/ and all other library packages under python_modules/libraries/ "
        f"(except {ALLOWED_LIBRARY}/) are denied."
    )


def _emit(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload) + "\n")


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        # failClosed should block; emit deny-shaped output just in case.
        _emit(
            {
                "permission": "deny",
                "user_message": "restrict-writes hook received invalid JSON.",
                "agent_message": "restrict-writes hook received invalid JSON.",
            }
        )
        return 2

    tool_name = payload.get("tool_name") or ""
    tool_input = payload.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        tool_input = {}

    if tool_name not in WRITE_TOOLS:
        _emit({"permission": "allow"})
        return 0

    workspace_roots = payload.get("workspace_roots") or []
    if not isinstance(workspace_roots, list):
        workspace_roots = []
    cwd = payload.get("cwd")
    if isinstance(cwd, str) and cwd and cwd not in workspace_roots:
        workspace_roots = [*workspace_roots, cwd]

    paths = _extract_paths(tool_name, tool_input)
    if not paths:
        message = (
            f"Write blocked: {tool_name} had no recognizable path. "
            f"Allowed write paths: {', '.join(ALLOWLIST)}."
        )
        _emit(
            {
                "permission": "deny",
                "user_message": message,
                "agent_message": message,
            }
        )
        return 0

    for path in paths:
        rel = _normalize_rel(path, workspace_roots)
        if not _is_allowed(rel):
            message = _deny_message(rel or path)
            _emit(
                {
                    "permission": "deny",
                    "user_message": message,
                    "agent_message": message,
                }
            )
            return 0

    _emit({"permission": "allow"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
