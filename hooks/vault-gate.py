#!/usr/bin/env python3
"""TrashPanda grep-first gate — a shell-hook pair in one file.

Wired as TWO pre_tool_call entries (see README-SETUP step 5b):
  matcher "search_files|read_file"  -> records that this session searched the vault
  matcher "terminal|execute_code|write_file|patch|browser_exec"
                                    -> blocks the FIRST gated call of a session
                                       that hasn't searched yet, with an
                                       instruction message to the model.
After one nudge the session passes freely: the gate steers, it never wedges.
Fail-open by default (do NOT set fail_closed on this hook).

State lives in <vault>/.gate/<session_id>.{searched,warned}. Vault root comes
from argv[1], TRASHPANDA_VAULT, or ~/.hermes/memory-vault.
Payload on stdin / directive on stdout per the Hermes shell-hook wire format.
Exit 0 with no stdout = silent pass.
"""
import json
import os
import sys

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
        return 0  # fail open
    event = payload.get("hook_event_name", "")
    tool = payload.get("tool_name") or ""
    args = payload.get("tool_input") or {}
    session = (payload.get("session_id") or payload.get("extra", {}).get("task_id") or "anon")
    session = "".join(c if c.isalnum() or c in "-_" else "_" for c in str(session))[:80]

    if event != "pre_tool_call":
        return 0

    root = vault_root()
    gate = os.path.join(root, ".gate")
    try:
        os.makedirs(gate, exist_ok=True)
    except OSError:
        return 0  # unwritable vault -> fail open

    searched = os.path.join(gate, session + ".searched")
    warned = os.path.join(gate, session + ".warned")

    # Observer half: did this call touch the vault?
    if tool in ("search_files", "read_file"):
        blob = _norm(json.dumps(args))
        if "memory-vault" in blob or _norm(root) in blob:
            open(searched, "a").close()
        return 0

    # Gate half: first real action of an unsearched session gets one nudge.
    if os.path.exists(searched) or os.path.exists(warned):
        return 0
    open(warned, "a").close()
    print(json.dumps({"action": "block", "message": (
        "TrashPanda: memory-vault not searched this session. Before acting, "
        "run search_files over %s for this request's keywords (layer 1), then "
        "INDEX.md if unsure. Retry this tool call afterwards; the nudge fires "
        "once per session." % root)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
