# coherence-standards

Mine a repository for the engineering standards it already follows, surface the decisions it has never made, and compile the confirmed rules into a form agents actually read.

Three commands, run in order. Each is resumable and never destroys a prior run.

```
/extract-standards    repo → 300-400 tagged rails + a review packet
/review-standards     ~40 decisions with a human (not 200)
/compile-standards    confirmed rails → AGENTS.md, exemptions, backlog
```

## What it produces

```
AGENTS.md                     the ten always-on rules, a router table, and
                              what is deliberately out of scope
.standards/
  PROFILE.yml                 8 human answers that stage and prune the taxonomy
  <domain>.md            ×16  every rail, tagged and staged, with evidence
  REVIEW.md                   the decisions a human owes, collapsed into themes
  exemptions.yaml             where a rail knowingly does not apply
  _backlog.md                 remediation and enablement — never in agent context
  _deferred.md                rails that wait for the next stage
  _inventory/                 the raw evidence every rail was drawn from
  _runs/                      prior runs, archived not deleted
```

## The ideas that make it work

**A rail is an obligation, not an observation or a task.** "Every list endpoint returns a bounded page" is a rail. "Nothing paginates" is a finding. "Add pagination" is backlog. The three get separated at compile time, and only the first reaches a working agent.

**Four tags, and two of them are commonly confused.** `[observed]` and `[inferred]` describe what the repo does. `[gap]` means nobody decided. `[external]` means somebody decided somewhere a file read cannot see — a cloud console, an IdP tenant, a VCS host setting. Scoring an externally-configured standard as a gap manufactures busywork; scoring an undecided one as external hides a real hole.

**A profile stages the taxonomy instead of pruning it.** Eight questions — product stage, compliance regime, API consumers, who operates it — decide which rails bind *now* versus at GA. Staging preserves the finding and changes only its urgency; pruning is rare and always annotated with the answer that caused it.

**The review collapses.** 350 rails do not mean 350 decisions. Themes cluster the gaps ("which static-analysis tools do we adopt?" settles seven at once), one default ruling covers the inferred rails, and deferred items are never asked about. Target: under 40 interactions. A packet that produces 200 questions does not get finished, and an unreviewed packet is worth nothing.

**Configs are ground truth — but only the ones this repo runs.** A universal rule belongs in a linter, not in prose an agent reads on every task. But deleting the prose when no tool here enforces it leaves the rule enforced by nothing. `SCANNER-COVERAGE.md` carries the dispositions; the commands require a config path before honouring any of them.

## The taxonomy

**312 rails across 23 domains** — the master list every extraction is scored against, in `toolkit/TAXONOMY.md`. It is deliberately over-complete: cutting a rail during review is cheap, discovering a missing one at the gate is not.

Each domain carries an *agent extraction sources* note naming where the rails are mined from — schema dumps and migration history for §3, lint configs and recently-touched files for §6, incident postmortems for §7, past audit reports for §16.

| # | Domain | Rails | |
|---|---|---:|---|
| 1 | Specification & Requirements | 17 | How intent is written down so agents build the right thing and gates can judge it |
| 2 | Domain Model & Ubiquitous Language | 12 | Stops the highest-frequency incoherence agents produce: inventing vocabulary |
| 3 | Data & Persistence | 23 | Schema naming, ID formats, migration safety, retention |
| 4 | Interface Contracts — Synchronous APIs | 24 | Resource naming, verb semantics, pagination, versioning, error shapes |
| 5 | Events & Asynchronous Messaging | 13 | Topic naming, event schemas, delivery semantics, DLQ policy |
| 6 | Code Structure & Style | 21 | Formatter and linter as ground truth, module boundaries, import rules |
| 7 | Application Runtime Patterns | 18 | Validation at boundaries, transaction scope, resilience, background work |
| 8 | Architecture & Technology Decisions | 14 | Approved stack, ADR format, what triggers a decision record |
| 9 | Security | 16 | AuthN/AuthZ, token handling, secrets, policy-as-code |
| 10 | Privacy & Compliance | 10 | Data classification, lawful basis, purpose limitation, deletion |
| 11 | Observability & Operations | 11 | Log schema, trace propagation, metric naming, alert ownership |
| 12 | Frontend Engineering | 17 | Framework conventions, state management, data fetching, bundles |
| 13 | UX Interaction Patterns | 17 | How the product behaves — the layer agents most confidently get wrong |
| 14 | Visual Design System | 10 | Tokens only, component library versions, new-component flow |
| 15 | Content & Communication | 12 | Voice, capitalization, UI terminology mirroring the glossary |
| 16 | Accessibility | 11 | WCAG floor, semantic HTML, focus management |
| 17 | Analytics & Experimentation | 8 | Event taxonomy, property naming, in-repo tracking plan |
| 18 | Testing & Quality | 12 | Pyramid expectations per change class, fixtures, flake policy |
| 19 | Dependencies & Supply Chain | 9 | Allowlists, licenses, pinning, lockfile discipline |
| 20 | Version Control & Change Management | 9 | Branch and commit conventions, PR size, ownership |
| 21 | Build, Deploy & Environments | 10 | Reproducible builds, golden images, IaC, rollback |
| 22 | Embedded AI Features | 9 | Applies when the product itself ships LLM functionality |
| 23 | Brownfield Meta-Rules | 9 | What an agent does when rails conflict, are missing, or are knowingly unmet |

§23 is the one to read first on an existing codebase — precedence order, the neighborhood rule, and the exemption registry fire in the first hour.

## Contents

| Path | |
|---|---|
| `commands/` | the three slash commands |
| `toolkit/TAXONOMY.md` | 312 standards across 23 domains — the master list |
| `toolkit/TEMPLATE.md` | the rail format and the rules drafters follow |
| `toolkit/SCANNER-COVERAGE.md` | which rails a code-health tool should own instead |
| `scripts/graph.py`, `scripts/graph.mjs` | stdlib-only import-graph analysis (cycles, chokepoints, orphans, test pairing) |

The taxonomy ships **with the plugin**, not copied into each repo — repos pin `taxonomy_version` in their `PROFILE.yml` so an extraction stays legible after the taxonomy moves on.

## Notes from the first real run

- The graph scripts encode repo conventions deliberately. A generic analyzer reports the test layout as missing tests and `__init__.py` as dead code. Read the exclusions before trusting a number — the first run of `graph.py` reported 59 orphans because `from pkg import submodule` was resolved to the package; the real answer was 30.
- Probes are read-only and never authenticate. An honest "probe unavailable — expired credentials" beats a guess, and the failure itself is a finding.
- `**Proposed:**` is never an answer. `/compile-standards` refuses to compile a rail whose only support is a draft.

## Status

`0.1.0` — validated end to end on one repository (352 rails, 39 decisions, seven compiled artifacts). Org-vs-repo rail inheritance is deliberately not built; that needs a second repo to design against.
