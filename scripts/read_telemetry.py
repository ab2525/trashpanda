#!/usr/bin/env python3
"""TrashPanda read-telemetry report.

Reads <vault>/.telemetry/reads.jsonl (written by hooks/vault-read-log.py) and
the vault tree, then reports per-file surfacing over the window:

  never-opened  — file exists, zero read_file hits in the window
                  => candidate MISSED memory (compare against the week's
                     search patterns: if a search could have hit it, it is a
                     discoverability failure -> fix keywords/links; if no
                     search asked for it, it may simply be unneeded yet)
  surfaced      — read N times; N high with zero follow-through is wasted
  search-dust   — search patterns with matches>0 whose result files were
                  never opened => exists-but-unopened, the class recall
                  probes cannot catch

Judgement stays human/agent-side: this script supplies DATA, the weekly
immune pass applies the used/wasted/missed VERDICT. Pure stdlib.
"""
import json
import os
import sys
import time
from collections import Counter


def vault_root():
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        return os.path.expanduser(sys.argv[1])
    env = os.environ.get("TRASHPANDA_VAULT")
    if env:
        return os.path.expanduser(env)
    return os.path.join(os.path.expanduser("~"), ".hermes", "memory-vault")


def main():
    root = vault_root()
    days = 7
    for arg in sys.argv[1:]:
        if arg.startswith("--days="):
            days = int(arg.split("=", 1)[1])
    log_path = os.path.join(root, ".telemetry", "reads.jsonl")
    if not os.path.exists(log_path):
        print("no read log yet at %s — wire hooks/vault-read-log.py first"
              " (README-SETUP step 5b). Nothing to report." % log_path)
        return 0

    cutoff = time.time() - days * 86400
    reads = Counter()
    patterns = []
    total_lines = 0
    with open(log_path, encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("ts", 0) < cutoff:
                continue
            total_lines += 1
            if rec.get("tool") == "read_file" and rec.get("target"):
                rel = rec["target"].replace("\\", "/")
                if root.replace("\\", "/") in rel:
                    rel = rel.split("memory-vault/")[-1]
                reads[rel] += 1
            elif rec.get("tool") == "search_files":
                patterns.append((rec.get("pattern") or "", rec.get("matches")))

    tree = []
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fn in files:
            if fn.endswith(".md") and fn not in ("INDEX.md",):
                p = os.path.relpath(os.path.join(base, fn), root).replace("\\", "/")
                tree.append(p)

    never = [p for p in sorted(tree) if reads.get(p, 0) == 0]
    print("window: %dd | logged vault reads: %d | vault files: %d" % (days, total_lines, len(tree)))
    print("\nSURFACED (read_file hits):")
    for p, n in reads.most_common(20):
        print("  %4d  %s" % (n, p))
    print("\nNEVER-OPENED (%d) — candidate MISSED memories:" % len(never))
    for p in never:
        print("  " + p)
    print("\nSEARCH PATTERNS WITH HITS (%d shown):" % min(len(patterns), 20))
    for pat, m in patterns[:20]:
        print("  matches=%s  %r" % (m, pat))
    print("\nNext step: weekly immune pass judges each NEVER-OPENED against the"
          "\nhits-with-no-open patterns => discoverability fix vs gate nudge."
          "\n(3x-missed rule: promote the same file three windows running.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
