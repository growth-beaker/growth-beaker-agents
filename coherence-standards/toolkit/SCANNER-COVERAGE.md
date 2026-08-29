---
okf_version: "0.2"
type: Reference
title: Scanner-covered rails
description: Which taxonomy rails a code-health tool should own instead of prose, and how to dispose of each.
tags: [standards, meta, scanner, coverage]
generated: { by: "market-research-feedback", at: "2026-08-29" }
verified:
  - { by: "human:chris", at: "2026-08-29" }
---

# Scanner-Covered Rails
## What to delete from `.standards/` because CodeScene / SonarQube already enforce it

Companion to `TAXONOMY.md`. Every rail below is **universal** — it would read identically at any other company. Universal rules belong in the scanner's ruleset, not in prose an agent must read on every task.

**Disposition key:**
- **DELETE** — remove the prose rail entirely; the scanner is the standard
- **THIN** — delete the generic part, keep only the house-specific remainder (noted per row)
- **THRESHOLD** — keep a one-line rail that records *your chosen number*, because the number is a decision; the check itself stays in the tool

---

## The list

| # | Taxonomy rail | Covered by | Disposition |
|---|---|---|---|
| 1 | **6.1** Formatter config is canonical | Sonar / formatter | DELETE — the config file is the rail |
| 2 | **6.2** Linter config is canonical; inline disables need a ticket | Sonar | THIN — keep only "disables require a ticket reference" |
| 3 | **6.7** Function/class size and complexity guidance | Sonar (cognitive/cyclomatic), CodeScene (Code Health) | THRESHOLD — record your ceiling, delete the guidance prose |
| 4 | **6.9** No magic numbers | Sonar | DELETE |
| 5 | **6.10** Immutability preferences | Sonar (language rules) | THIN — keep only if your codebase has a non-default idiom |
| 6 | **6.11** Null/absence handling idiom | Sonar (null-safety rules) | THIN — keep the *choice* (e.g. "Optional, never null returns"), delete the safety checks |
| 7 | **6.12** Errors never swallowed | Sonar (empty catch, ignored exceptions) | THIN — keep your custom error taxonomy, delete "don't swallow" |
| 8 | **6.13** No floating promises; async correctness | Sonar (async rules) | DELETE |
| 9 | **6.17** TODOs carry a ticket | Sonar (TODO/FIXME rules) | THIN — keep the "must carry a ticket ID" format only |
| 10 | **6.18** Dead-code removal; no commented-out code | Sonar, CodeScene | DELETE |
| 11 | **6.21** Language feature/syntax level policy | Sonar (per-language profile), tsconfig/compiler | DELETE — the compiler config is the rail |
| 12 | — | Duplicated code blocks | Sonar, CodeScene | DELETE — never had a rail; don't add one |
| 13 | — | Deep nesting / arrow code | Sonar, CodeScene | DELETE — same |
| 14 | — | Unused variables, imports, parameters | Sonar | DELETE — same |
| 15 | **7.4** N+1 prohibition | Sonar (some ORMs), CodeScene (hotspots) | THIN — scanner coverage is partial; keep your eager-loading idiom |
| 16 | **8.7** Layering pattern enforced | CodeScene (architectural rules), dependency-cruiser | THIN — keep the *named* pattern and module map; delete generic layering prose |
| 17 | **9.6** Input validation / output encoding (generic) | Sonar Security | THIN — keep "use the blessed schema library X", delete the generic rule |
| 18 | **9.7** Parameterized queries only; no dynamic SQL | Sonar (injection rules) | DELETE |
| 19 | **9.8** SSRF protections on outbound fetches | Sonar Security | THIN — keep your host-allowlist location |
| 20 | **9.10** Approved cryptography; no custom crypto | Sonar (weak crypto rules) | THIN — keep your approved-algorithm list |
| 21 | **9.11** Secrets scanning | Sonar / secret scanners / pre-commit | DELETE — the scanner is the rail |
| 22 | **9.12** Security headers / CSP baseline | Sonar, scanners | THIN — keep your specific CSP policy |
| 23 | **9.13** CORS: no wildcard with credentials | Sonar | DELETE |
| 24 | **12.9** Bundle budgets | bundler/CI checks | THRESHOLD — record the number |
| 25 | **12.10** Web-vitals thresholds | Lighthouse CI | THRESHOLD — record the numbers |
| 26 | **16.x** Generic accessibility violations (alt text, label association, contrast) | axe / a11y linters | THIN — keep pattern-level a11y (focus management, keyboard paths); delete what axe catches |
| 27 | **18.9** Performance thresholds on hot paths | perf tests / CI | THRESHOLD — record the numbers |
| 28 | **18.10** Coverage / mutation thresholds | Sonar quality gate | THRESHOLD — record the numbers |
| 29 | **18.11** Flaky-test detection | CI flake detection | THIN — keep the quarantine *process*, delete detection |
| 30 | **19.5** Vulnerability fix SLA by severity | Sonar / SCA tools | THIN — keep the SLA (a policy), delete the detection |

**Net effect:** roughly 12 rails deleted outright, ~13 thinned to their house-specific remainder, ~5 reduced to a recorded number. Expect `.standards/code.md` and the generic half of `security-privacy.md` to shrink substantially.

---

## What does NOT move to the scanner

Guard against over-deleting. These *look* adjacent but are house-specific and stay in prose:

- **6.3–6.6** naming, file placement, module boundaries, import direction (your structure, not universal)
- **6.8** naming semantics (is/has/can, handler prefixes)
- **6.14–6.15** DI pattern, injected clock/randomness
- **9.1–9.5** your auth integration, permission model, object-level authz, hide-vs-403 rules
- **All of §2** (glossary), **§13** (UX patterns), **§15** (content), **§17** (analytics), **§23** (meta-rules) — no scanner has any opinion here
- Any threshold's *value* — the number is yours even when the check is theirs

---

## AGENTS.md — the scanner authority block

Paste into AGENTS.md. This is the rail that makes every deleted rule above still binding.

```markdown
## Automated checks are law

Lint, format, type, security, and code-health checks are the standard — not advice.
This repo deliberately does not restate in prose what a tool already enforces.

- Fix the finding, never the check. Do not disable, suppress, ignore, baseline,
  or reconfigure a rule to make a build pass.
- No inline suppressions (`// eslint-disable`, `# noqa`, `@SuppressWarnings`,
  `// NOSONAR`, CodeScene ignores) without a ticket ID and a one-line reason
  on the same line.
- Do not restructure code for the sole purpose of moving a metric. If a check
  is wrong, say so in the PR and leave it failing.
- Changing a threshold, quality profile, or gate severity requires an ADR —
  it is a standards change, not a code change.
- A failing check blocks the gate. "Pre-existing failure" is not an exemption
  unless the module is listed in `.standards/exemptions.yaml`.
- Never add a new suppression to clear an inherited failure; fix it or leave it.
- Treat CodeHealth feedback during generation as a required revision, not a hint.
```

Condensed to one line, if you only have room for one:

> **Automated checks are law: fix findings, never suppress them; changing a threshold or disabling a rule requires an ADR.**

---

## Note on maintenance

When a rail graduates from prose to a tool check, delete the prose in the same PR that adds the check. If `.standards/` only ever grows, nothing is graduating — and the files will drift out of agreement with the tools that actually decide.
