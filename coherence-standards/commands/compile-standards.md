# Compile confirmed standards into agent-consumable form

Run this after a human has reviewed and answered `.standards/REVIEW.md`. This pass turns confirmed rails into the artifacts agents actually consume.

## Inputs

- `.standards/PROFILE.yml` — the answers that staged and pruned the taxonomy
- `.standards/*.md` domain files (updated per review answers — resolve every `[inferred]`, `[gap]`, and `[external]` the human answered; delete rails they rejected)
- `.standards/REVIEW.md` with inline answers

## Split every answered item before compiling anything

An answered gap usually contains three different things, and shipping them together is what makes a standards file unreadable. Separate them first:

| | What it is | Where it goes |
|---|---|---|
| **Rail** | The obligation future work must satisfy | `AGENTS.md`, path-scoped `CLAUDE.md` |
| **Remediation** | Bringing existing code into compliance | `.standards/_backlog.md` |
| **Enablement** | Adopting the tool or config that enforces the rail | `.standards/_backlog.md` |

An agent mid-task needs the rule. It does not need "install gitleaks" in its context on every request — it needs "no credential, token, or key is committed." Remediation and enablement are real work and must survive into the backlog with their rail ID, but they never reach `AGENTS.md`.

**Derive the rail if the answer did not state one.** Extraction runs before this rule existed produced observation-shaped and task-shaped lines — `Nothing verifies a dependency name`, `Adopt a secret scanner`, `Write down how to roll back`. Rewrite each into the obligation underneath, keeping the original text as the remediation or enablement entry:

- *"Adopt a secret scanner"* → rail **"No credential, token, or key is committed"**; enablement *"add gitleaks to pre-commit and CI"*.
- *"Write down how to put the last good revision back"* → rail **"Every deployed service has a written rollback procedure"**; remediation *"write the Cloud Run revision runbook"*.
- *"Run the sweeper as a Cloud Run Job"* → rail **"Every recurring job declares an owner, a schedule, and overlap protection"**; remediation *"migrate `anon_reaper` off the FastAPI lifespan"*.

If an answer contains only work and no derivable rule, it is backlog and no rail is emitted — say so in the summary rather than inventing a rule to justify it. *(This toolkit's "obligation" is unrelated to `.alucify/invariants/` and distinct from TAXONOMY §2.8's domain invariants; keep all three separate.)*

## The filter (read before writing anything)

**Only `stage:now` rails reach a working agent.** `stage:ga`, `stage:scale`, and `[n/a — profile: …]` items stay in the domain files for the reviewer and are **absent** from every compiled artifact — not annotated, not badged, not listed as deferred. An agent that reads "deferred until GA" has already spent context on the thing you were trying to keep out of its way; the badge costs nearly as much as the rail.

Three audiences, three views. Keep them separate:

| Audience | Sees | Artifact |
|---|---|---|
| Coding agent, mid-task | `stage:now`, scoped to the paths it touches | `AGENTS.md`, path-scoped `CLAUDE.md` stubs |
| Reviewer at the gate | everything staged, with reasons | `.standards/<domain>.md`, `_deferred.md` |
| The next extraction run | everything incl. pruned items | domain files + `PROFILE.yml` |

If `PROFILE.yml` is absent, treat every rail as `stage:now` and say so in the summary — an unprofiled compile is valid but noisier, and the human should know which one they got.

## Preflight — never regress human work

This pass writes into the repo proper (`AGENTS.md`, path-scoped `CLAUDE.md` stubs), so it is the more dangerous of the two commands. Before writing:

- **Archive prior compiled artifacts** to `.standards/_runs/<YYYY-MM-DD-HHMM>-compile/` — `INDEX.md`, `_deferred.md`, `rails.json`, `_hooks-proposed.md`, `_claims/`, and copies of the `AGENTS.md` / `CLAUDE.md` regions you are about to touch. Move or copy, never truncate in place. The archived `_claims/` is what makes the next run able to say *which* rails went stale between two compiles rather than only that some did.
- **Verify the prior run's anchors before writing new ones.** If `.standards/_claims/` exists, re-resolve every anchor in it against the working tree first and report the counts by status. A rail that comes back `changed` or `lost` was reviewed against code that no longer exists, and compiling it into `AGENTS.md` ships a rule the repo may have already abandoned. Do not block on this — report it, list the affected rails, and offer `/review-standards` — but never let a re-compile launder a stale rail into a fresh-looking artifact.
- **Never shorten a `verified:` history.** Appending a new event is the only legal edit; if a domain file's `verified` list would lose an entry, stop — something is wrong with the merge.
- **Never overwrite `exemptions.yaml` entries that carry a real owner or expiry.** Merge new candidates in; leave confirmed ones untouched. An exemption a human signed is a decision, not a derived artifact.
- **`AGENTS.md` and `CLAUDE.md` are merge-only.** Write inside clearly delimited markers (e.g. `<!-- standards:begin -->` … `<!-- standards:end -->`) so a re-compile replaces only its own region and hand-written content outside the markers survives untouched. If the markers are absent on an existing file, insert them around your addition rather than rewriting the file.
- If anything above would be violated, **stop and report** rather than proceeding with a best-effort merge.

