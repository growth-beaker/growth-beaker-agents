# Extract coherence standards from this repository

Generate draft engineering standards for this repo by mining its existing artifacts against the taxonomy in `${CLAUDE_PLUGIN_ROOT}/toolkit/TAXONOMY.md`. Optional argument: a domain filter (e.g. `api`, `data`, `frontend`) to run one domain only: $ARGUMENTS

## Ground rules

- **Read-only with one exception:** you may only write inside `.standards/`. Never modify source code, configs, or anything else during extraction.
- **Evidence over invention.** Every rail you draft must be tagged:
  - `[observed]` — the repo does this consistently (cite 2–3 file paths as evidence)
  - `[inferred]` — majority pattern with exceptions (name the exceptions and their paths)
  - `[gap]` — the taxonomy says a decision is needed but the repo is silent or contradictory (write the question, not an answer)
  - `[external]` — the decision was made, but its source of truth lives outside this repo (cloud console, IdP tenant, VCS host settings, analytics dashboards). Name where it lives, the command that reads it, and what the probe returned. This is a *confirm-and-mirror* item for the human, not a decision.
- **`[gap]` and `[external]` are not interchangeable.** `[gap]` means nobody decided; `[external]` means somebody decided somewhere you cannot see from a file read. Scoring an externally-configured standard as a gap manufactures busywork; scoring an undecided one as external hides a real hole. When a probe is available, run it and quote the result rather than assuming either way.
- **A rail states an obligation on future work — never an observation, never a task.** The test is whether a reviewer could hold a diff against it. "Every list endpoint returns a bounded page" is a rail; "Nothing paginates" is a finding about today's code; "Add pagination" is a backlog item. A `[gap]` asks *"what rule should govern this?"*, never *"what is missing?"* — the second phrasing reliably produces task-shaped answers that cannot be applied to a future change. Banned rail openings: `Nothing…`, `There is no…`, `The repo…`, `Adopt…`, `Add…`, `Build…`, `Install…`, `Write down…`, `Decide…`. Full guidance and the rewrite pattern are in TEMPLATE.md.
- **Keep the rule separate from the work it implies.** An answered gap yields a **rail** (the obligation), and often also **remediation** (making existing code comply) and **enablement** (adopting the tool that enforces it). Only the rail reaches a working agent; the other two are backlog. Record them on `Remediation:` / `Enablement:` lines so they are not lost, but never let them stand in for the rail.
- **Never resolve a `[gap]` yourself.** Gaps are questions for humans. Inventing an answer defeats the purpose.
- **Configs are ground truth.** Where a lint/format/CI config already encodes a standard, the rail is one line pointing at the config — do not restate config contents as prose.
- **Do not restate in prose what a tool already enforces.** A universal rule — one that would read identically at any company — belongs in the tool's ruleset. Record it under "Covered by tooling" with one of three dispositions (DELETE / THIN / THRESHOLD, defined in TEMPLATE.md) instead of writing a rail. This is what keeps `code.md` and the generic half of `security-privacy.md` from becoming prose an agent skims past.
- **`${CLAUDE_PLUGIN_ROOT}/toolkit/SCANNER-COVERAGE.md` lists the ~30 taxonomy items that are scanner candidates**, each with a DELETE / THIN / THRESHOLD disposition and a "what does NOT move to the scanner" guard list. The same items are marked inline in TAXONOMY.md as `` `[scanner: …]` ``. A drafter that hits a marked item MUST consult that file before writing a rail. Items without the marker are house-specific by default — do not invent coverage for them.
- **Coverage must be real and local.** Mark a rail `[covered: …]` only when the tool is configured IN THIS REPO, citing the config path from `_inventory/configs.md`. The `[scanner: …]` marker says an item is a *candidate*, never that it is covered here — the marker plus a missing tool equals a `[gap]` whose answer is "adopt the tool". "Sonar would catch this" is not coverage in a repo that does not run Sonar — deleting the prose then leaves the rule enforced by nothing, which is strictly worse than the duplication. A universal rule that no configured tool here enforces is a `[gap]` whose answer is "adopt the tool", never a deletion.
- **Every file you write carries OKF frontmatter** per `${CLAUDE_PLUGIN_ROOT}/toolkit/TEMPLATE.md` — domain files, `_inventory/` files, and `REVIEW.md` alike. Read TEMPLATE.md before writing anything.

## Preflight — never destroy a prior run

`.standards/` is frequently untracked, so an overwrite here is unrecoverable. Before writing anything:

