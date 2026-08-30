---
date: 2026-08-29
topic: standards-compliance-checking
---

# Standards Compliance Checking

## Problem Frame

`coherence-standards` extracts, reviews, and compiles a repo's engineering rails into `AGENTS.md`, path-scoped `CLAUDE.md` stubs, and `.standards/` domain files. Everything downstream of compile is advisory: rails reach an agent as context, and nothing checks whether the work an agent produced actually honours them.

The taxonomy already specifies the missing half. §1.12 defines a deviation declaration block, §23.5 says an agent facing an uncovered situation flags it rather than choosing silently and the answer becomes a new rail, §23.6 says undeclared deviation is a rejection, and §23.8 has agents cite the rail version they built against. None of it is implemented — the plugin ships `commands/`, `scripts/`, and `toolkit/` only, with no enforcement surface of any kind. `/compile-standards` writes `.standards/_hooks-proposed.md` and explicitly stops at "Propose only; do not install hooks."

The gap matters most because compliance is currently unmeasured. No repo has run extract → review → compile and then had agents build under the compiled rails, so which rails get followed, which get quietly broken, and which are dead letters is unknown. A checker that only blocks bad work would not answer that either. What is needed is a mechanism that surfaces conflicts *and* routes each one to a decision that writes back into the rail set.

---

## Actors

- A1. Producing agent: writes the spec or the code. Has the rails in context; makes the choices under review.
- A2. Checking agent: a separate invocation that reads a finished artifact and reports rail conflicts. Did not make the choices, so does not rationalise them.
- A3. Developer: the only actor permitted to weaken a rail. Dispositions accumulated declarations.

---

## Key Flows

- F1. Spec compliance
  - **Trigger:** A spec is drafted or revised.
  - **Actors:** A1, A2
  - **Steps:** A2 reads the spec, loads the domain files the router points at, reports conflicts. A1 either amends the spec to comply or records each remaining conflict in the spec's §1.12 deviation block.
  - **Outcome:** The spec is compliant, or carries an explicit list of what it knowingly breaks.
  - **Covered by:** R1, R2, R4, R5

- F2. Code review
  - **Trigger:** A diff or PR is ready for review.
  - **Actors:** A2, A3
  - **Steps:** A2 reads the diff — plus the spec if one exists — and reports conflicts, specifically including changes that were never declared. A3 dispositions each finding: comply, accept an exception, change the rail, or reject.
  - **Outcome:** Every conflict has a recorded disposition; exceptions and rail changes are written back into `.standards/`.
  - **Covered by:** R1, R2, R6, R7, R8

- F3. Coding time
  - **Trigger:** An agent is mid-task, editing files.
  - **Actors:** A1
  - **Steps:** A1 consults the rails already in its context. If it recognises a conflict it cannot resolve by complying, it appends to the running declaration and continues rather than blocking.
  - **Outcome:** Conflicts noticed during work survive to review instead of being forgotten.
  - **Covered by:** R3, R5, R11

---

## Requirements

**The check command**

- R1. A single command checks an artifact against the compiled rails. The three moments are three invocations of it, not three implementations.
- R2. The artifact under review supplies its own scope. Checking a spec, the spec is the scope; checking code, the diff is the scope, plus the spec if one exists. There is no separate rail-scoping mechanism, and the command works on unspecced work.
- R3. The command runs as a fresh agent invocation, separate from the agent that produced the artifact.
- R4. Findings cite the rail ID they rest on, so every finding is traceable to a confirmed rail.
- R12. When no rail covers a situation the artifact raises, the command reports it as an uncovered gap rather than inventing a ruling (§23.5).

**Resolution**

- R5. A producing agent has exactly two moves on a finding: comply (fix the artifact) or declare (record the conflict and continue). Both are autonomous and neither blocks on a human.
- R6. Only a human may pick a disposition that weakens a rail — accepting an exception or changing the rail. An agent may propose either; it may never apply one.
- R7. A human dispositions each declaration exactly once, at review, choosing comply, exception, rail change, or reject.
- R8. Exceptions write to `.standards/exemptions.yaml` with owner and expiry (§23.3); rail changes write to the rail and the standards changelog (§23.8). This write-back is what makes the rail set self-correcting, and is the reason the feature exists rather than a side effect.
- R14. Every exception written to `exemptions.yaml` carries a mandatory expiry, defaulted when the human does not set one. An exception with no expiry is a permanent rail deletion in disguise, and is the slowest form of the corrosion R6 exists to prevent.
- R9. Declarations persist in one file per branch under `.standards/declarations/`, committed alongside the change and deleted once dispositioned. Committing it puts the declaration in the diff, so a reviewer sees it next to the code it excuses, and a non-empty file is itself the pending-decision signal. Requires no spec and no open PR, so it holds for local and unspecced work.

**Invocation guidance**

- R10. `/compile-standards` writes guidance into the `AGENTS.md` it generates telling agents when to run the check — before finishing a spec, before opening a PR, and when a conflict is noticed mid-task.
- R11. That guidance is understood to be advisory. It raises the odds an agent checks its own work; it does not guarantee it. Any deterministic trigger is a hook or branch protection, which this feature proposes but does not install, consistent with the existing posture on `_hooks-proposed.md`.

