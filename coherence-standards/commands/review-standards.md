# Review the standards packet interactively

Walk the human through `.standards/REVIEW.md` and write their answers back, instead of making them edit hundreds of slots by hand. Optional argument: a phase or domain filter (e.g. `themes`, `external`, `now`, `api`) to review one slice: $ARGUMENTS

`REVIEW.md` stays the source of truth. Hand-editing and this command interoperate freely — this one only fills slots that are still blank.

## The constraint that shapes everything

**A rail-by-rail interrogation is a failed review.** Even a small repo yields 200+ rails, and nobody works through 200 questions — an unreviewed packet is worth nothing, so a design that produces one is worse than a shorter one that gets finished. Rails are not independent decisions; they cluster. Your job is to ask the **smallest set of questions whose answers determine the rest**, and to make the remainder a skim rather than an interrogation.

Target **under ~40 interactions** for a full pass. If the packet forces more, say so plainly and offer to review by theme only — do not grind through it.

## Ground rules

- **Write inside `.standards/` only.** Never touch source, configs, or the toolkit.
- **Never invent an answer.** Every question offers a way to defer. An unanswered item is honest; a fabricated one silently becomes a rail.
- **A `**Proposed:** ` line is not an answer.** It is a draft for the human to accept or override. Only an explicit acceptance moves it into `**Answer:** `, and the answer records that it came from a proposal.
- **Never overwrite an existing answer**, and never re-ask an answered question — including across sessions. Resumability is what makes a large packet tractable.
- **Do not resolve a gap the human declines.** Leave it blank and move on.

## Preflight

Read `REVIEW.md`. If absent, stop and point at `/extract-standards`.

Classify every `**Answer:** ` slot as answered or open, then report the shape **as interactions, not as rails**: how many theme questions, prune groups, breakout rulings, proposals to skim, and individual questions remain. "213 open items" is a discouraging and misleading number when 8 questions resolve 65 of them. If everything is answered, say so and point at `/compile-standards`.

## Phase order

Announce each phase with its interaction count. Offer an exit after every phase — a tired reviewer produces worse rulings than a blank slot, and a blank slot is recoverable.

1. **Themes** (section 2, ~6–12 questions). Highest leverage: each cascades to a list of rails. Do these first — later phases shrink as a result, and skipping ahead wastes the reviewer's attention on questions a theme would have settled.
2. **Prunes** (section 0, ~4–6 questions, grouped by profile key). Highest regret if wrong: a prune removes a question permanently.
3. **External** (section 5, 1 question). Offer bulk confirmation — these report what a probe already read. Name the subset that a re-probe would clear so the human can skip them entirely.
4. **Proposals digest** (section 3). Group by domain and ask one question per group: accept all, or name the ones to override. Only overrides become individual questions. See "Asking about a proposal" below — this is the phase where an under-specified question does the most damage, because the human is being asked to ratify a position rather than form one.
5. **Inferred** (section 4). Confirm the blanket default in one question, then ask only the breakout items.
6. **Precedence and exemptions** (sections 6–7, ~2 questions).
7. **Deferred** — never asked. Mention the count once, as the next-stage worklist.

## Asking

`AskUserQuestion`, at most 4 per call, grouped so context carries.

- **Options come from the document, never from you.** Where an entry lists `Options: (a)/(b)/(c)`, use them verbatim. Where it says `Options: open`, offer the natural shape of the decision. Never manufacture a third position for balance.
- **Recommended-first only where the document argued for one.** The packet was written not to lead the answer; asking it aloud must not either. A `**Proposed:** ` line does count as the document arguing — put it first and say it is the proposal.
- `header` is the rail or theme id (`T3`, `D4.6b`) so the human can find it in the file.
- **Carry the evidence into the question**: the `Found:` line, exception paths, measured counts. A ruling made without the evidence is worse than a blank slot.
- For a theme, **name what it resolves** — "this settles 14 rails including D6.1, D9.11, D19.5a". The reviewer needs to feel the leverage to answer confidently.
- Add an explicit **"Skip for now"** whenever the honest answer may be "I need to check" — anything touching compliance, licensing, cost, or another person's decision.

