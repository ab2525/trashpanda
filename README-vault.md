---
date: TEMPLATE
type: reference
keywords: [vault-map, retrieval-protocol]
---
# Memory Vault

Long-term memory for this Hermes instance. Files over vectors: retrieval is
grep first, always.

## Trees
- `doctrine/`  — OPERATOR-LOCKED. The agent refuses to edit these without
                 explicit operator instruction. Safety law, derived from
                 incidents.
- `sop/`       — proven procedures. Self-editable, but changes get logged in
                 the file's `revised:` frontmatter.
- `memory/`    — episodic lessons. Failures first, written at incident time.
- `state/`     — active threads and current facts. The temporal-continuity
                 layer. Rewritten by distillation; nothing deleted.
- `reference/` — external knowledge digests.

## Retrieval protocol (tiered, grep-first)
1. Ripgrep over this tree on the request's keywords.
2. If miss: read `INDEX.md` and follow the map by topic.
3. If still miss: LLM-summarized query over candidate files (rare).

## Forgetting
Never delete. Old memories sink into low cross-linkage and stop surfacing.
Forgetting is a property of discoverability, not of destruction.