If REVIEW.md still contains unanswered `stage:now` `[gap]` items, stop and list them — do not compile around open decisions that bind today. Offer `/review-standards` to work through them conversationally, or the human can type into the slots directly.

**A `**Proposed:** ` line is not an answer.** It is a draft the extraction wrote for the human to accept or override, and an item carrying only a proposal counts as UNANSWERED. Never promote one to a rail, never treat it as consent, and never let its presence satisfy the check above — a proposal that compiled itself would be precisely the invention this process exists to prevent. Count them separately in the summary so the human sees how many drafts are still awaiting a decision.

**An answer marked `(via theme T<n>)` IS a real answer.** It was cascaded from a theme question the human answered deliberately, and the annotation records provenance rather than weakening it. Treat it exactly as a directly-typed answer, and preserve the annotation so a later reader can trace how it was decided.

Unanswered **deferred** gaps (`stage:ga` / `stage:scale`) do not block: they are staged out of the agent's context anyway, so compiling without them changes nothing an agent sees. Report them in the summary as the worklist for the next stage transition.

**Check rail IDs are unique before compiling.** Every artifact this pass writes cites rail IDs so prose can be traced back, and drafters working in parallel routinely land the same ID on different rails — a domain file can even reuse one across a rail, an inferred pattern, and a gap. Traceability then breaks silently: the citation resolves to the wrong rule, or to three. Collect every `^### D<n>.<n>` heading across the domain files, and if any ID appears twice, stop and list the collisions with their files and headings so the human can suffix them (`D20.1a` / `D20.1b`). Do not renumber on your own judgment — an ID may already be cited in a plan, a PR, or a commit.

Unanswered `[external]` items do **not** block the compile: the standard exists, it just is not readable from the repo. Compile the rail with its off-repo location named, and list every unconfirmed one in the final summary so the human knows which rails an agent cannot verify locally. An `[external]` rail the human answered "mirror it in" becomes a normal rail plus an entry in the hook proposals (§5) for a check that reads the external source.

## Outputs