### Explaining consequences — assume the reviewer did not write the code

The person answering is often not the person who wrote the codebase, and is sometimes not an engineer at all. They may be a founder, a lead who has been away from the code for months, or someone inheriting the repo. **A question they cannot evaluate produces an answer that looks like a decision and is not one.**

Every question must be answerable by someone who has never opened the file it concerns:

- **Say what the thing IS before asking about it.** `getByRole` and `data-testid` mean nothing to a reader who has not written Playwright tests. Show the two lines of code and say what each does in words: *"find the button labelled Approve"* versus *"find the element tagged approve-btn"*.
- **Never assume a path, module, or symbol is familiar.** `services/notify.py::_dispatch_to` is not a shared reference. Say what it does — *"the one place outbound email is built"* — and then cite the path.
- **State the day-to-day consequence.** What will someone actually do differently tomorrow? "Renaming a button breaks tests" beats "increases coupling to accessible names." Concrete beats correct-but-abstract.
- **Name the second-order effect** where one exists: what this makes harder later, and what it makes possible. If a choice removes the only thing enforcing an earlier answer, say so in the question — not afterwards.
- **Say how reversible it is.** Deciding a naming convention is cheap to revisit. Renaming a published enum, deleting a rail, or committing to a licence is not. Reversibility changes how much care an answer deserves, and the reviewer cannot infer it.
- **Define any unavoidable jargon inline**, in the question, not by reference. If a term needs a glossary the question is too dense.
- **Prefer a worked example over a definition.** One real line from this repo, and what changes about it, is worth a paragraph of description.

If a question cannot be made answerable this way — because it genuinely requires knowing the codebase — say so plainly and offer to defer it rather than extracting an uninformed answer. An unanswered item is honest; an answer given without understanding is worse than a blank, because it looks settled.

### Asking about a proposal

**Assume the human has not read `REVIEW.md`.** They are being asked to ratify a position someone else drafted, which is only possible if the question carries everything the document would have given them. A proposal summarised without its alternatives reads as a fait accompli, and "accept" then means "I have no basis to object" rather than "I agree."

Every proposal question includes, in this order:

1. **What the repo does today** — the `Found:` line, with paths and measured counts. Without it there is nothing to judge the proposal against.
2. **The decision being made**, in one line.
3. **The alternatives that were on the table** — reproduce the entry's `Options:` verbatim, including the ones the proposal rejected. Presenting only the proposed option is the single worst failure mode of this phase: it converts a choice into an announcement.
4. **The proposal and the specific reason it was drafted** — the evidence, not a preference.
5. **What accepting changes, and what overriding would mean instead.**

Make the override options **name the alternative**, not the rail. "Override D2.1" tells the human nothing; "Hand-write the glossary instead of generating it" tells them what they are choosing.

**Prefer two well-explained proposals per question over four compressed ones.** More batches is the correct trade — a fast "accept" made without the alternatives in view is worth less than a slower answer, and it is worth less precisely because it looks like agreement. If a group cannot be explained inside a readable question, split it.

## Writing back

**After every batch, not at the end**, so a dropped connection costs one batch.

- Fill the matching slot in place: `**Answer:** <the human's words>`.
- **Cascade a theme answer** to every rail it resolves, writing `**Answer:** <text> (via theme T3)` so the provenance is visible and a later reader can see it was not answered individually.
- Where the human accepted a proposal: `**Answer:** <proposal text> (accepted proposal)`.
- Write the option's text, never its letter — `(b)` is meaningless once options are edited.
- Keep any reasoning the human volunteers. The *why* is what makes a rail defensible later, and it is the part `/compile-standards` cannot reconstruct.
- Preserve everything else byte-for-byte: never reflow, re-order, or re-number.
- Confirm the count after each write (`theme T3 answered — cascaded to 14 rails`).

## Ending

Report: interactions completed this session, rails resolved (including cascades), what remains by phase, and whether `/compile-standards` can run. It can run once the `stage:now` gaps are answered; deferred gaps and unconfirmed external items do not block it.
