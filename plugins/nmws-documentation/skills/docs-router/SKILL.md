---
name: docs-router
description: Retrieve relevant architecture, code, and product documentation from a NMWS documentation corpus. Use prior to working on of bug fixes, features, refactors, investigations, or when asked for explanations.
---

# docs-router

NMWS documentation is stored in a structured corpus. Use Read-loop entry point for the `nmws-documentation` corpus. It turns "understand this
area before touching it" from ad-hoc code spelunking into a cheap, consistent lookup — and
refuses to hand over a claim without flagging how much to trust it.

## When to use

At the **start** of a task that needs understanding of a subsystem or a product feature,
before diving into code. Skip it for trivial or purely mechanical work (a rename, a
formatting pass, a one-line fix in code you already understand).

## Corpus location

Resolve the docs corpus root in this order:

1. `$NMWS_DOCS_CORPUS_ROOT`, if set.
2. Otherwise `${CLAUDE_PLUGIN_ROOT}/examples` (bundled illustrative docs).

`PLUGIN_ROOT` below means this plugin's installed directory: use `CLAUDE_PLUGIN_ROOT`
when available, otherwise resolve it from this skill's location (`skills/docs-router/`
is beneath the plugin root). Use the same fallback for locating bundled examples.
Examples are fabricated illustrations, not authoritative knowledge; their configuration must
be replaced before accessing real repositories.

## Prerequisites

Git and `uv` are required. Use [set-me-up](../set-me-up/SKILL.md) to install missing
tools and configure the corpus. Run helpers through `uv run --locked --script`;
uv manages Python and isolated dependencies from inline metadata and bundled
lockfiles, without pip or manual virtualenv setup. Initial use may require downloads.
Surface missing tools or failed downloads explicitly rather than skipping freshness
checks. Do not install dependencies into the user's project.

## Procedure

1. **Index cheaply.** Glob `code/**/*.md` and `product/**/*.md` under the corpus root and read **only** the
   frontmatter of each (the block between the first pair of `---`). Do not read bodies yet.
2. **Select.** Rank docs against the task using `description`, `keywords`, `tree`, and
   `tier`. Prefer the coarsest matching `tier` first (`architecture`/`overview`), then drill.
3. **Progressive disclosure.** Read the body of the top match. Follow its `children` and
   `related` links **only as far as the task needs**, and stop once you have enough. Never
   load the whole tree.
4. **Refresh and check freshness.** Collect every doc whose body you loaded into one
   batch. For docs with `code_references`, use the corpus's `repositories.yaml`:
   ```sh
   uv run --locked --script "${PLUGIN_ROOT}/skills/docs-router/scripts/check_staleness.py" \
     <doc-path> [<other-loaded-doc-path> ...] --registry <corpus-root>/repositories.yaml
   ```
   Add `--override <corpus-root>/repositories.local.yaml` if that file exists.
   The checker resolves each reference to its configured `local` checkout, validates
   its remote/clean state/authoritative branch, fetches, and fast-forwards only.
   Each needed repository is refreshed once per batch. Do not separately run the
   refresh helper for the same lookup.

   Exit `0` = fresh, `1` = stale, `2` = error/incomplete. A refresh failure must be
   reported as **not confirmed current**, never fresh. Still report known results
   for other repositories. Treat stale, draft, or agent-generated docs as leads,
   not authority. Missing registry/checkout/access permission is a verification gap,
   not permission to guess repository locations or mutate another checkout.
5. **Brief with citations.** Return a compact synthesis, then a citation list: for each doc
   used — `id`, `tier`, `trust`, and overall freshness (fresh / stale / incomplete).
   For each code reference include repository ID, verification date, checked SHA,
   and per-repository freshness.
   The refresh helper's SHAs stay in tool/conversation output, not a saved snapshot.
   Explicitly flag stale, incomplete, or low-trust docs and verify load-bearing claims
   against code in the correct configured checkout.
6. **Hand off selectively.** If nothing matches, state plainly that the corpus does not
   cover this and fall back to reading code. Keep a compact conversation-only handoff:
   uncovered question, relevant document IDs, any contradictions, consulted repository
   IDs/checked SHAs, and task-branch differences. After the task, use `docs-capture`
   only if meaningful reusable understanding emerged; a miss alone does not justify
   a capture offer. Use `docs-verify` for existing claims needing deep re-derivation.
   Do not queue gaps on disk, write docs, or advance verification metadata in the router.

## Guardrails

- Never present a doc's claim without its trust + freshness attached.
- When a doc is flagged stale, prefer the source of truth (the code) and note the conflict.
- Never switch branches, reset, stash, rebase, discard edits, or clone to repair a
  configured checkout. Respect network and authentication permissions.
- Assume refreshed checkouts remain unchanged during source reads; rerun the lookup
  if they change. Report task-branch differences separately from freshness on main.
- Updating a checkout does not update a doc's `verified_at` or prove its claims.
- Keep context lean: frontmatter for selection, bodies only for the branch you actually need.

## Reference

- Frontmatter fields this skill consumes: [`../../reference/frontmatter-schema.md`](../../reference/frontmatter-schema.md)
- Staleness + trust model: [`../../reference/staleness-convention.md`](../../reference/staleness-convention.md)
- Repository configuration: [`../../reference/repository-registry.md`](../../reference/repository-registry.md)
- Write-loop handoff: [`../../reference/write-loop.md`](../../reference/write-loop.md)
