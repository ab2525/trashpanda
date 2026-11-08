# TrashPanda — file-based long-term memory for Hermes Agent

> **TrashPanda** (n.): a raccoon. Also: a vault-oriented memory system for
> agents, because raccoons are caching animals with excellent retrieval
> instincts and no shame about where the good garbage is buried.
>
> *"The transcript is cache; the vault is disk."*

A minimum, portable memory system for a Hermes instance: a growing markdown
corpus retrieved by grep and agentic search (no vector DB, no RAG), with cron
jobs that distill sessions into durable lesson files and an immune pass that
audits the corpus for poisoning and drift. Architecture adapted from Pulsed
Media's production "Vainamoinen" write-ups (7 memory layers, 0 RAG, 91%
ticket autonomy, CSAT 9.8) and validated independently: Claude Code dropped
RAG for agentic grep; Amazon research reached ~90% of RAG performance with
plain keyword search over agent tools.

Design travel: Pulsed Media (production, ~400 servers) -> Kit Edition (single
user, this bundle) -> your instance.

## What you get

```
doctrine/000-doctrine.md      The 8 laws. OPERATOR-LOCKED after install.
README-vault.md               Vault map + retrieval protocol (becomes the
                              vault's own README.md)
sop/maintenance-runbook.md    What the cron jobs do, in prose
scripts/vault_index.py        Index/link-graph builder + orphan detector
templates/                    File skeletons: lesson, incident, state,
                              reference, SOUL snippet, cron prompts
```

## Install (10 minutes)

1. **Create the vault** under the instance's Hermes home:
   `mkdir -p $HERMES_HOME/memory-vault/{doctrine,sop,memory,state,reference,scripts}`
   Copy `README-vault.md` in as `memory-vault/README.md`, copy
   `doctrine/000-doctrine.md` and `sop/maintenance-runbook.md` verbatim,
   copy `scripts/vault_index.py`.
2. **Seed the state file** from `templates/state-template.md` — one page of
   "active threads" (current projects, connector status, open loops). This is
   the hot cache the agent reads first on "where were we".
3. **Optional: identity.** If the instance has a persona, add a short
   identity+values section to its `SOUL.md` (see `templates/SOUL-snippet.md`).
   Keep it under ~2.5 KB: SOUL.md is injected EVERY turn; it is a standing
   cost, not free storage.
4. **Point the agent at the vault.** Add one entry to the injected memory
   store (the tiny always-loaded memory) along the lines of:
   "memory-vault/ exists at <path>; for durable facts, grep the vault first
   (layer 1), read INDEX.md second; state/ holds active threads."
   That single pointer is the entire always-in-context footprint of the
   system. Everything else is pull-on-demand.
5. **Create the two cron jobs** from `templates/cron-prompts.md`:
   - nightly distillation (03:30 local, deliver=local — silent)
   - weekly immune pass (Sunday 04:00, deliver=origin — silent when clean)
   Both load a skill or the runbook path; both must be self-contained
   prompts (cron runs in a fresh session with no chat context).
6. **Lock the doctrine.** Replace the `granted_by:` frontmatter with your
   operator name and date. From that moment the agent refuses to edit
   `doctrine/` without explicit instruction; the immune cron audits that the
   lock still holds. (Convention + audit, not filesystem ACLs — tighten with
   real permissions if your instance can.)

## Verify (the acceptance test)

1. `python scripts/vault_index.py` — prints a file count, writes INDEX.md.
2. **Recall probe:** put a fact into a vault file that has never appeared in
   chat (e.g. "the espresso machine on floor 3 was replaced 2024-06-12"), then
   ask the agent in a FRESH session. A correct answer proves layer-1 retrieval
   is live. Gotcha: the probe fact must actually exist in the corpus — if the
   SOP cites a fact the corpus lacks, fix the data, never the test.
3. Wait one distillation cycle, then ask "what did you learn last night" and
   read the cron output / new memory files.

## Operating rules (why it is shaped this way)

- **Pull, not push.** Nothing enters context until a request's keywords grep
  it in. Standing cost = SOUL + a one-line pointer. The vault can grow
  100x without touching the context budget.
- **Failures first.** The single most valuable category at the source system
  was the agent documenting its own mistakes. The distiller writes scars
  before wins, immediately.
- **DRY applies to code, not safety.** Safety text repeats across topic files
  on purpose: repetition is behavioral reinforcement. A compression pass that
  deduplicated guardrails once dropped a fleet throttle and mass-updated 126
  servers. Distillation NEVER touches doctrine/ or safety text.
- **Doctrine is operator-locked.** A self-editable guardrail layer is the
  poisoning vector the whole design guards against.
- **Contradiction triggers a sweep**, not a silent edit: conflicts get
  flagged for human adjudication, both sides preserved.
- **Forget by sinkage, never deletion.** Old memories sink into low
  cross-linkage and stop surfacing. Nothing is ever destroyed to "clean up".

## Limits (honest ones)

- No mid-turn auto-injection ("hunches") — stock Hermes has no hook for it.
  Approximated by the tiny always-injected pointer + relevance-loaded skills.
- The immune pass is grep-based cross-referencing, not embeddings; it catches
  lexical contradictions, not semantic ones.
- Vault quality is bounded by distiller discipline: garbage in, greppable
  garbage out. Keep the "durable, shelf life > 1 week, no secrets" filter
  strict.
- Secrets never enter the vault: no tokens, passwords, keys, codes — not even
  masked fragments.

MIT-licensed. Attribution chain: Pulsed Media's Vainamoinen write-ups (design),
Kit Edition / Alex Buie (this bundle). Go bury something good. 🦝
