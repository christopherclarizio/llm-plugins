---
name: retrieve-relevant-documentation
description: Retrieve relevant architecture, code, and product documentation from a NMWS documentation corpus. Use prior to working on of bug fixes, features, refactors, investigations, or when asked for explanations.
---

# retrieve-relevant-documentation

Retrieve relevant documentation from the structured `nmws-documentation` corpus. This turns "understand this
area before touching it" from ad-hoc code spelunking into a cheap, consistent lookup — and
refuses to hand over a claim without flagging how much to trust it.

## When to use

At the **start** of a task that needs understanding of a subsystem or a product feature,
before diving into code. Skip it for trivial or purely mechanical work (a rename, a
formatting pass, a one-line fix in code you already understand).

## Corpus location

Use `$NMWS_DOCS_CORPUS_ROOT` as the docs corpus root. If it is unset or empty,
report **"documentation corpus not configured"**, skip corpus lookup and freshness
checks, and continue with source investigation. Do not blockon corpus setup.

`PLUGIN_ROOT` below means this plugin's installed directory: use `CLAUDE_PLUGIN_ROOT`
when available, otherwise resolve it from this skill's location (`skills/retrieve-relevant-documentation/`
is beneath the plugin root). This fallback locates helpers, not a documentation corpus.

## Prerequisites

Git and `uv` are required. Use [set-me-up](../set-me-up/SKILL.md) to install missing
tools and configure the corpus. Run helpers through `uv run --locked --script`;
uv manages Python and isolated dependencies from inline metadata and bundled
lockfiles, without pip or manual virtualenv setup. Initial use may require downloads.
Surface missing tools or failed downloads explicitly rather than skipping freshness
checks. Do not install dependencies into the user's project.

## Procedure

1. **Discover cheaply.** Run one local metadata scan instead of loading every document's
   frontmatter into context:
   ```sh
   uv run --locked --script "${PLUGIN_ROOT}/skills/retrieve-relevant-documentation/scripts/discover_docs.py" \
     --corpus-root "$NMWS_DOCS_CORPUS_ROOT" --query "<task question or component>" \
     --mode focused --limit 5
   ```
   Use `focused` for a narrow task: exact ID/title/keyword matches lead, then query-term
   coverage and weighted field matches, with finer tiers breaking relevance ties.
   Use `--mode orientation` for a broad introduction: coarser tiers lead among matching
   docs. Query-free orientation is allowed to find corpus entry points.
   Optionally filter with `--tree code` or `--tree product`.
   JSON contains at most `--limit` candidates (default 5, maximum 20), corpus-relative
   paths, routing metadata, navigation IDs, and match evidence. It also reports scanned
   and matched counts and whether the shortlist was truncated. No bodies, saved index,
   repository access, or freshness assertions. The local scan remains linear in corpus
   size, but model context is limited to the shortlist.
   Exit `0` includes an empty shortlist; `2` is a read/configuration/metadata error
   with an explicit JSON error and stderr diagnostic, not proof of a coverage gap.
2. **Select flexibly.** Treat the deterministic lexical order as a shortlist, not a
   semantic verdict. Choose using the task, descriptions, keywords, tree, and tier.
   Go directly to a precisely relevant component/workflow for narrow questions; start
   with architecture/overview for orientation. If needed, refine the query or change
   mode/tree rather than reading all frontmatter. A lexical miss is not proof that
   the corpus has no semantic coverage.
3. **Progressive disclosure.** Read the body of the top match. Follow its `children` and
   `related` links **only as far as the task needs**, and stop once you have enough. Never
   load the whole tree. Resolve a navigation ID to its path and metadata with the same
   helper's `--id <document-id>` instead of rescanning frontmatter in model context.
4. **Refresh and check freshness.** Collect every doc whose body you loaded into one
   batch. For docs with `code_references`, use the corpus's `repositories.yaml`:
   ```sh
   uv run --locked --script "${PLUGIN_ROOT}/skills/retrieve-relevant-documentation/scripts/check_staleness.py" \
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
   IDs/checked SHAs, and task-branch differences. After the task, use `capture-information-in-documentation`
   only if meaningful reusable understanding emerged; a miss alone does not justify
   a capture offer. Use `verify-documentation-accuracy` for existing claims needing deep re-derivation.
   Do not queue gaps on disk, write docs, or advance verification metadata in the router.

## Guardrails

- Never present a doc's claim without its trust + freshness attached.
- When a doc is flagged stale, prefer the source of truth (the code) and note the conflict.
- Never switch branches, reset, stash, rebase, discard edits, or clone to repair a
  configured checkout. Respect network and authentication permissions.
- Assume refreshed checkouts remain unchanged during source reads; rerun the lookup
  if they change. Report task-branch differences separately from freshness on main.
- Updating a checkout does not update a doc's `verified_at` or prove its claims.
- Keep context lean: bounded metadata candidates for selection, bodies only for the
  branch you actually need.

## Reference

- Frontmatter fields this skill consumes: [`../../reference/frontmatter-schema.md`](../../reference/frontmatter-schema.md)
- Staleness + trust model: [`../../reference/staleness-convention.md`](../../reference/staleness-convention.md)
- Repository configuration: [`../../reference/repository-registry.md`](../../reference/repository-registry.md)
