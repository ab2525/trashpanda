---
date: TEMPLATE
type: sop
revised: []
keywords: [distillation, immune-pass, cron, vault-maintenance]
links: [README.md, doctrine/000-doctrine.md]
---
# Vault maintenance runbook

Both jobs are Hermes crons. Prompts live in `templates/cron-prompts.md`.

## Nightly distillation (03:30 local)
1. Read the day's session transcripts (state.db / sessions mirror; skip the
   distiller's own runs).
2. Extract DURABLE items only: decisions, incidents, corrections, facts with
   shelf life > 1 week. No logs, no ephemera, no secrets — credentials,
   tokens, card numbers and codes never enter the vault.
3. FAILURES FIRST (Doctrine 4). One file per lesson in `memory/`, named
   YYYY-MM-DD-lesson-<slug>.md or YYYY-MM-DD-incident-<slug>.md, with the
   frontmatter convention.
4. Update `state/` active threads in place (state is rewritten, history is
   appended — never deleted).
5. NEVER write into `doctrine/` (Doctrine 3). NEVER compress safety text
   (Doctrine 2).
6. Run `scripts/vault_index.py` to rebuild INDEX.md.

## Weekly immune pass (Sunday 04:00)
1. Run `scripts/vault_index.py`; note [ORPHAN] files; link genuinely adjacent
   ones; never delete.
2. Cross-reference pass: for each `state/` fact, grep `memory/` and
   `reference/` for contradictions. Record conflicts as
   memory/YYYY-MM-DD-immune-flag-<slug>.md — both sides preserved, operator
   adjudicates (Doctrine 5).
3. **External ground-truth review (v1.1):** for each live `state/` thread
   with an authoritative external source (ticket tracker, monitoring,
   deployment system), verify the thread against that source. Drift is a
   contradiction — flag it, keep both sides, never silently rewrite.
4. **Read telemetry (v1.1):** classify the week's vault reads as
   used / wasted / missed (from the post_tool_call read log, if installed).
   Anything missed three times gets promoted: fix the file's
   keywords/links (discoverability problem) or add a pre_tool_call gate
   nudge (compliance problem). A memory read-then-contradicted-by-ground-
   truth is the dangerous class — surface it loudly.
5. Doctrine integrity: `doctrine/000-doctrine.md` must still carry
   `status: operator-locked` and its laws must not have been edited by the
   distiller.
6. If the vault carries instance-specific canary checks (e.g. a source patch
   that an update may clobber), verify and alert loudly when missing.

## Recall probe (health check, any time)
Ask the agent to answer something that exists ONLY in a vault file. A correct
answer in a fresh session proves layer-1 retrieval is live.
