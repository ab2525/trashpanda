# Cron job prompts (adapt paths, then create via the cronjob tool)

Job 1 — name: vault-distill, schedule: 30 3 * * *, deliver: local
---
You are the nightly memory distiller. Follow the runbook at
<HERMES_HOME>/memory-vault/sop/maintenance-runbook.md (read it first, then
README.md). Steps: (1) inspect the day's session transcripts (state.db /
sessions mirror; skip your own prior runs). (2) Extract DURABLE lessons only
— decisions, incidents, corrections, facts with shelf life > 1 week.
FAILURES FIRST, one file per lesson in memory/ named
YYYY-MM-DD-lesson-<slug>.md or YYYY-MM-DD-incident-<slug>.md with the vault's
YAML frontmatter convention. (3) Update state/ active-threads in place
(rewrite, never delete history files). (4) NEVER write into doctrine/ — it is
operator-locked. NEVER compress or deduplicate safety text. (5) Secrets rule:
credentials, tokens, passwords, card numbers, one-time codes NEVER enter the
vault, not even masked fragments. (6) Run
python <HERMES_HOME>/memory-vault/scripts/vault_index.py and confirm INDEX.md
rebuilt. Environment: pass explicit workdir on terminal calls if the default
cwd is broken on this host; write files with file tools, not redirection.
If nothing durable happened, still rebuild the index and end with exactly:
NO_REPLY

Job 2 — name: vault-immune, schedule: 0 4 * * 0 (Sundays), deliver: origin
---
You are the weekly memory immune pass. Read
<HERMES_HOME>/memory-vault/sop/maintenance-runbook.md (weekly section) and
README.md, then: (1) run scripts/vault_index.py; note [ORPHAN] files, link
genuinely-adjacent ones, never delete anything. (2) Contradiction sweep: for
each state/ fact, grep memory/ and reference/ for conflicts; write
memory/YYYY-MM-DD-immune-flag-<slug>.md with BOTH sides, do not rewrite
either. (3) Verify instance canaries from state/ (patches, locks, configs an
update could clobber) — if one is missing, say so LOUDLY in the final
response; that alert is the whole point of this job. (4) Doctrine integrity:
doctrine/000-doctrine.md must still contain status: operator-locked with the
laws unedited (do not edit it). If everything is clean, end with exactly:
NO_REPLY

Notes: cron prompts run in a fresh session with NO chat context — they must
be fully self-contained (paths spelled out). deliver=local keeps the nightly
job silent (output still lands in cron/output/<job>/); deliver=origin posts
the weekly job's response to its origin chat, so the NO_REPLY convention
keeps clean weeks quiet and loud weeks loud.
