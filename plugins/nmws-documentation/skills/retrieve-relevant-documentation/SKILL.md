---
name: retrieve-relevant-documentation
description: Finds code and product documentation relevant to a task and reports its trust and freshness. Use before substantive bug fixes, features, refactors, investigations, or explanations; skip trivial or purely mechanical work.
---

# Retrieve relevant documentation

Return the understanding needed for the task, not a dump of the corpus.

## Before starting

Use `$NMWS_DOCS_CORPUS_ROOT`. If unset or empty, report **"documentation corpus not
configured"** and continue with source investigation without corpus lookup or
freshness checks. Never substitute bundled examples.

Resolve the plugin location and run commands as described in
[Helper commands](../../reference/helpers.md). Git and uv are required.

## Workflow

1. **Find candidates.** Run `discover_docs.py` with a task-specific query in
   `focused` mode; use `orientation` for a broad introduction. Treat the bounded
   metadata shortlist as suggestions, not a semantic verdict. Refine the query
   when results are weak or truncated; a lexical miss does not prove missing coverage.
2. **Read selectively.** Choose the most relevant document. Go directly to a
   component/workflow for narrow questions, or start with architecture/overview
   for orientation. Follow `children` and `related` only as needed; resolve IDs
   with the helper's `--id` option. Do not load the whole tree.
3. **Establish freshness.** Batch every document whose body you read through
   `check_staleness.py` with the corpus registry and any local override. It refreshes
   each needed checkout once; do not refresh separately. Failures mean **not
   confirmed current**, not fresh. Retain known results for other repositories.
   Verify load-bearing claims from stale, incomplete, draft, or agent-generated
   documents against the configured source checkout.
4. **Brief the task.** Give a compact synthesis and citations. For each document,
   include `id`, `tier`, `trust`, and overall freshness (`fresh`, `stale`, or
   `incomplete`). For each code reference, include repository ID, verification
   date, checked SHA, and per-repository freshness. State contradictions,
   verification gaps, and differences on the task branch explicitly.

## When coverage is missing or uncertain

If refined lookup still yields no relevant document, report the coverage gap and
investigate source. Keep the unanswered question, relevant document IDs, repository
SHAs, contradictions, and task-branch differences in the conversation, not a saved
snapshot or gap queue.

After the task, if meaningful reusable understanding emerged and the user requested
a capture review or `nmws-documentation-auto` reminders are active, use
[Offer capture](../offer-documentation-capture/SKILL.md) and wait for consent.
Use [Capture](../capture-information-in-documentation/SKILL.md) directly when the
user already authorized capture of those findings. Use
[Verify](../verify-documentation-accuracy/SKILL.md) to re-derive existing claims.
Retrieval never writes documents or advances verification metadata.

## Boundaries

Attach trust and freshness to every document citation. Refreshing code does not
prove a document correct. If checkout files or HEAD change during source reads,
rerun the lookup. Never repair a checkout, guess another location, or bypass
network/authentication permissions.

## References

- [Helper commands and result handling](../../reference/helpers.md)
- [Frontmatter contract](../../reference/frontmatter-schema.md)
- [Trust and staleness](../../reference/staleness-convention.md)
- [Repository configuration and refresh safety](../../reference/repository-registry.md)
