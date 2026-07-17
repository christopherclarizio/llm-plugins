# clarizio-documentation — roadmap & backlog

What exists, what's deliberately deferred, and the skills we've designed but not yet built.
This file is the durable record so the plan survives across sessions and people.

> This plugin repo is **public**. Keep this file free of proprietary architecture detail.
> The documentation *corpus* it operates on lives in a **separate private repo** and is
> the only place source-derived internals belong.

## Guiding principle

**Demand-driven.** Build machinery when a real task needs it, not speculatively. The same
discipline we apply to docs applies to the tooling: don't gold-plate a skill suite around a
handful of documents. The pilot needs only the read loop plus, eventually, capture + verify.

## Status

- **Read loop — shipped.** `docs-router` skill + `check_staleness.py` (drift detection),
  the shared frontmatter schema, the staleness/trust convention, and the two body templates.
- **First corpus slice — written** (kept in the private docs repo), `trust: agent-generated`,
  anchored to source and verified fresh.
- **Write loop — not built.** Deferred until there's enough corpus to justify it.

## Skills backlog

### Read loop
- `docs-router` — **shipped**. Selects docs by frontmatter, follows the hierarchy only as
  deep as needed, checks freshness, briefs with trust + staleness citations.
- *(future)* generated `INDEX` + an index-builder skill — only once globbing frontmatter at
  read time gets expensive. Not needed at pilot scale (deliberately no index today).

### Write loop (designed, not yet built)
1. **capture / graduate** *(highest priority of this loop)* — after a session that did real
   re-derivation, offer to persist it as a doc. Design constraints we've locked:
   - *Selective.* Offer only when non-trivial understanding was gained or a wrong assumption
     was corrected — most sessions produce nothing durable. Nagging after every task gets it
     disabled.
   - *Prepared diff, not an open prompt.* Present a concrete doc/change for yes/no.
   - Auto-fill `sources` + `verified_at`; enforce the altitude rule (no code-restating trivia)
     and the "state what it does NOT cover" rule; dedup against existing docs.
   - *Trigger signal:* `docs-router` **misses** (task not covered by the corpus) are prime
     capture candidates. The read loop feeds the write loop.
2. **verify / ground** — given a doc, re-derive its claims from current source; report
   agreements/contradictions; bump `verified_at` or flag drift. This is the deep counterpart
   to `check_staleness` (which only cheaply detects that anchors moved), and it's the workflow
   that promotes a doc from `agent-generated` → `human-reviewed`.
3. **style-as-validation** — a doc *linter* + the templates, NOT a prose style guide (agents
   drift from prose, not from a check). Validates: required frontmatter present & well-formed,
   `sources`/`verified_at` present, `tier` vocabulary matches `tree`, links resolve, altitude
   heuristics. Runnable on demand or in CI.
4. **eval harness** — run a representative task *with* vs. *without* the corpus and capture the
   comparison (wrong turns, correctness, tokens). This is what turns "it feels better" into
   evidence. May be a one-off harness rather than a durable skill.

### Learning / mentorship (the tutorial quadrant)
5. **learning / onboarding** — a skill built *on top of* the corpus: guided walk-throughs and
   comprehension checks for a subsystem, for onboarding engineers and agents. Depends on a
   reasonable corpus existing first. Also the safest framing for the whole initiative — scaling
   mentorship rather than replacing anyone's expertise.

## Corpus backlog

- A **product-tree counterpart** for the first slice, to exercise the code↔product bridge on
  real content.
- Additional subsystems **as demand surfaces** — do not pre-build.
- A **human-review pass** to promote the first slice from `agent-generated` → `human-reviewed`.

## Decisions recorded

- Two trees (`code`, `product`); **shared frontmatter, different bodies**.
- **Frontmatter is the router's contract** — a field exists only if a consumer reads it.
- **Per-doc anchors** (not per-claim) for v1.
- **No generated index** at pilot scale.
- **Relative-path links in prose; `id` as the router's key.**
- **Keep `tier`** — altitude label distinct from `parent`/`children` topology.
- **No "howtos" tree.** Howtos are the *doing* half; these trees are the *understanding* half,
  which is the thing nothing else provides and the wedge for the whole effort. Executable
  procedures belong in **skills** (the active form of a how-to, already an accepted pattern);
  human-process procedures belong in the monorepo's existing procedural docs. Both also don't
  fit the source-anchored staleness contract cleanly. Docs **cross-link** to the relevant
  skill/howto via `related` rather than absorbing them. The decision rule:
  | Need | Home |
  |---|---|
  | Understand what/why | docs (these trees) |
  | Do a task, agent-triggered | a skill |
  | Do a task, human process | existing monorepo procedural docs |
  | Guided learning | a skill (the learning/onboarding one above) |

  Revisit only if demand proves a gap none of those fill.

## Open questions

- Vend mechanism into the target monorepo (user-level config pointer vs. other) — TBD.
- Scale threshold at which the generated index becomes worth it.
- Who owns the human-review pass that promotes docs to `human-reviewed`.