**1. Separate inputs from outputs.** The toolkit lives OUTSIDE `.standards/` entirely, at `${CLAUDE_PLUGIN_ROOT}/toolkit/` (`TAXONOMY.md`, `TEMPLATE.md`) — an extraction never writes there. Inside `.standards/`, the only non-output files are `PROFILE.yml` and anything under `_runs/`; never archive or overwrite either. Everything else in `.standards/` is output from a previous run.

**2. Detect human work.** A prior run is *answered* if any of these is true:
- a domain file's frontmatter has a non-empty `verified:` list
- `REVIEW.md` has any `**Answer:**` line with text after it
- `exemptions.yaml` exists with a real (non-`TBD`) owner or expiry

**3. Branch on what you found.**
- **Answered prior run → STOP.** Report exactly which files carry human work and how much (count the answered questions), and ask before continuing. Do not archive, do not overwrite, do not "merge" — a human's rulings are the most expensive artifact in this directory and re-deriving them is not free. Wait for an explicit go-ahead.
- **Unanswered prior run →** move every output file to `.standards/_runs/<YYYY-MM-DD-HHMM>/` (preserving `_inventory/` structure), report the destination, then proceed. Use a minute-resolution timestamp, not a run counter: a counter has to be derived by scanning existing directories, and two runs in one day collide or silently overwrite. Move, never delete.
- **No prior run →** proceed.

**4. Archive by moving, never by copying-then-truncating,** so a crash mid-run cannot leave both copies half-written.

Re-running is a normal operation — a taxonomy bump, a profile change, or a big refactor all justify one. The point of this preflight is that re-running is never *lossy*, so nobody has to weigh "is it worth losing the old one."

## Phase 0 — Profile (ask once, reuse forever)

The taxonomy is written for enterprise brownfield and is deliberately over-complete. Without a profile, drafters score items as `[gap]` that were never live for this product, and the reviewer pays for it. The profile is what lets a drafter say "not applicable" with a cited human answer instead of a guess.

**If `.standards/PROFILE.yml` exists, read it and skip to Phase 1.** Do not re-ask. If it exists but its `answered_at` is older than a year, note the staleness in your Phase 0 report and continue — do not re-ask unprompted.

Otherwise ask the user these, using `AskUserQuestion` (two calls of ≤4), then write `.standards/PROFILE.yml`:

| Key | Question | Values |
|---|---|---|
| `stage` | What stage is the product at? | `pre-ga` · `ga` · `scaling` |
| `compliance` | What compliance regime applies? | `none` · `soc2-in-progress` · `soc2-certified` · `regulated` |
| `i18n` | Localization intent? | `english-only-permanent` · `english-only-for-now` · `multi-locale` |
| `api_consumers` | Who consumes the HTTP API? | `first-party` · `first-party-plus-cli` · `public` |
| `operators` | Who operates this in production? | `authors` · `separate-on-call` · `nobody-yet` |
| `residency` | Data-residency commitment to customers? | `none` · `single-region` · `multi-region` |
| `out_of_scope` | Anything deliberately out of scope right now? | free text |
| `never_edit` | Any module that may only be wrapped, never edited? | free text → §23.3, §23.4 |

Ask plainly. Do not attach gap-count estimates to the questions — those are extrapolations, and dressing a question in a number it cannot support pressures the answer.

`PROFILE.yml` carries OKF frontmatter plus:

```yaml
profile_version: 1
answered_at: "<YYYY-MM-DD>"
answered_by: "human:<name>"
stage: pre-ga
compliance: none
i18n: english-only-for-now
api_consumers: first-party-plus-cli
operators: authors
residency: none
out_of_scope: ["<verbatim>"]
never_edit: ["<verbatim>"]
```

### How the profile is used — and its two hard limits

Drafters use it to do three things, in this order of preference:

1. **Reclassify** — the answer shows a standard exists off-repo → `[external]`, not `[gap]`.
2. **Stage** — the rail applies but is premature → `stage:ga` or `stage:scale`. The finding survives intact; only its urgency changes.
3. **Prune** — the item can never apply under this profile → `[n/a — profile: <key>=<value>]` under "Not applicable".

Staging is the common case and pruning the rare one. A drafter that prunes aggressively is doing it wrong: expect a handful of genuine prunes per run, not dozens.

**Limit 1 — the stage floor.** Security, tenant-isolation, data-loss, and irreversible-migration rails are `stage:now` under every profile. `stage: pre-ga` must never defer secrets scanning, an authz check, or a destructive-migration rule. These are cheapest to install before there is anything to lose, and a profile that defers them is being used to make the packet look clean.