**Naming and fit**

- R13. The command is `/check-compliance`. It disambiguates by changing the object rather than the verb: every `<verb>-standards` name collides with `/review-standards`, because only the verb would carry the distinction.

---

## Acceptance Examples

- AE1. **Covers R2, R3.** Given a repo with compiled rails and an uncommitted diff touching `db/migrations/` and no spec, when the check runs, it reports conflicts scoped to the migration and persistence rails without any spec being present.
- AE2. **Covers R6, R7.** Given a finding that a query is not tenant-scoped, when the producing agent runs the check, it may fix the query or declare the conflict — it may not add the module to `exemptions.yaml`. That entry appears only after a human dispositions the declaration.
- AE3. **Covers R8.** Given a human dispositions a declaration as "change the rail," when the disposition is applied, the rail text and the standards changelog both update, and the next check run evaluates against the new text.
- AE4. **Covers R1.** Given the same command is pointed at a spec file and then at a PR, both runs produce findings in the same shape with the same resolution vocabulary.

---

## Success Criteria

- After a month of use on one repo, the declaration record answers a question nobody can answer today: which rails are cited, which are repeatedly deviated from, and which never appear at all. Rails in the third category are candidates for deletion; rails in the second are mis-staged or wrong.
- A developer facing a finding always has a move that is not "ignore it" — comply, declare, except, or change the rail — and picking one takes less effort than working around it.
- Exceptions and rail changes made during review are visible in `.standards/` afterward, so the rail set reflects decisions actually made rather than only decisions made at compile time.
- A planner reading this document does not need to invent the resolution vocabulary, who may weaken a rail, or how scope is determined.

---

## Scope Boundaries

- Installing hooks. The feature may propose deterministic triggers; installing them stays the user's decision, matching the existing `_hooks-proposed.md` posture.
- Blocking a merge. Whether a finding stops a merge is branch protection, configured outside the plugin.
- Replacing scanners. Universal rules stay in the scanner ruleset per `SCANNER-COVERAGE.md`; this checks the house-specific rails prose still carries.
- Classifying rails by detectability. Considered and dropped — the artifact-scopes-itself model removes the need for it.
- Per-moment authority tiers. Considered and dropped in favour of one rule: only humans weaken.
- Auto-remediation of existing violations. The check reports on the artifact in front of it, not the repo's backlog, which `_backlog.md` already owns.

---

## Key Decisions

- The artifact under review is the scope: it removes an entire scoping subsystem, and works whether or not a spec exists.
- Only humans may weaken a rail: reduces the agent's menu to comply-or-declare, and prevents an agent from editing a rail until its own work passes — the corrosion risk that would otherwise turn a self-correcting loop into an eroding one.
- Humans disposition once, at review, over accumulated declarations: the agent is never blocked waiting, and the same conflict is never adjudicated twice.
- The checking agent is a separate invocation from the producing agent: a fresh context is what catches unwitting violation, which self-report structurally cannot.
- One command, three invocation points: the three moments differ in when it runs, not in what it does.
- Declarations live with the change, exceptions live in the repo: they have opposite lifecycles. A declaration is an undisposed decision that dies at review; an exception is a disposed one that persists until its expiry. Sharing a home would blur the two.
- `/check-compliance` over `/check-standards`: the object of the verb is what disambiguates. Follows conftest, which splits `verify` (test the policies themselves) from `test` (validate real files against them).
- Mandatory expiry on exceptions: convergent practice across security tooling — Snyk requires reason plus expiry with a 90-day maximum, tfsec supports `exp:yyyy-mm-dd` and advises always setting it. Cheap to adopt, since `exemptions.yaml` already carries the field.

---

## Dependencies / Assumptions

- Requires a repo that has completed extract → review → compile, so `.standards/` and `AGENTS.md` exist. Verified absent in `growth-beaker-agents` itself, which does not currently dogfood the plugin.
- Assumes the router table in a compiled `AGENTS.md` is good enough to select relevant domain files for a given artifact. Untested — no compiled `AGENTS.md` was available to inspect.
- Assumes an agent reading a diff plus a scoped set of domain files produces findings of useful precision. Unvalidated, and the main technical risk: too noisy and the check gets ignored, too quiet and it provides false assurance.

---

## Outstanding Questions

### Deferred to Planning

- [Affects R3][Technical] Does the checking agent ship as a plugin subagent, a skill, or a command that spawns one?
- [Affects R7][Technical] How does a human disposition declarations in practice — interactive prompt, editing a file, or PR comments?
- [Affects R8][Needs research] How does a rail change mid-PR interact with `/compile-standards`, whose preflight is merge-only and forbids shortening a `verified:` history?
- [Affects R9][Technical] How does the per-branch declaration file behave across rebase, squash merge, and stacked PRs?
- [Affects R1, R2][Needs research] How noisy is an agent checking a real diff against real domain files? Needs a live trial before the shape is fixed.

---

## Next Steps

-> /ce-plan for structured implementation planning