1. **`AGENTS.md`** (repo root; if one exists, merge — never clobber existing content). Target ≤150 lines:
   - The ten always-on rules: select **from `stage:now` rails only** by three criteria — universal (applies to every task), cheap to state (one line), catastrophic to miss. A deferred rail can never be an always-on rule however catastrophic it would be later; if that feels wrong for a specific rail, the rail is mis-staged and belongs at `stage:now`. Candidates in priority order: glossary verbatim / no synonyms (§2.1–2.2); extend-don't-duplicate entities and services (§2.4, §8.4); tenant scoping on every query (§3.14–15) if multi-tenant; dependency allowlist (§19.1); configs are law (§6.1–2); wrap-don't-modify list (§23.4); declared deviations only (§1.12); propose-don't-invent (§23.5); the signed precedence order (§23.1); no PII in logs/events/URLs (§10.7)
   - The router table: task type → `.standards/<file>` to read first. **Omit any domain whose active rail count is zero** — sending an agent to read a file that has nothing live in it is worse than not listing it.
   - **"Deliberately out of scope"** — 3–5 lines, drawn from `PROFILE.yml`'s pruned items and `out_of_scope`. Pruning creates negative space that a helpful agent will fill: prune i18n and an agent adds a message catalog nobody asked for. State the decision so the absence reads as intentional — *"English-only by decision (profile: i18n); no message catalog, do not add one."* This is the one place a pruned item is allowed to appear, and only as a prohibition, never as a rail.
   - **The scanner authority block** — this is what keeps every rail deleted as tool-covered still binding, so it is not optional whenever any domain file has a "Covered by tooling" section. Include it verbatim:
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
     - Treat code-health feedback during generation as a required revision, not a hint.
     ```
     If space is tight, the one-line form is: *"Automated checks are law: fix findings, never suppress them; changing a threshold or disabling a rule requires an ADR."*
   - The workflow line: "plans and PRs cite the rail IDs they rely on"
   - Pointers: spec template, gate checklist, `exemptions.yaml`
2. **Path-scoped `CLAUDE.md` stubs** — **check the review answers for a ruling on nested instruction files before writing any.** Distinguish two things a ruling may mean: a *generated stub* is derived from the same source as `AGENTS.md` and cannot contradict it; a *hand-authored package instruction file* can, and is what fragments a rule set. A repo may ban the second while allowing the first — do not read a ban on one as a ban on both. If generated stubs ARE banned, put the full index in `AGENTS.md`, create no nested file, and say plainly in the summary that the primary anti-distraction lever is unavailable. Never reintroduce stubs merely because they would be more efficient; the ruling was made knowing the cost.

   Where they ARE allowed:

   Where they ARE allowed: in the 3–6 directories where domain rails concentrate (e.g. `src/api/`, `db/migrations/`, `src/ui/`). Each ≤6 lines: which `.standards/` file governs here plus the 1–2 `stage:now` rails most violated historically. Merge if files exist. **These are the primary anti-distraction lever** — six lines an agent reads because it opened a file in that directory beats a 150-line index it has to filter itself. Prefer moving a rail into a stub over adding it to AGENTS.md whenever the rail is path-specific.
3. **`.standards/exemptions.yaml`** from the confirmed candidate list: `{path, rails_waived: [ids], owner, expiry, reason}` per entry.
4. **`.standards/INDEX.md`** — one line per domain file: what it covers, when to read it, and its active/deferred rail counts.
5. **`.standards/_backlog.md`** — every remediation and enablement item split out above, each carrying the rail ID it serves, so the work is traceable back to the rule that motivated it. Group by rail and mark which items are prerequisites for a rail being enforceable at all (a rail whose enablement is unbuilt is aspirational, and the summary should say so). This file is never linked from `AGENTS.md`.
6. **`.standards/_deferred.md`** — every `stage:ga` and `stage:scale` rail with its stage and the profile answer that deferred it, plus every `[n/a — profile: …]` prune. This keeps deferral auditable and gives the next stage transition a ready worklist, **without putting any of it in the agent read path**. Nothing links to this file from `AGENTS.md`.
7. **Hook suggestions** — write `.standards/_hooks-proposed.md` listing PreToolUse/PostToolUse hook candidates for machine-enforceable rails (package allowlist, migration naming, glossary new-term detection, contract lint), with the settings snippet for each. Propose only; do not install hooks.
8. **`.standards/_claims/<domain>.json`** — one sidecar per domain file, pinning every rail's evidence to the exact code it rests on. See "Evidence anchors" below.

## Evidence anchors — pin every rail to the code it rests on

A compiled rail set is a set of assertions about this repo, and six months later nobody can tell
which of them are still true. `stale_after` is a wall-clock guess; a `verified` event signs off a
whole domain file, so one moved function invalidates nothing legibly and re-reviewing everything
is the only honest response. Nobody does that, so the rail set quietly decays into folklore.

The sidecars fix that by recording, per rail, a hash of the code its `Evidence:` ranges point at.
Then "which rails no longer describe this repo?" is a computation instead of a re-read. This is
also the precondition for checking compliance at all: a checker that holds a diff against a rail
whose `[observed]` evidence rotted away months ago is enforcing a rule the repo already abandoned.

### Emitting

For every rail carrying at least one file-backed `Evidence:` range, resolve each anchor against
the working tree and write:

```json
{
  "schemaVersion": 1,
  "domain": "data",
  "sourceFile": ".standards/data.md",
  "sourceVersion": "sha256:9f2c…",
  "generated": { "by": "coherence-standards/0.1.0", "model": "<model-id>",
                 "taxonomy_version": "<from PROFILE.yml>", "at": "<ISO 8601>" },
  "commit": "a1b2c3d",
  "rails": [
    {
      "id": "D3.14",
      "statement": "Every tenant-scoped query includes tenant_id",
      "tag": "observed",
      "stage": "now",
      "anchors": [
        {
          "resource": "src/models/scoped.py#L31-L44",
          "algo": "repo-lines-v1",
          "lines": 14,
          "range":  "sha256:7500d011…",
          "first":  "sha256:8d821f47…",
          "last":   "sha256:5a771dc2…",
          "before": "sha256:88bab312…",
          "after":  "sha256:47e87f46…"
        }
      ]
    }
  ]
}
```

- `sourceVersion` hashes the domain file itself, so a later reader can tell *"the code moved under
  these claims"* from *"somebody edited the rails and the sidecar is behind."* Two different
  problems with two different fixes; conflating them is how a sidecar becomes untrusted.
- `commit` is the `git rev-parse --short HEAD` the anchors were resolved against — the answer to
  "changed since when?".
- Hash construction, normalization, and the five statuses are specified once in
  `${CLAUDE_PLUGIN_ROOT}/toolkit/TEMPLATE.md` under "Evidence anchors". Follow it exactly; the
  format is only worth anything if two runs of two different models produce identical hashes for
  identical code.
- **Compute hashes with a tool, never by inspection.** `${CLAUDE_PLUGIN_ROOT}/scripts/anchors.py`
  (stdlib only, like `graph.py`) takes `path#Lm-Ln` anchors and emits the block above:
  `python3 anchors.py emit src/models/scoped.py#L31-L44` . A hash an agent typed from memory is
  not a hash — it will verify `lost` on the first real check and discredit the whole sidecar.

