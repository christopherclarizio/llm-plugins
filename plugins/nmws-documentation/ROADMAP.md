# nmws-documentation — roadmap & backlog

What exists, what's deliberately deferred, and the skills we've designed but not yet built.
This file is the durable record so the plan survives across sessions and people.

> This plugin repo is **public**. Keep this file free of proprietary architecture detail.
> The documentation *corpus* it operates on lives in a **separate private repo** and is
> the only place source-derived internals belong.

## Guiding principle

**Demand-driven.** Build machinery when a real task needs it, not speculatively. The same
discipline we apply to docs applies to the tooling: don't gold-plate a skill suite around a
handful of documents. The write loop uses agent workflows and a small offline validator,
not an autonomous publishing system.

## Status

- **Read loop — shipped.** `docs-router`, batched per-repository drift detection,
  safe fetch/fast-forward refresh of configured local checkouts, the repository
  registry, shared frontmatter schema, staleness/trust convention, and body templates.
- **First corpus slice — written** (kept in the private docs repo), `trust: agent-generated`,
  referenced to source and verified fresh.
- **Write loop — shipped.** `docs-capture`, `docs-verify`, `docs-validate`, and an
  on-demand `docs-evaluate` pilot workflow. Capture/verification prepare concrete diffs
  for approval; human trust promotion remains explicit. Real private-corpus adoption,
  human-review ownership, and measured evaluation results are still outstanding.

## Skills backlog

### Read loop
- `docs-router` — **shipped**. Selects docs by frontmatter, follows the hierarchy only as
  deep as needed, checks freshness, briefs with trust + staleness citations.
- *(future)* generated `INDEX` + an index-builder skill — only once globbing frontmatter at
  read time gets expensive. Not needed at pilot scale (deliberately no index today).

### Write loop
1. **capture / graduate — shipped** (`docs-capture`) — after a session that did real
   re-derivation, offer to persist it as a doc. Design constraints we've locked:
   - *Selective.* Offer only when non-trivial understanding was gained or a wrong assumption
     was corrected — most sessions produce nothing durable. Nagging after every task gets it
     disabled.
   - *Prepared diff, not an open prompt.* Present a concrete doc/change for yes/no.
   - Auto-fill `code_references` + per-repository `verified_at`; enforce the altitude rule (no code-restating trivia)
     and the "state what it does NOT cover" rule; dedup against existing docs.
   - *Trigger signal:* `docs-router` **misses** (task not covered by the corpus) are prime
     capture candidates. The read loop feeds the write loop.
2. **verify / ground — shipped** (`docs-verify`) — given a doc, re-derive its claims from current source; report
   agreements/contradictions; bump `verified_at` or flag drift. This is the deep counterpart
   to `check_staleness` (which only cheaply detects referenced-code changes), and it's the workflow
   that prepares a doc for explicit human acceptance before promotion from
   `agent-generated` → `human-reviewed`. Agent grounding alone never promotes trust.
3. **style-as-validation — shipped** (`docs-validate`, `validate_docs.py`) — a doc *linter* + the templates, NOT a prose style guide (agents
   drift from prose, not from a check). Validates: required frontmatter present & well-formed,
   `code_references`/per-repository `verified_at` present, `tier` vocabulary matches `tree`, links resolve, altitude
   heuristics. Runnable on demand or in CI.
4. **eval pilot workflow — shipped; real measurements pending** (`docs-evaluate`) — run a representative task *with* vs. *without* the corpus and capture the
   comparison (wrong turns, correctness, tokens). This is what turns "it feels better" into
   evidence. Uses independent contexts and private JSON results rather than a permanent
   benchmark platform; unavailable runtime counters are reported, not estimated.

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
- **Per-document code references** (not per-claim), with independent verification
  commits for every referenced repository.
- **Explicit local checkouts.** Registry entries provide `remote`,
  `authoritative_branch`, and `local`; local overrides may change only the path.
- **Refresh on demand.** Fetch and fast-forward clean authoritative-branch checkouts
  once per document batch. No branch switches, destructive repairs, remote API layer,
  or checkout discovery. Refresh failures never imply freshness.
- **No saved lookup snapshot.** Updated SHAs remain in process/tool output only;
  refreshing code never updates document verification metadata.
- **No generated index** at pilot scale.
- **Relative-path links in prose; `id` as the router's key.**
- **Keep `tier`** — altitude label distinct from `parent`/`children` topology.
- **Approval-gated writes.** Validate the concrete proposal before approval; recheck
  source/target stability before applying. No automatic commits or trust promotion.
- **Current reference format only.** No top-level `sources`/`verified_at` or local-only
  checker mode. Bundled examples use the same contract as the private corpus.
- **No "howtos" tree.** Howtos are the *doing* half; these trees are the *understanding* half,
  which is the thing nothing else provides and the wedge for the whole effort. Executable
  procedures belong in **skills** (the active form of a how-to, already an accepted pattern);
  human-process procedures belong in the monorepo's existing procedural docs. Both also don't
  fit the code-reference staleness contract cleanly. Docs **cross-link** to the relevant
  skill/howto using relative-path prose links rather than absorbing them; `related`
  remains a list of corpus document IDs. The decision rule:
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
