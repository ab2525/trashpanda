# Rebuild INDEX.md for the vault: tree, frontmatter summary, link graph.
# Pure stdlib. Run nightly from the distillation cron and weekly from the
# immune pass. Orphan files (zero inbound+outbound links) are the immune
# pass audit signal.
import os, re, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TREES = ("doctrine", "sop", "memory", "state", "reference")

def fm(text):
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            out[k.strip()] = v.strip()
    return out

files = []
for t in TREES:
    d = os.path.join(ROOT, t)
    if not os.path.isdir(d):
        continue
    for name in sorted(os.listdir(d)):
        if name.endswith(".md"):
            rel = t + "/" + name
            with open(os.path.join(d, name), encoding="utf-8") as f:
                body = f.read()
            links = sorted(set(re.findall(r"(?:memory|sop|doctrine|state|reference)/[\w.\-]+\.md", body)))
            files.append((rel, fm(body), links))

inbound = {}
for rel, _, links in files:
    for l in links:
        if l != rel:
            inbound[l] = inbound.get(l, 0) + 1

words = 0
lines = ["# Vault index — rebuilt " + datetime.datetime.now().isoformat(timespec="seconds")]
for rel, _, _ in files:
    with open(os.path.join(ROOT, rel.replace("/", os.sep)), encoding="utf-8") as f:
        words += len(f.read().split())
lines.append("Files: %d  |  Words: %d" % (len(files), words))
lines.append("")
for t in TREES:
    sub = [f for f in files if f[0].startswith(t + "/")]
    if not sub:
        continue
    lines.append("## " + t + "/ (%d)" % len(sub))
    for rel, meta, links in sub:
        kw = meta.get("keywords", "")
        lock = "  **[OPERATOR-LOCKED]**" if meta.get("status") == "operator-locked" else ""
        orphan = "" if (inbound.get(rel) or links) else "  [ORPHAN]"
        lines.append("- [%s] %s%s%s — %s" % (meta.get("date", "?"), rel, lock, orphan, kw))
    lines.append("")

with open(os.path.join(ROOT, "INDEX.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
orphans = sum(1 for r, _, lk in files if not inbound.get(r) and not lk)
print("INDEX.md rebuilt: %d files, orphans=%d" % (len(files), orphans))