**Limit 2 — a profile answer is not evidence.** It narrows *which taxonomy items are live*; it never substitutes for repo evidence about what the code does. `compliance: none` retires §10.10; it does not let you tag anything `[observed]`.

## Phase 1 — Inventory (deterministic, no judgment)

Create `.standards/_inventory/` and populate it with raw facts. Adapt to the stack you find; skip what doesn't exist:

1. `stack.md` — languages, frameworks, package manifests, lockfiles present; toolchain versions
2. `configs.md` — every lint/format/type/security/code-health/CI config found, with paths (these become Tier-1 rails). **For each tool, record what it ACTUALLY enforces here, not what that class of tool typically enforces** — the enabled rule set, the ruleset name or profile, the thresholds, and whether CI runs it in blocking or advisory mode. A drafter deletes prose on the strength of this file, so an overstated entry silently removes a rule from the standard. Explicitly list the scanners that are ABSENT (Sonar, CodeScene, Semgrep, CodeQL, Snyk, Lighthouse, axe, secret scanners, SCA) — an absent scanner is why a universal rule stays a `[gap]` instead of becoming a deletion.
3. `schema.md` — database schema dump or model inventory; the last 20 migrations verbatim (migration history is the richest source of data conventions)
4. `api.md` — route table; the OpenAPI/proto/GraphQL schema files if present; 5 representative endpoint implementations pasted as exemplars
5. `frontend.md` — component directory tree (2 levels); token/theme files; router config; the 10 most-imported components
6. `events.md` — topics/queues/schemas if a broker or event system exists
7. `git.md` — 30 most-recently-changed files (style exemplars); commit message samples (last 50 subjects); branch names; CODEOWNERS if present
8. `deps.md` — direct dependency list with licenses if derivable
9. `docs.md` — paths of any existing ADRs, style guides, glossaries, spec templates, onboarding docs
10. `external.md` — standards that live outside the repo tree (see below)
11. `graph.md` — import-graph facts a file read cannot produce (see below)

Use `Bash` for all of this. Prefer `git log`, `ls`, `grep`/`rg`, and direct file reads. Do not install anything.

### Import-graph facts (`graph.md`)

Reading files tells you what a module says; it does not tell you what the module *graph* does. Cycles, chokepoints, and unreferenced modules are invisible to a drafter reading exemplars, and they stay invisible no matter how many files it reads — an extraction without this step reliably ships zero rails about any of them. Feeds §6 (structure), §8 (architecture), §18 (test coverage).

**Write the script; do not reach for a generic tool.** Off-the-shelf architecture analyzers score badly here for one reason: they do not know this repo's conventions, so they report the test layout as missing tests, `__init__.py` and migrations as dead code, and parent-package imports as cycles. You have read `stack.md` and `configs.md` and can encode the real conventions. That knowledge is the whole advantage — spend it.

For each first-party language, write and run `.standards/_inventory/graph.<ext>` (starting points: `${CLAUDE_PLUGIN_ROOT}/scripts/graph.py` and `graph.mjs`) using **only the standard library** — no installs, no `node_modules` walk, no compiler invocation. Resolve imports to first-party modules (honor path aliases from `tsconfig.json` / package manifests), then report:

- **Cycles** — strongly connected components of the module graph (Tarjan is ~10 lines). Report each cycle's members and, for each edge, whether it is a deferred/function-local/bottom-of-file import, which usually means it is a deliberately managed seam rather than a defect.
- **Chokepoints** — highest fan-in modules (what everything depends on) and highest fan-out modules (what carries the most coupling).
- **Modules with zero inbound edges** — after excluding entrypoints, `__init__`/barrel files, migrations, generated types, test infrastructure, and anything the framework loads by convention rather than by import. List every exclusion you applied and why.
- **Source files with no test pair** — using *this* repo's test layout as found in `configs.md`, not a guessed convention.

Save the script next to its output. It costs nothing and makes the run auditable, re-runnable, and diffable against the next extraction — determinism without a dependency.

**These are inventory inputs, not findings.** Regex import extraction misses dynamic imports, re-export barrels, and string-built paths, so treat every number as a lead a drafter must verify against the code. An orphan list is `[inferred]` with candidate paths named — never an assertion that code is dead. Record the method's limits in the file so the drafter reading it knows what it cannot see.

### Adjacent sources (`external.md`)

A repo read alone cannot see standards configured in a cloud console, an identity provider, or the VCS host. Left unprobed these get mis-scored as `[gap]`, and the reviewer is asked to decide something already decided. Probe what you can, **read-only**, and record the raw result — the probe output is the evidence a drafter cites for an `[external]` tag.

