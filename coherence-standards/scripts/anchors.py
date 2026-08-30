#!/usr/bin/env python3
"""Evidence anchors: pin a rail to the code it rests on. Standard library only.

    anchors.py emit   src/models/scoped.py#L31-L44 [more...]
    anchors.py verify .standards/_claims/data.json [more...]

`emit` resolves `path#Lm-Ln` anchors against the working tree and prints the anchor
blocks that go in a `.standards/_claims/<domain>.json` sidecar. `verify` re-resolves
the anchors in a sidecar and reports one of five statuses per anchor.

The format is specified in toolkit/TEMPLATE.md ("Evidence anchors"). This file is the
implementation of that spec and the two must not drift: a hash written by hand, or by a
second implementation that normalizes differently, verifies `lost` forever and
discredits every other anchor in the file.

Why five hashes and not one. `range` is exact, so it answers "did this code change?" —
any edit inside the span breaks it. `first`/`last`/`before`/`after` are
whitespace-normalized, so they answer "where did this code go?" — a reformat or 200
inserted lines above leaves the block findable at its new offset. One hash cannot do
both jobs: an exact whole-file hash reports every rail stale on every commit, and a
fuzzy one never reports anything stale at all.

Limits (stated so a drafter knows what this cannot see): a span that was both moved AND
edited reports `lost`, not `moved`+`changed` — the two signals are not separable once
the fingerprint breaks. A span duplicated verbatim elsewhere in the file relocates to
the first match, which may be the wrong one. Renames are invisible: a file that moved
reports `missing`, and only a human can tell that from a deletion. Every status here is
a LEAD to verify against the code, never an assertion.
"""
import hashlib
import json
import pathlib
import re
import sys

CONTEXT = 3
ANCHOR_RE = re.compile(r"^(?P<path>.+?)#L(?P<start>\d+)-L(?P<end>\d+)$")
STATUS_ORDER = ["current", "moved", "changed", "lost", "missing"]


def sha(text):
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def norm(lines):
    """Normalized join: strip each line, join with \\n. Survives reindents and reflows."""
    return "\n".join(line.strip() for line in lines)


def read_lines(path):
    """Line endings normalized to \\n. Returns None when the file is gone."""
    p = pathlib.Path(path)
    if not p.is_file():
        return None
    text = p.read_text(encoding="utf-8", errors="surrogateescape")
    return text.replace("\r\n", "\n").replace("\r", "\n").split("\n")


def fingerprint(lines, start, end):
    """Hashes for the 1-indexed inclusive span [start, end]. Caller checks bounds."""
    span = lines[start - 1:end]
    return {
        "lines": len(span),
        "range": sha("\n".join(span)),
        "first": sha(span[0].strip()),
        "last": sha(span[-1].strip()),
        "before": sha(norm(lines[max(0, start - 1 - CONTEXT):start - 1])),
        "after": sha(norm(lines[end:end + CONTEXT])),
    }


def emit(anchor):
    m = ANCHOR_RE.match(anchor)
    if not m:
        raise SystemExit(f"not an anchor: {anchor!r} (want path#L12-L48)")
    path, start, end = m["path"], int(m["start"]), int(m["end"])
    if start < 1 or end < start:
        raise SystemExit(f"bad range in {anchor!r}: L{start}-L{end}")
    lines = read_lines(path)
    if lines is None:
        raise SystemExit(f"no such file: {path}")
    if end > len(lines):
        raise SystemExit(f"{path} has {len(lines)} lines; {anchor} runs past the end")
    return {"resource": anchor, "algo": "repo-lines-v1", **fingerprint(lines, start, end)}


def verify(anchor):
    """One of: current, moved, changed, lost, missing. Plus where it went, if known."""
    m = ANCHOR_RE.match(anchor["resource"])
    path, start, end = m["path"], int(m["start"]), int(m["end"])
    lines = read_lines(path)
    if lines is None:
        return {"status": "missing", "resource": anchor["resource"]}

    n = anchor["lines"]

    # 1. Unchanged where it was recorded.
    if end <= len(lines) and fingerprint(lines, start, end)["range"] == anchor["range"]:
        return {"status": "current", "resource": anchor["resource"]}

    # 2. Same code, new offset: the whole fingerprint matches a window elsewhere.
    for i in range(1, len(lines) - n + 2):
        fp = fingerprint(lines, i, i + n - 1)
        if all(fp[k] == anchor[k] for k in ("first", "last", "before", "after")):
            return {"status": "moved", "resource": anchor["resource"],
                    "found_at": f"{path}#L{i}-L{i + n - 1}"}

    # 3. Context still brackets something, but the interior was edited. Smallest span wins.
    starts = [i for i in range(1, len(lines) + 1)
              if sha(norm(lines[max(0, i - 1 - CONTEXT):i - 1])) == anchor["before"]]
    ends = [j for j in range(1, len(lines) + 1)
            if sha(norm(lines[j:j + CONTEXT])) == anchor["after"]]
    spans = sorted(((j - i, i, j) for i in starts for j in ends if j >= i))
    if spans:
        _, i, j = spans[0]
        return {"status": "changed", "resource": anchor["resource"],
                "found_at": f"{path}#L{i}-L{j}"}

    # 4. File is there; nothing recognizable is.
    return {"status": "lost", "resource": anchor["resource"]}


def worst(statuses):
    return max(statuses, key=STATUS_ORDER.index) if statuses else "current"


def main(argv):
    if len(argv) < 3 or argv[1] not in ("emit", "verify"):
        raise SystemExit(__doc__)
    mode, args = argv[1], argv[2:]

    if mode == "emit":
        print(json.dumps([emit(a) for a in args], indent=2))
        return 0

    exit_code = 0
    for sidecar in args:
        doc = json.loads(pathlib.Path(sidecar).read_text())
        print(f"\n{sidecar}  (rails: {len(doc.get('rails', []))})")
        tally = dict.fromkeys(STATUS_ORDER, 0)
        for rail in doc.get("rails", []):
            results = [verify(a) for a in rail.get("anchors", [])]
            if not results:
                if rail.get("tag") in ("observed", "inferred"):
                    print(f"  {rail['id']:<10} NO ANCHORS  [{rail.get('tag')}] — unverifiable")
                    exit_code = 1
                continue
            status = worst([r["status"] for r in results])
            tally[status] += 1
            if status != "current":
                exit_code = 1
                print(f"  {rail['id']:<10} {status.upper()}")
                for r in results:
                    if r["status"] != "current":
                        moved = f"  ->  {r['found_at']}" if "found_at" in r else ""
                        print(f"      {r['status']:<8} {r['resource']}{moved}")
        print("  " + "  ".join(f"{k}={v}" for k, v in tally.items() if v))
    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
