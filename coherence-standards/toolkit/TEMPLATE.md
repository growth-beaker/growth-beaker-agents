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
generated:
  by: "coherence-standards/<plugin version>"   # the toolkit that produced this
  model: "<model-id>"                          # what drafted it
  taxonomy_version: "<from PROFILE.yml>"       # what it was scored against
  at: "<YYYY-MM-DD>"
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
- **`generated.by` names the toolkit, not the model.** The model is recorded separately, but the toolkit version and `taxonomy_version` are what actually explain a file's shape: rail IDs trace into a taxonomy that moves, and the drafting rules in this template move too. A file stamped only with a model id cannot be read against the rules it was written under, and a rail whose `D6.4` resolves to a different taxonomy item than it did at drafting time is worse than an unstamped one.

## Body shape

```markdown
# <Domain name> standards
_Drafted from repo evidence on <date>. Taxonomy: §<n>._

## Rails

### <ID> <One imperative line>  `[observed|inferred|gap|external]` `stage:now`
Evidence: `path/one.py#L12-L48`, `path/two.py#L88-L104`
DO:
    <small real example from this repo>
DON'T:
    <the anti-pattern, ideally one actually found>
[enforced: <config/hook name>]   <!-- only when a machine check exists -->

### D3.14 Every tenant-scoped query includes tenant_id  `[observed]`
Evidence: `src/models/scoped.py#L31-L44`, `src/api/accounts.py#L112-L128`
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

## Evidence anchors

An `Evidence:` path with no line range is not evidence — it is a hint. A rail tagged
`[observed]` asserts that this repo does a thing today, and that assertion has to stay
checkable after the code moves. **Every `Evidence:` entry that points at a file cites a line
range: `path/to/file.py#L12-L48`.** Ranges are 1-indexed and inclusive.

Three lines take ranges and one does not:

| Line | Ranges? |
|---|---|
| `Evidence:` on an `[observed]` or `[inferred]` rail | **Required** — this is the anchored claim |
| `Majority:` / `Exceptions:` on an inferred rail | Ranges where the citation is a specific block; a bare directory (`legacy/reports/`) stays bare |
| `Found:` on a `[gap]` | Only if it cites a specific block. A gap's evidence is usually an absence, and an absence has no line number |
| `Found:` / `Lives in:` on an `[external]` | **No** — the artifact is not in this repo. The probe command is the anchor |

Pick the *smallest span that supports the rail*: the function, the policy block, the config
key — not the file, and not one line of a construct that spans twelve. An anchor that is too
wide reports a change on every unrelated edit; one that is too narrow relocates poorly.

### What gets hashed, and why the split matters

Ranges alone rot — a file gets a new import at the top and every range below it is off by one,
though nothing the rail describes has changed. `/compile-standards` therefore records, in the
`_claims/` sidecar (never in this prose), five hashes per anchor:

| Field | Content | Normalization |
|---|---|---|
| `range` | the selected lines, joined `\n` | **exact** |
| `first` / `last` | the first and last selected line | normalized |
| `before` / `after` | the 3 lines on each side of the span | normalized |
| `lines` | count of selected lines | — |

*Exact* means the line as committed. *Normalized* means line endings to `\n`, then leading and
trailing whitespace stripped per line, then joined with `\n`. All five are `sha256`, lowercase
hex, over UTF-8.

The split is the whole mechanism. `range` is exact, so it answers **"did this code change?"**
— any edit inside the span breaks it. The other four are whitespace-normalized, so they answer
**"where did this code go?"** — a re-indent, a reformat, or 200 lines inserted above leaves the
fingerprint intact and the block findable at its new offset. One hash cannot do both jobs: an
exact whole-file hash reports every rail stale on every commit, and a fuzzy one never reports
anything stale at all.

Where fewer than 3 lines exist on a side (span at the top or bottom of the file), hash what is
there; where none exist, hash the empty string.

### The five statuses

A verifier re-reads each anchor and returns one of:

- **`current`** — `range` matches at the recorded line numbers. The rail's evidence is intact.
- **`moved`** — `range` failed there, but a window of `lines` lines elsewhere in the file matches
  `first`, `last`, `before`, and `after`. The code is unchanged and the anchor needs renumbering.
  Not a review trigger; a mechanical fix.
- **`changed`** — `before` and `after` match at some position but the interior does not. The code
  the rail rests on was edited. **This is the review trigger** — an `[observed]` rail whose
  evidence changed may now describe something the repo no longer does.
- **`lost`** — the file exists, nothing matches. Treat as `changed`, but the rail needs re-drafting
  from scratch rather than re-confirming.
- **`missing`** — the file is gone. Often means the rail is obsolete; sometimes means it moved
  and only a human can say which.

A rail's status is the **worst** status among its anchors, and a domain file's is the worst among
its rails. Order: `current` < `moved` < `changed` < `lost` < `missing`.

This is what makes `stale_after` a fact instead of a guess. The date stays — standards drift for
reasons no hash can see, and a rail nobody has looked at in a year deserves a look regardless —
but "41 of 352 rails cite code that changed since review" is the number that actually routes
attention, and it is the number `/check-compliance` needs to know whether a rail still describes
this repo before it holds a diff against it.

Rules for drafters:
- Every file opens with the OKF frontmatter block above. No exceptions.
- **Cite a line range on every file-backed `Evidence:` entry**, per "Evidence anchors" above. Do
  not compute or write hashes — `/compile-standards` derives those into `_claims/` from the ranges
  you cite. Your job is to pick the right span.
- **Never cite a range you did not read.** An anchor is a claim that these specific lines support
  this specific rail; a plausible-looking range guessed from a grep hit is worse than no range,
  because it will verify `current` forever while pointing at the wrong thing.
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