### Rules

- **A rail with no file-backed evidence gets no anchors, and that is not a defect.** A `[gap]`
  rests on an absence, and an `[external]` rail's source of truth is outside the repo — neither
  has anything to pin. Emit them with `"anchors": []` so the rail is still enumerable, and never
  invent a range to make a rail look better-supported than it is.
- **An `[observed]` rail with no anchors is a defect.** It claims the repo does something and
  offers nothing to check that against. Report every one in the summary; do not silently accept it.
- **Sidecars are derived — regenerate, never hand-patch.** If a re-compile would change a hash,
  the code changed, and the right response is to re-resolve the anchor and re-review the rail if it
  came back `changed`. Editing a hash to make a check pass is the same failure as suppressing a
  lint rule, and it destroys the only signal the file carries.
- **Never resolve an anchor against a dirty tree without saying so.** If `git status` is not clean,
  record `"dirty": true` alongside `commit` and flag it in the summary — hashes taken over
  uncommitted work verify `changed` for everyone else the moment they pull.
- **A `moved` anchor is a mechanical fix, not a review event.** Renumber the `Evidence:` range in
  the domain file and re-emit. Do not touch `verified` — the human signed off on a rail, not on a
  line number, and burning a review event on a renumber trains people to ignore them.
- **A `changed`, `lost`, or `missing` anchor never silently re-verifies.** Report it; the rail goes
  back to the reviewer. This is the one place the sidecar is allowed to create work, and it is the
  entire reason it exists.

## Consistency requirements

- Every AGENTS.md rule and CLAUDE.md line cites its rail ID, so prose can be traced to a confirmed rail.
- **Every `[observed]` and `[inferred]` rail resolves to at least one anchor at status `current` or `moved`.** A rail whose every anchor is `changed`, `lost`, or `missing` does not get compiled into `AGENTS.md` on the strength of a prior review — list it as needing re-confirmation instead. Rails with no file-backed evidence (`[gap]`, `[external]`) are exempt from this check by construction, not by exception.
- A rail may live in exactly one tier: if a config enforces it, it appears nowhere as prose except the one "configs are law" line.
- **Graduation is a deletion, not an addition.** When a rail moves from prose to a tool check, the prose goes in the same change that adds the check — never later. If `.standards/` only ever grows, nothing is graduating, and the files drift out of agreement with the tools that actually decide. Report any rail whose `[enforced: …]` tool now covers it fully as a graduation candidate for the next review.
- **Never delete prose for a tool this repo does not run.** Before honouring a "Covered by tooling" entry, confirm the cited config path exists. A rail covered by a scanner that is not configured here is enforced by nothing — carry it forward as a live rail and flag the discrepancy in the summary rather than silently dropping it.
- Every file this pass writes or merges into carries OKF frontmatter per `${CLAUDE_PLUGIN_ROOT}/toolkit/TEMPLATE.md`. On a domain file whose rulings the human signed off, append a `verified` event — `{by: "human:<name>", at: "<ISO 8601>"}` — leaving `generated` untouched. That flip from `verified: []` to a signed event is what distinguishes a confirmed rail set from a draft one.
- When merging into an existing `AGENTS.md` or `CLAUDE.md` that already has frontmatter, merge keys rather than replacing the block; never clobber an existing `generated` or `verified` history.
- A `stage:now` rail that appears in a path-scoped stub does not also belong in AGENTS.md unless it is genuinely universal. Duplication across tiers is how a 150-line index becomes a 400-line one nobody reads.
- **Re-compile on profile change.** Record `profile_version` and `answered_at` in the frontmatter of every generated artifact. If `PROFILE.yml` is newer than the artifacts, say so and re-derive rather than patching — a stage promotion (`pre-ga` → `ga`) is exactly the moment a deferred rail must reappear, and an incremental patch will miss it.
- Finish with a summary: rails confirmed per domain split by stage, the ten selected always-on rules and why, what the profile pruned and deferred, which proposed hooks would retire which rails from prose, every `[external]` rail still unconfirmed, and the anchor tally — how many rails are anchored, how many resolved `current` / `moved` / `changed` / `lost` / `missing`, and how many `[observed]` rails carry no anchor at all. State the compiled context cost — roughly how many lines a coding agent now reads before touching a file — since keeping that number small is the point of the whole filter.
