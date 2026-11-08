---
date: 2026-11-08
type: reference
keywords: [field-notes, v1.1, hooks, telemetry, ground-truth]
---
# Field notes — v1.1

v1.1 incorporates feedback from a community member running an independent
file-based agent-memory deployment in production (architecture independently
converged: keyword search, one hot state file, ritual distillation, no
vectors — a third independent arrival at this design is strong evidence it's
a local minimum). Their setup's specifics stay private; the ideas are
general. Three upgrades adopted:

## 1. Grep-first is enforced, not encouraged (tool-call gate)

v1.0 relied on convention: an injected pointer saying "grep the vault
first." Convention fails exactly when the agent is hurried — the documented
failure mode of interactive mediums.

**Hermes exposes the mechanism to make it structural:** `hooks:` →
`pre_tool_call` (with a tool-name `matcher`) runs a script per tool call,
JSON payload on stdin; the script's stdout JSON can **block the call or
inject context into the next LLM turn**. Sketch:

```
hooks:
  pre_tool_call:
    - matcher: "terminal|execute_code|browser_exec"
      command: "~/.hermes/hooks/vault-gate.py"   # consent needed on first
                                                  # use (TTY); --accept-hooks
                                                  # / HERMES_ACCEPT_HOOKS=1
                                                  # for headless runs
```

**Shipped as `hooks/vault-gate.py`.** One script, two `pre_tool_call`
entries: a `search_files|read_file` matcher records (in
`<vault>/.gate/<session>.searched`) that this session touched the vault; a
`terminal|execute_code|write_file|patch|browser_exec` matcher blocks the
FIRST gated call of an unsearched session with an instruction message the
model reads as the tool error, then passes freely for the rest of the
session — the gate steers, it never wedges. Fail-open everywhere (no
`fail_closed`), malformed payloads pass silently, state is two tiny marker
files. Wire it:

```yaml
hooks:
  pre_tool_call:
    - matcher: "search_files|read_file"
      command: "<path-to>/hooks/vault-gate.py <vault-root>"
    - matcher: "terminal|execute_code|write_file|patch|browser_exec"
      command: "<path-to>/hooks/vault-gate.py <vault-root>"
```

On POSIX the shebang runs it directly; on Windows Hermes spawns `.py`
through the running Hermes interpreter. First use prompts for consent on a
TTY (`--accept-hooks` / `HERMES_ACCEPT_HOOKS=1` for headless). Validated
against the documented shell-hook wire format; test fixtures in the repo's
commit history (9-case suite: block-once, no-deadlock, backslash paths,
fail-open on malformed stdin).

## 2. Read telemetry: used / wasted / missed (the real health check)

A recall probe proves retrieval *works*. It cannot detect the two failures
that dominate in practice:

- **missed** — a memory existed and was never opened (discoverability or
  compliance failure), and
- **quietly wrong** — a memory was opened, trusted, and was stale or false.

Fix: a `post_tool_call` hook logs every vault read; each session's reads get
classified **used / wasted / missed**. Anything missed three times is
promoted — either fix the file's keywords/links (discoverability problem) or
add a gate nudge (compliance problem). Quietly-wrong detection rides the
weekly immune pass: a memory read and *contradicted by ground truth* (see 3)
is the dangerous class, and it only surfaces if you track reads.

This is also the best community answer yet to the source system's open
question — "how do you measure whether a memory affected a cognitively
complex system?"

## 3. External ground-truth review (immune pass extension)

Internal consistency checks (contradiction sweep, orphans) can't catch a
state file that agrees with itself and has drifted from reality. When a
live thread in `state/` has an authoritative external source (ticket
tracker, monitoring, deployment system), the weekly pass verifies the
thread **against that source**. Drift is a contradiction (Doctrine 5): flag
it, keep both sides, operator adjudicates.

## Also noted

- **Close ritual vs nightly distiller:** a per-session close ritual files
  scars while they're fresh (and matches Doctrine 4's "immediately"); a
  nightly cron catches the sessions that never close (gateway/daemon
  instances). Hybrid is the correct answer: write failures at incident
  time, sweep nightly for strays.
- **Orphan files are a shared disease:** independent deployments report a
  meaningful fraction of memory files with no links in or out. The INDEX
  [ORPHAN] flag exists for exactly this; treat orphan count as a health
  metric, not cosmetic.

*Attribution: the v1.1 upgrades came from community field feedback. If you
deploy TrashPanda and find a gap, open an issue — field notes are how this
thing evolves.*
