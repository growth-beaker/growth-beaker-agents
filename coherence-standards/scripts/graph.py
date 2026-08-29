#!/usr/bin/env python3
"""Import-graph facts for the Python packages. Standard library only.

Run: uv run python .standards/_inventory/graph.py

Encodes THIS repo's conventions rather than generic ones, because a generic tool
reports the wrong things here:
  * tests live in packages/<pkg>/tests/, never colocated  -> test pairing uses that layout
  * alembic/versions/* are migrations, loaded by Alembic   -> excluded from orphans
  * __init__.py re-export barrels are imported implicitly  -> excluded from orphans
  * FastAPI routes are wired via include_router in main.py -> import edge exists, kept
  * domain.entities._all_models imports siblings via pkgutil at runtime (NOT a static
    import) -> entity modules would look orphaned; excluded with that reason recorded

Limits (stated so a drafter knows what this cannot see): regex extraction misses
dynamic imports, importlib calls, string-built module paths, and re-export chains.
Every number here is a LEAD to verify against the code, never an assertion.
"""
import ast
import pathlib
import sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[2]
PKGS = ["domain", "api", "agent", "mcp_server", "hureva"]
SRC_DIRS = [
    ROOT / "packages/domain/src",
    ROOT / "packages/api/src",
    ROOT / "packages/agent/src",
    ROOT / "packages/mcp/src",
    ROOT / "packages/hureva/src",
]


def modname(path: pathlib.Path) -> str | None:
    for src in SRC_DIRS:
        try:
            rel = path.relative_to(src)
        except ValueError:
            continue
        parts = list(rel.with_suffix("").parts)
        if parts and parts[-1] == "__init__":
            parts.pop()
        return ".".join(parts) if parts else None
    return None


def first_party(mod: str) -> bool:
    return any(mod == p or mod.startswith(p + ".") for p in PKGS)


files: dict[str, pathlib.Path] = {}
for src in SRC_DIRS:
    for p in src.rglob("*.py"):
        m = modname(p)
        if m:
            files[m] = p

edges: dict[str, set[str]] = defaultdict(set)
deferred: set[tuple[str, str]] = set()   # function-local imports = managed seam
parse_failures: list[str] = []

def targets_of(node, mod: str) -> list[str]:
    """Import targets, absolute or relative, expanding `from pkg import submodule`.

    `from api.routes import auth, teams` imports SUBMODULES, not names — recording
    only the edge to `api.routes` makes every route module look orphaned. Try the
    dotted child first and fall back to the package.
    """
    if isinstance(node, ast.Import):
        return [a.name for a in node.names]
    if not isinstance(node, ast.ImportFrom):
        return []
    if node.level:  # relative: resolve against this module's package
        parts = mod.split(".")
        base = ".".join(parts[: max(0, len(parts) - node.level + 1)])
        head = f"{base}.{node.module}" if node.module else base
    else:
        head = node.module or ""
    out = []
    for a in node.names:
        child = f"{head}.{a.name}" if head else a.name
        out.append(child if child in files else head)
    return out or [head]


for mod, path in files.items():
    try:
        tree = ast.parse(path.read_text())
    except SyntaxError as e:
        parse_failures.append(f"{mod}: {e}")
        continue
    for node in ast.walk(tree):
        for t in targets_of(node, mod):
            if not t or not first_party(t):
                continue
            cand = t
            while cand and cand not in files:
                cand = cand.rpartition(".")[0]
            if cand and cand != mod:
                edges[mod].add(cand)

# mark function-local imports separately
for mod, path in files.items():
    try:
        tree = ast.parse(path.read_text())
    except SyntaxError:
        continue
    for fn in [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
        for node in ast.walk(fn):
            for t in targets_of(node, mod):
                if not t or not first_party(t):
                    continue
                cand = t
                while cand and cand not in files:
                    cand = cand.rpartition(".")[0]
                if cand and cand != mod:
                    deferred.add((mod, cand))


def tarjan(nodes, adj):
    idx = {}
    low = {}
    on = set()
    stack = []
    out = []
    counter = [0]

    def strong(v):
        idx[v] = low[v] = counter[0]
        counter[0] += 1
        stack.append(v)
        on.add(v)
        for w in adj.get(v, ()):
            if w not in idx:
                strong(w)
                low[v] = min(low[v], low[w])
            elif w in on:
                low[v] = min(low[v], idx[w])
        if low[v] == idx[v]:
            comp = []
            while True:
                w = stack.pop()
                on.discard(w)
                comp.append(w)
                if w == v:
                    break
            if len(comp) > 1:
                out.append(comp)

    sys.setrecursionlimit(10000)
    for v in nodes:
        if v not in idx:
            strong(v)
    return out


cycles = tarjan(list(files), edges)

fan_in: dict[str, int] = defaultdict(int)
for m, ts in edges.items():
    for t in ts:
        fan_in[t] += 1
fan_out = {m: len(ts) for m, ts in edges.items()}

# --- orphans, with this repo's conventions applied ---
EXCLUDE_REASONS = {
    "entrypoint": lambda m: m.endswith(("main", "__main__")) or m in ("api.main", "agent.main"),
    "barrel/__init__": lambda m: m in files and files[m].name == "__init__.py",
    "pkgutil-discovered entity": lambda m: m.startswith("domain.entities."),
    "cli entrypoint (pyproject scripts)": lambda m: m.startswith("hureva.") and m.count(".") == 1,
    "generated": lambda m: "generated" in m,
}
orphans = []
for m in files:
    if fan_in.get(m, 0):
        continue
    reason = next((r for r, f in EXCLUDE_REASONS.items() if f(m)), None)
    if reason:
        continue
    orphans.append(m)

# --- test pairing, using THIS repo's layout: packages/<pkg>/tests/ ---
test_files = set()
for pkg_dir in (ROOT / "packages").iterdir():
    td = pkg_dir / "tests"
    if td.is_dir():
        for p in td.rglob("test_*.py"):
            test_files.add(p.stem.removeprefix("test_"))
untested = sorted(
    m for m, p in files.items()
    if p.stem not in test_files
    and p.name != "__init__.py"
    and not m.startswith("domain.entities.")
)

print("## Python import graph\n")
print(f"modules analysed: {len(files)}  |  edges: {sum(len(v) for v in edges.values())}")
if parse_failures:
    print(f"parse failures: {parse_failures}")
print(f"\n### Cycles (strongly connected components): {len(cycles)}")
for c in cycles:
    print(f"- {' <-> '.join(sorted(c))}")
    for a in c:
        for b in edges.get(a, ()):
            if b in c:
                tag = "DEFERRED (function-local — likely a managed seam)" if (a, b) in deferred else "module-level"
                print(f"    {a} -> {b}  [{tag}]")
print("\n### Chokepoints — highest fan-in (what everything depends on)")
for m, n in sorted(fan_in.items(), key=lambda kv: -kv[1])[:12]:
    print(f"- {n:>3}  {m}")
print("\n### Highest fan-out (what carries the most coupling)")
for m, n in sorted(fan_out.items(), key=lambda kv: -kv[1])[:12]:
    print(f"- {n:>3}  {m}")
print(f"\n### Zero inbound edges after exclusions: {len(orphans)}")
print("exclusions applied: " + ", ".join(EXCLUDE_REASONS))
for m in sorted(orphans):
    print(f"- {m}")
print(f"\n### Source modules with no test_<name>.py pair: {len(untested)} of {len(files)}")
for m in untested[:40]:
    print(f"- {m}")
if len(untested) > 40:
    print(f"- … and {len(untested)-40} more")