Run only the probes that fit the stack you found in `stack.md` / `configs.md`. Every one is optional: if the CLI is missing, unauthenticated, or errors, **record that fact verbatim and move on** — never install a CLI, never authenticate, never prompt for credentials, and never run a mutating subcommand.

- **VCS host** (if `gh` is present and authed): branch protection and required checks (`gh api repos/{owner}/{repo}/branches/{default}/protection`), repo-level settings (`gh repo view --json …`), rulesets, and whether a CODEOWNERS is enforced. Feeds §20.5, §20.8, §20.9.
- **Cloud runtime** (if `gcloud` / `aws` / `az` is present and authed, and the deploy config names a service): the deployed service's config — env vars, scaling bounds, traffic split, log/retention settings. Feeds §11 (observability), §21.4/§21.8/§21.9 (environments, rollback, progressive delivery).
- **Identity provider** (Auth0/Okta/Entra): only what the repo's own committed config or docs reveal. Do **not** call a management API with credentials from `.env`. Feeds §9.1–9.2.
- **Analytics / dashboards**: whether a tracking plan or metric registry exists outside the repo, inferred from committed config and docs. Feeds §17.3, §17.7.
- **CI history** (if `gh` is authed): recent workflow run names and outcomes, which reveal required checks not visible in the workflow files themselves.

Record for each: what you probed, the exact command, and the raw output or the failure reason. Mark anything you could not reach as `probe unavailable` with the reason — an honest "unauthenticated" beats a guess, and it tells the reviewer which probes to re-run themselves.

## Phase 2 — Domain drafting (parallel subagents)

For each taxonomy domain below (or only the one matching $ARGUMENTS), dispatch a subagent. Run up to 4 in parallel per batch. Each subagent receives: its taxonomy section (read from `${CLAUDE_PLUGIN_ROOT}/toolkit/TAXONOMY.md`), the relevant `_inventory/` files, and the output template in `${CLAUDE_PLUGIN_ROOT}/toolkit/TEMPLATE.md`.

| Domain file | Taxonomy sections | Primary inventory |
|---|---|---|
| `glossary.md` | §2 | schema, api, frontend, docs |
| `data.md` | §3 | schema |
| `api.md` | §4, §5 | api, events |
| `code.md` | §6, §7 | configs, git, graph |
| `architecture.md` | §8 | docs, stack, api, graph |
| `security-privacy.md` | §9, §10 | configs, api, deps |
| `observability.md` | §11 | configs, code samples, external |
| `frontend.md` | §12 | frontend |
| `ux-patterns.md` | §13, §14, §15, §16 | frontend |
| `analytics.md` | §17 | frontend, api |
| `testing.md` | §18 | git, configs, graph |
| `deps.md` | §19 | deps, configs |
| `vcs.md` | §20 | git, external |
| `build-deploy.md` | §21 | configs, external |
| `ai-features.md` | §22 | only if the app embeds LLM features |
| `meta-rules.md` | §23 | docs, git blame on oldest modules — expect mostly `[gap]` |

Each subagent writes `.standards/<domain>.md` following `${CLAUDE_PLUGIN_ROOT}/toolkit/TEMPLATE.md` exactly: OKF frontmatter, then rail ID, one imperative line, a DO/DON'T example pair drawn from real repo code where possible, evidence paths, and the tag. Skip taxonomy items that don't apply to this stack — note them in one line at the bottom of the file under "Not applicable".

Give every subagent `.standards/PROFILE.yml`, `_inventory/external.md`, and `${CLAUDE_PLUGIN_ROOT}/toolkit/SCANNER-COVERAGE.md` alongside its primary inventory, and tell it explicitly:

- Any taxonomy item marked `` `[scanner: DELETE|THIN|THRESHOLD]` `` requires a coverage check against `_inventory/configs.md` BEFORE a rail is written. Covered here → record it under "Covered by tooling" with the config path. Not covered here → it stays a normal rail or a `[gap]`; the marker alone never justifies a deletion.

- Before scoring anything `[gap]`, check whether `external.md` already answers it. A standard visible in a probe is `[external]`, not a gap.
- Before scoring anything `[gap]`, check whether the profile stages it. Prefer `stage:ga` over a gap the product is not ready to answer.
- Prune only what the profile makes impossible, and always with the `[n/a — profile: …]` citation. Never prune on your own judgment about what "probably doesn't matter here".
- The stage floor overrides everything: security, tenant-isolation, data-loss, and irreversible-migration rails are `stage:now` no matter what the profile says.

