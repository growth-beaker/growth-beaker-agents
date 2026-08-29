---
okf_version: "0.2"
type: Reference
title: Template — standards extraction
description: Domain file template and frontmatter contract for extracted standards.
tags: [standards, meta, template]
generated: { by: "claude-code/claude-opus-5", at: "2026-08-28" }
verified: []
stale_after: 2027-02-28
---

# Domain file template

Every `.standards/<domain>.md` follows this shape. Keep files under ~200 lines by cutting explanation, never examples.

## Frontmatter is mandatory

`docs/` in this repo is an [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) v0.2 bundle, and the contract keys on *what a document is, not where it lives* (`docs/index.md`). Standards files are durable cross-cutting reference docs, so they carry the same frontmatter — validated against `SpecFrontmatter` in `packages/hureva`, the single schema this repo has for document metadata.

Every file written into `.standards/` — domain files, `_inventory/` files, and `REVIEW.md` — opens with:

```yaml
---
okf_version: "0.2"
type: Reference
title: <Domain name> standards
description: <one sentence: what this file governs>
tags: [standards, <domain>, extracted]
generated: { by: "claude-code/<model-id>", at: "<YYYY-MM-DD>" }
verified: []          # stays empty until a human signs off in REVIEW.md
stale_after: <YYYY-MM-DD>   # ~6 months out; standards drift
sources:
  - id: inventory
    resource: /.standards/_inventory/<primary>.md
    title: Raw evidence this file was drafted from
---
```

Notes:
- **Do not set `status` or `hureva_status`.** `status` is derived from `hureva_status` and is never hand-set (`hureva.models.OkfStatus`); these files are not enrolled in the review flow. Draft-ness is expressed by `verified: []`.
- `verified` is the review state: an empty list means no human has confirmed these rails. `/compile-standards` appends a `{by: "human:<name>", at: <ts>}` event when a domain file's rulings are signed off.
- `sources` points back at the `_inventory/` evidence, so provenance is machine-readable.

## Body shape

```markdown
# <Domain name> standards
_Drafted from repo evidence on <date>. Taxonomy: §<n>._

## Rails

### <ID> <One imperative line>  `[observed|inferred|gap|external]` `stage:now`
Evidence: `path/one.py`, `path/two.py`
DO:
    <small real example from this repo>
DON'T:
    <the anti-pattern, ideally one actually found>
[enforced: <config/hook name>]   <!-- only when a machine check exists -->

### D3.14 Every tenant-scoped query includes tenant_id  `[observed]`
Evidence: `src/models/scoped.py`, `src/api/accounts.py`
DO:
    Account.for_tenant(ctx.tenant_id).filter(...)
DON'T:
    Account.objects.get(id=account_id)   # unscoped fetch — IDOR
[enforced: scoped-query lint rule]

## Inferred — needs a human ruling
### D6.4 New modules use feature folders  `[inferred]`
Majority: 34 of 41 modules. Exceptions: `legacy/reports/`, `legacy/billing/`
Question: exemption or violation?

## Gaps — repo is silent
### D4.14 API versioning strategy  `[gap]`
Found: no version segments, no deprecation headers.
Options: (a) URL versioning (b) header versioning (c) additive-only, no versions

## External — decided, but the source of truth is outside this repo
### D20.5 Required checks before merge  `[external]`
Lives in: GitHub branch-protection settings for `main`.
Read via: `gh api repos/{owner}/{repo}/branches/main/protection`
Found: <what the probe returned, or "probe unavailable — unauthenticated">
Confirm: is this the intended standard, and should it be mirrored into the repo?

## Covered by tooling — deleted from prose on purpose
§6.9 magic numbers  [covered: ruff PLR2004 — `pyproject.toml [tool.ruff.lint]`]
§6.21 language feature level  [covered: `packages/frontend/tsconfig.json` target/lib]
§18.10 coverage threshold  [threshold: 80% lines — enforced by `vitest --coverage`]

## Not applicable
§4.23 GraphQL (none present) · §4.24 gRPC (none present)
§15.6 ICU pluralization  [n/a — profile: i18n=english-only-permanent]
```

