#!/usr/bin/env python3
"""TrashPanda read telemetry — a post_tool_call shell hook.

Appends one JSONL line per vault-touching search_files/read_file call to
<vault>/.telemetry/reads.jsonl: timestamp, session, tool, query/path, and a
heuristic match count when the result parses as search output. Consumed by
scripts/read_telemetry.py; the weekly immune pass turns the data into
used/wasted/missed judgement (the script supplies data, the agent judges).

Wire it as: hooks.post_tool_call -> matcher "search_files|read_file".
Stdlib only, fail-open, silent on non-vault calls.
"""
import json
import os
import sys
import time

BACKSLASH = chr(92)


def _norm(path):
    """Lowercase, forward-slashed, JSON-escape-safe comparison form."""
    return str(path).lower().replace(BACKSLASH + BACKSLASH, "/").replace(BACKSLASH, "/")


def vault_root():
    if len(sys.argv) > 1:
        return os.path.expanduser(sys.argv[1])
    env = os.environ.get("TRASHPANDA_VAULT")
    if env:
        return os.path.expanduser(env)
    return os.path.join(os.path.expanduser("~"), ".hermes", "memory-vault")


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    tool = payload.get("tool_name") or ""
    args = payload.get("tool_input") or {}
    blob = _norm(json.dumps(args))
    root = vault_root()
    if "memory-vault" not in blob and _norm(root) not in blob:
        return 0  # not a vault read: log nothing (wasted-by-noise avoided)

    target = args.get("path") or args.get("pattern") or ""
    matches = None
    result = payload.get("result")
    if isinstance(result, str) and tool == "search_files":
        try:
            parsed = json.loads(result)
            total = parsed.get("total_count")
            matches = int(total) if total is not None else None
        except (json.JSONDecodeError, ValueError, TypeError, AttributeError):
            pass

    line = {
        "ts": int(time.time()),
        "session": (payload.get("session_id") or "")[:80],
        "tool": tool,
        "target": str(target)[:200],
        "pattern": str(args.get("pattern", ""))[:200] if tool == "search_files" else None,
        "matches": matches,
        "duration_ms": payload.get("duration_ms"),
    }
    log_dir = os.path.join(root, ".telemetry")
    try:
        os.makedirs(log_dir, exist_ok=True)
        with open(os.path.join(log_dir, "reads.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(line, ensure_ascii=False) + "\n")
    except OSError:
        return 0  # fail open
    return 0


if __name__ == "__main__":
    sys.exit(main())