## Phase 3 — The review packet

After all domains complete, write `.standards/REVIEW.md`:

**The packet's job is to make review tractable, not to be exhaustive.** A file with one question per rail produces 200+ decisions on a small repo, which no one will work through — and an unreviewed packet is worth nothing. Rails are not independent: they cluster into far fewer real decisions, and the packet must do that collapsing rather than pushing it onto the reviewer. Aim for **under ~40 human interactions** regardless of rail count. If the draft exceeds that, collapse harder — do not ship it and hope.

Four mechanisms do the collapsing. Apply them in this order:

**A. Theme decisions.** Cluster the `stage:now` gaps by the underlying decision, not by taxonomy section. One question — *"adopt a formatter, secret scanner, SCA, and import-boundary linter, or accept these rules stay unenforced pre-GA?"* — resolves every gap whose answer is "adopt the tool". Typical themes: tooling adoption, merge gating, public-API contract posture, privacy baseline, observability baseline, accessibility target, decision records, IaC and rollback. Give each a `T<n>` id and **list the rail IDs it resolves**, so one answer cascades and the reviewer can see exactly what it moved. Expect 6–12 themes covering roughly half the gaps.

**B. Profile-key grouping for prunes.** Prunes trace back to a handful of profile answers, so group them by the answer that caused them (`residency=none`, `out_of_scope=self-hosted`, …) and ask once per key, listing the items each retires. Never bulk-confirm across keys — a prune removes a question permanently.

**C. A default ruling for `[inferred]`.** State the default once: *the majority pattern is the standard; the named exceptions are violations to fix.* Apply it wholesale, then break out ONLY the items where the domain file argued the exception is legitimate. Those get individual rulings; the rest ride the default. Expect 5–10 breakouts, not 50.

**D. Proposed answers for the long tail.** For a gap that no theme covers, draft the answer the evidence supports and write it on a `**Proposed:** ` line beneath the question, with one line of reasoning. The reviewer skims and overrides rather than composing from scratch — reading is far cheaper than answering.

> **`**Proposed:**` is NOT an answer and must never be treated as one.** The `**Answer:** ` slot stays empty until a human fills it. A proposal that silently became a rail would be exactly the invention this whole process exists to prevent. `/compile-standards` refuses to compile a rail whose only support is a proposal.

### Structure

0. **The profile in force**, quoted from `PROFILE.yml`. Then prunes **grouped by profile key** (mechanism B), each group listing the items it retires with one `**Answer:** ` per group. A prune the human disagrees with is the most dangerous output of the run, so it is read first.
1. **Summary counts** per domain: observed / inferred / gap / external, split `stage:now` vs deferred. Say plainly how many human interactions the packet asks for.
2. **Theme decisions** (mechanism A) — the `T<n>` questions, each with its resolved rail IDs and an `**Answer:** `. This is the highest-leverage section; it comes before the per-rail detail.
3. **Gaps that bind now**, grouped by domain, each carrying `**Resolved-by:** T<n>` if a theme covers it, or a `**Proposed:** ` line if not. Only items that are neither theme-covered nor safely proposable get a bare open question.
4. **Inferred** — the blanket default stated once, then only the breakout items (mechanism C).
5. **External** — confirm-and-mirror, not decisions. One bulk-confirm question plus the per-item detail for reference. Note which clear with a re-probe rather than a ruling.
6. **Precedence order** (§23.1) for explicit sign-off — candidates carried forward, none chosen.
7. **Candidate exemptions** for `exemptions.yaml`, separating profile-signed decisions from genuine candidates.
8. **Deferred** — `stage:ga` / `stage:scale` gaps, listed for reference with NO answer slots. They neither reach an agent nor block the compile; they are the worklist for the next stage transition, not work for today. Keeping them out of the answer flow is what holds the interaction count down.

Every question carries an inline `**Answer:** ` slot. Deferred items deliberately carry none.

End by telling the user they have two ways to work through the packet, and that the two interoperate freely — both write to the same slots, so they can switch at any point:
- **`/review-standards`** — walks the open questions conversationally, prioritised cheapest-and-most-consequential first, writing answers back after each batch. Better for a large packet: it orders the work and carries the evidence into each question.
- **Editing `REVIEW.md` directly** — type after each `**Answer:** `. Better for a handful of items, or when the answer needs composing rather than choosing.

Then `/compile-standards`.

Report progress after each phase. Total expected output: `.standards/_inventory/` (11 files plus the graph script(s)), one file per applicable domain, and REVIEW.md — all carrying OKF frontmatter.
