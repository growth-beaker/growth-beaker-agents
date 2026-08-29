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

## Contents

| Path | |
|---|---|
| `commands/` | the three slash commands |
| `toolkit/TAXONOMY.md` | ~240 standards across 23 domains — the master list |
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