Rules for drafters:
- Every file opens with the OKF frontmatter block above. No exceptions.
- **A rail states an OBLIGATION on future work, never an observation about today's code and never a task.** The test: could a reviewer hold a diff against this line and say yes or no? "Every list endpoint takes `limit`/`offset` and returns a bounded page" passes. "Nothing verifies that a dependency name is real" is an observation — it describes the repo, not a rule. "Adopt a secret scanner" is a task — it is work to schedule, not a rule to follow.
  - **Banned openings** for a rail line: `Nothing…`, `There is no…`, `The repo…`, `Adopt…`, `Add…`, `Build…`, `Install…`, `Write down…`, `Decide…`. If your line starts this way you have written a finding or a backlog item, not a rail.
  - Rewrite to the rule underneath. *"Nothing verifies a dependency name"* → **"Every dependency added is verified to exist on its registry before install."** *"Adopt a secret scanner"* → **"No credential, token, or key is committed."** The tool that enforces it is enablement, not the rail.
  - The evidence that the repo currently violates the rail belongs on the `Found:` / `Evidence:` line, which is exactly where an observation is useful.
  - *("Obligation" here is this toolkit's own term for a rule-shaped rail. It is unrelated to `.alucify/invariants/`, which is a separate system, and distinct from the domain invariants of TAXONOMY §2.8 — the two must not be conflated or made to depend on each other.)*
- **Separate the rule from the work it implies.** One answered gap can yield up to three things, and only the first is a rail:
  - **Rail** — the obligation future work must satisfy. Ships to `AGENTS.md` and path-scoped `CLAUDE.md`.
  - **Remediation** — bringing existing code into compliance ("paginate the 12 endpoints that do not").
  - **Enablement** — adopting the tool or config that lets the rail be enforced ("add gitleaks to pre-commit").
  Write remediation and enablement on their own `Remediation:` / `Enablement:` lines beneath the rail. They are real work and must not be lost — but an agent mid-task needs the rule, not the backlog, and mixing them is what makes a standards file unreadable.
- **Write rails so they cluster.** The review packet collapses gaps into a handful of cross-cutting decisions, and it can only do that if your rails name the underlying decision rather than restating the taxonomy heading. A gap whose real answer is "adopt a secret scanner" should say so — then it groups with the other tooling gaps into one question instead of becoming a lone item nobody gets to. Where several of your rails share one decision, say which in the gap text.
- Rail IDs are `D<taxonomy number>` so every rail traces to the taxonomy.
- One rail = one imperative sentence. If you need a paragraph, it is two rails or it is commentary — cut it.
- Real repo code beats invented examples; invented examples beat prose.
- Tag honestly. An `[observed]` tag with weak evidence poisons trust in the whole file.
- **Every rail carries a `stage:`** — `now`, `ga`, or `scale` — taken from `.standards/PROFILE.yml`. `/compile-standards` puts only `stage:now` rails in front of a working agent; `ga` and `scale` rails stay in this file for the reviewer and are absent from the compiled artifacts entirely. Getting this wrong is expensive in both directions: a mis-staged `ga` rail vanishes from the agent's context, and a mis-staged `now` rail dilutes the ten that matter.
- **The stage floor is absolute.** Any rail whose failure mode is a security breach, a cross-tenant leak, data loss, or an irreversible migration is `stage:now` regardless of what the profile says. Never defer one of these because the product is pre-GA — they are cheapest to install before there is anything to lose. If you are unsure whether a rail is floor-class, it is.
- **Pruning is annotation, never deletion.** A taxonomy item the profile rules out goes under "Not applicable" as `[n/a — profile: <key>=<value>]`, citing the answer that retired it. Never silently drop an item: the annotation is what makes the decision auditable and what lets a later profile change resurface it.
- **Do not restate in prose what a tool already enforces.** A universal rule — one that would read identically at any company — belongs in a lint/format/type/security/code-health config, not in prose an agent must read on every task. Three dispositions, recorded under "Covered by tooling" rather than as rails:
  - **DELETE** — the tool is the standard; write no rail. (`§6.9` magic numbers, `§9.7` parameterized queries, `§6.18` dead code, duplicated blocks, deep nesting, unused imports.)
  - **THIN** — write a rail carrying ONLY the house-specific remainder, and delete the generic half. (`§6.12` → keep your custom error taxonomy, drop "don't swallow exceptions". `§9.6` → keep "validate with the blessed library X", drop the generic rule. `§16.x` → keep focus management and keyboard paths, drop what axe catches.)
  - **THRESHOLD** — write a one-line rail recording *your chosen number*, because the number is a decision even when the check is the tool's. (`§6.7` complexity ceiling, `§12.9` bundle budget, `§18.10` coverage, `§18.9` perf.)
- **A rail may only be marked `[covered: …]` if the tool is configured IN THIS REPO, and you must cite the config path.** "Sonar would catch this" is not coverage if this repo does not run Sonar; deleting the prose then leaves the rule enforced by nothing at all — worse than the duplication you removed. When a rule is universal but no configured tool here enforces it, that is a `[gap]` whose answer is "adopt the tool", not a deletion. Verify against `_inventory/configs.md` before every deletion.
- **Guard against over-deleting.** These look adjacent but are house-specific and stay in prose: §6.3–6.6 (naming, file placement, module boundaries, import direction), §6.8 (boolean/handler naming semantics), §6.14–6.15 (DI pattern, injected clock and randomness), §9.1–9.5 (your auth integration, permission model, object-level authz, hide-vs-403), and all of §2, §13, §15, §17, §23 — no scanner has an opinion on glossary, UX, content, analytics, or meta-rules.
- **`[n/a]` is NOT a fifth tag and never takes a rail heading.** There are exactly four tags. An item that does not apply — whether the profile retired it or the stack simply lacks the thing (no GraphQL, no SSR, no broker) — goes as ONE line under "Not applicable", never as a `### D…` heading. Rail headings are machine-parsed into the rail index, so an `### D12.16 … [n/a]` heading would be counted as a live rail and shipped to agents as a rule. Carry the evidence on the Not-applicable line itself rather than promoting it to a rail: `§12.16 SSR/hydration — pure Vite SPA; main.tsx calls createRoot, no hydrateRoot, no server entry.`
- `[gap]` and `[external]` are different failures and must not be conflated. `[gap]` = nobody decided. `[external]` = somebody decided, but the artifact lives outside this repo (cloud console, IdP tenant, VCS host settings, dashboards). Guessing `[gap]` when the answer is sitting in a GCP or GitHub setting wastes the reviewer's time; guessing `[external]` when nothing was ever decided hides a real hole. If a probe was available and you ran it, quote what it returned.
