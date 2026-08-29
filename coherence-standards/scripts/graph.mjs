#!/usr/bin/env node
// Import-graph facts for packages/frontend. Node standard library only.
// Run: node .standards/_inventory/graph.mjs
//
// Encodes THIS repo's conventions, not generic ones:
//   * tests live in src/__tests__/ mirroring the tree, never colocated
//   * the `@/` alias maps to ./src/ (tsconfig paths) and must be resolved
//   * components/ui/* are shadcn-style primitives, imported widely by design
//   * main.tsx is the Vite entrypoint; e2e/ is Playwright, not app code
//
// Limits: regex extraction misses dynamic import(), re-export barrels, and
// string-built paths. Every number is a LEAD to verify, not an assertion.

import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative, resolve, dirname, extname } from "node:path";

const ROOT = resolve(import.meta.dirname, "../..");
const SRC = join(ROOT, "packages/frontend/src");
const EXT = [".ts", ".tsx"];

function walk(dir, out = []) {
  for (const e of readdirSync(dir)) {
    const p = join(dir, e);
    if (statSync(p).isDirectory()) walk(p, out);
    else if (EXT.includes(extname(p))) out.push(p);
  }
  return out;
}

const files = walk(SRC);
const key = (p) => relative(SRC, p).replace(/\.(tsx?)$/, "");
const known = new Set(files.map(key));

function resolveSpec(spec, fromFile) {
  let base;
  if (spec.startsWith("@/")) base = spec.slice(2);
  else if (spec.startsWith(".")) base = relative(SRC, resolve(dirname(fromFile), spec));
  else return null; // third-party
  for (const cand of [base, `${base}/index`]) if (known.has(cand)) return cand;
  return null;
}

const edges = new Map();
const IMPORT_RE = /(?:^|\n)\s*(?:import|export)[\s\S]*?from\s+["']([^"']+)["']/g;
for (const f of files) {
  const src = readFileSync(f, "utf8");
  const k = key(f);
  const set = new Set();
  for (const m of src.matchAll(IMPORT_RE)) {
    const t = resolveSpec(m[1], f);
    if (t && t !== k) set.add(t);
  }
  edges.set(k, set);
}

// Tarjan SCC
let idx = 0;
const I = new Map(), L = new Map(), on = new Set(), st = [], cycles = [];
function strong(v) {
  I.set(v, idx); L.set(v, idx); idx++; st.push(v); on.add(v);
  for (const w of edges.get(v) ?? []) {
    if (!I.has(w)) { strong(w); L.set(v, Math.min(L.get(v), L.get(w))); }
    else if (on.has(w)) L.set(v, Math.min(L.get(v), I.get(w)));
  }
  if (L.get(v) === I.get(v)) {
    const c = [];
    for (;;) { const w = st.pop(); on.delete(w); c.push(w); if (w === v) break; }
    if (c.length > 1) cycles.push(c);
  }
}
for (const v of edges.keys()) if (!I.has(v)) strong(v);

const fanIn = new Map();
for (const [, ts] of edges) for (const t of ts) fanIn.set(t, (fanIn.get(t) ?? 0) + 1);

const EXCLUDE = [
  ["entrypoint", (k) => k === "main" || k === "App"],
  ["test file", (k) => k.startsWith("__tests__/") || k.startsWith("test/")],
  ["generated types", (k) => k === "api/schema.d" || k.startsWith("api/schema")],
  ["vite env shim", (k) => k.includes("vite-env")],
];
const orphans = [...edges.keys()].filter((k) => {
  if (fanIn.get(k)) return false;
  return !EXCLUDE.some(([, f]) => f(k));
});

const testStems = new Set(
  [...known].filter((k) => k.startsWith("__tests__/")).map((k) => k.split("/").pop().replace(/\.test$/, "")),
);
const untested = [...known].filter(
  (k) => !k.startsWith("__tests__/") && !k.startsWith("test/") && !testStems.has(k.split("/").pop()),
);

const top = (m, n) => [...m.entries()].sort((a, b) => b[1] - a[1]).slice(0, n);
console.log("## TypeScript import graph (packages/frontend/src)\n");
console.log(`modules analysed: ${files.length}  |  edges: ${[...edges.values()].reduce((a, s) => a + s.size, 0)}`);
console.log(`\n### Cycles: ${cycles.length}`);
for (const c of cycles) console.log(`- ${c.sort().join(" <-> ")}`);
console.log("\n### Chokepoints — highest fan-in");
for (const [k, n] of top(fanIn, 12)) console.log(`- ${String(n).padStart(3)}  ${k}`);
console.log("\n### Highest fan-out");
for (const [k, n] of top(new Map([...edges].map(([k, s]) => [k, s.size])), 12)) console.log(`- ${String(n).padStart(3)}  ${k}`);
console.log(`\n### Zero inbound edges after exclusions: ${orphans.length}`);
console.log("exclusions applied: " + EXCLUDE.map(([r]) => r).join(", "));
for (const k of orphans.sort()) console.log(`- ${k}`);
console.log(`\n### Source modules with no __tests__ pair: ${untested.length} of ${known.size}`);
for (const k of untested.sort().slice(0, 40)) console.log(`- ${k}`);
if (untested.length > 40) console.log(`- … and ${untested.length - 40} more`);
