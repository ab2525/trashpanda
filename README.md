# 🦝 TrashPanda

**File-based long-term memory for AI agents. Grep-first. No RAG. No vector DB.**

> *TrashPanda (n.): a raccoon. Also: a memory system for agents — because
> raccoons are caching animals with excellent retrieval instincts and no
> shame about where the good garbage is buried.*

**The transcript is cache. The vault is disk.**

## Why

Your agent is a very clever goldfish. Every session it wakes up, does brilliant
work, and forgets. Standard fixes (RAG, vector stores) bolt a retrieval layer
onto the forgetting — and the research keeps landing against them: Claude Code
[dropped RAG for agentic grep](https://www.latent.space/p/claude-code) because
"agentic search generally works better"; Amazon found keyword search via
agentic tool use hits ~90% of RAG performance with no database at all; and in
production, Pulsed Media's autonomous sysadmin ("Väinämöinen") runs ~400
servers at 91% autonomy on exactly this shape of system — 7 memory layers,
0 RAG, every mistake becoming a file.

TrashPanda is the distilled, portable version of that architecture: a growing
markdown corpus your agent greps on demand, plus two cron jobs — a **nightly
distiller** that files the day's lessons (failures first) and a **weekly
immune pass** that audits the corpus for poisoning and drift.

## The architecture

```
                     ┌────────────────────────────────────┐
 ALWAYS IN CONTEXT   │ SOUL.md · injected memory (tiny)   │  ← fixed cost, ~KB
 (fixed, every turn) │ skill descriptions (one-liners)    │
                     └───────────────┬────────────────────┘
                                     │ pointer: "grep the vault first"
                                     ▼
 ON DEMAND (pull)    ┌────────────────────────────────────┐
 (only when asked)   │  memory-vault/                     │
                     │  ├── doctrine/   OPERATOR-LOCKED   │  ← 8 laws, human-only
                     │  ├── sop/        proven procedures │
                     │  ├── memory/     lessons & scars   │  ← failures first
                     │  ├── state/      active threads    │  ← hot cache, rewritten
                     │  ├── reference/  external digests  │
                     │  └── INDEX.md    link graph        │
                     └───────┬────────────────────────────┘
                             │ ripgrep → read_file (tier 1)
                             │ INDEX.md map        (tier 2)
                             │ LLM over candidates (tier 3, rare)
                             ▼
  cron 03:30 nightly ──► distiller: transcripts → durable lessons
  cron 04:00 Sunday ──► immune pass: orphans, contradictions, canary checks
```

**Pull, not push.** Nothing enters the agent's context until a request's
keywords grep it in. The standing overhead is a SOUL file and a one-line
pointer — the vault can grow 100× without touching the context budget.

## Install (10 minutes)

See **[README-SETUP.md](README-SETUP.md)** for the full walkthrough, the
acceptance test (a recall probe), and the operating rules. Short version:

1. Copy the trees into `<HERMES_HOME>/memory-vault/`
2. Seed `state/` from the template — one page of active threads
3. Point the agent at the vault with a single injected-memory line
4. Create the two cron jobs from `templates/cron-prompts.md`
5. Lock `doctrine/000-doctrine.md` (fill in `granted_by:` — then the agent
   refuses to edit it without explicit operator instruction)
6. Run the recall probe and wait one dream cycle

Works with any Hermes Agent instance; the pattern (markdown vault + grep +
distillation cron + immune cron) ports to any agent framework with file tools
and a scheduler.

## The laws (why it's shaped this way)

- **Investigate, then act** — every "it works" is an exercised artifact.
- **DRY applies to code, not safety** — safety text repeats on purpose; a
  dedup pass once dropped a fleet throttle and mass-updated 126 servers.
- **Doctrine is operator-locked** — a self-editable guardrail layer is the
  poisoning vector the whole design guards against.
- **Failures first** — the largest, most valuable memory category at the
  source system was the agent documenting its own mistakes.
- **Contradiction triggers a sweep** — conflicts get flagged for a human,
  never silently rewritten.
- **Forget by sinkage, not deletion** — nothing is ever destroyed to clean up.

Full version: [doctrine/000-doctrine.md](doctrine/000-doctrine.md)

## Honest limits

- No mid-turn auto-injection ("hunches") — approximated by the tiny injected
  pointer plus relevance-loaded skills
- The immune pass is grep-based cross-referencing: it catches lexical
  contradictions, not semantic ones
- Vault quality is bounded by distiller discipline — garbage in, greppable
  garbage out. Keep the "durable, shelf-life > 1 week, **no secrets, no
  customer PII**" filter strict

## Lineage & attribution

Design adapted from Pulsed Media's production write-ups on
[Väinämöinen](https://pulsedmedia.com/blog/2026/03/ai-agent-who-never-forgets-3109-files-7-layers-0-rag-9-80-10-csat/)
(7 layers, 0 RAG, 9.80/10 CSAT — read their numbers with a skeptic's eye, but
the architecture core is corroborated). Packaged as the "Kit Edition" for
Hermes Agent, then generalized here so any agent can bury its own garbage.

## License

[MIT](LICENSE) — go bury something good. 🦝
