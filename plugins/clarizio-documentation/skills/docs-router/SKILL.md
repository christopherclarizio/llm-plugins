---
name: docs-router
description: Assembles the relevant architecture and product documentation for a task before reading code. Use at the START of any task that needs understanding of how a subsystem works or how a product feature behaves — bug fixes, feature work, refactors, investigations. Globs the doc corpus, selects by relevance, follows the hierarchy only as deep as needed, checks each loaded doc for staleness, and briefs with citations. Skip for trivial or purely mechanical edits.
---

# docs-router

Read-loop entry point for the `clarizio-documentation` corpus. It turns "understand this
area before touching it" from ad-hoc code spelunking into a cheap, consistent lookup — and
refuses to hand over a claim without flagging how much to trust it.

## When to use

At the **start** of a task that needs understanding of a subsystem or a product feature,
before diving into code. Skip it for trivial or purely mechanical work (a rename, a
formatting pass, a one-line fix in code you already understand).

## Corpus location

Resolve the docs corpus root in this order:

1. `$CLARIZIO_DOCS_ROOT`, if set.
2. Otherwise `${CLAUDE_PLUGIN_ROOT}/examples` (bundled demo docs).

## Procedure

1. **Index cheaply.** Glob `**/*.md` under the corpus root and read **only** the
   frontmatter of each (the block between the first pair of `---`). Do not read bodies yet.
2. **Select.** Rank docs against the task using `description`, `keywords`, `tree`, and
   `tier`. Prefer the coarsest matching `tier` first (`architecture`/`overview`), then drill.
3. **Progressive disclosure.** Read the body of the top match. Follow its `children` and
   `related` links **only as far as the task needs**, and stop once you have enough. Never
   load the whole tree.
4. **Check freshness.** For every doc whose body you load, run:
   ```sh
   python "${CLAUDE_PLUGIN_ROOT}/skills/docs-router/scripts/check_staleness.py" <doc-path> --repo <code-repo-root>
   ```
   Exit `0` = fresh, `1` = stale, `2` = error. Treat a stale result — or `trust: draft` /
   `agent-generated` — as "lead, not authority."
5. **Brief with citations.** Return a compact synthesis, then a citation list: for each doc
   used — `id`, `tier`, `trust`, `verified_at.date`, and freshness (fresh / stale).
   Explicitly flag any stale or low-trust doc and tell the caller to verify it against source.
6. **On a miss, say so.** If nothing matches, state plainly that the corpus does not cover
   this and fall back to reading code. Note the gap — a miss is a capture candidate for later.

## Guardrails

- Never present a doc's claim without its trust + freshness attached.
- When a doc is flagged stale, prefer the source of truth (the code) and note the conflict.
- Keep context lean: frontmatter for selection, bodies only for the branch you actually need.

## Reference

- Frontmatter fields this skill consumes: [`../../reference/frontmatter-schema.md`](../../reference/frontmatter-schema.md)
- Staleness + trust model: [`../../reference/staleness-convention.md`](../../reference/staleness-convention.md)
