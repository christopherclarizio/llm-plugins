# clarizio-documentation

Agent-first documentation for a codebase **and** the product it ships, structured
for progressive disclosure and designed so it can be trusted.

This plugin holds the **machinery**, not the docs themselves:

- a **router skill** (`docs-router`) that assembles the relevant docs for a task
  before an agent starts reading code;
- a **staleness contract** (source anchors + a `verified_at` commit) so drift is
  cheaply detectable rather than silent;
- two **body templates** (code tree, product tree) that share one frontmatter schema.

## Why it's built this way

Four ideas do all the work:

1. **The frontmatter is the contract.** Every doc, in either tree, carries the same
   YAML frontmatter. The router and the staleness check are just consumers of those
   fields — so a field only exists if something reads it. See
   [`reference/frontmatter-schema.md`](reference/frontmatter-schema.md).

2. **Two trees, shared frontmatter, different bodies.** The *code* tree answers
   "how is this built / how does it work"; the *product* tree answers "what does this
   do for a user, how is it used, where does it fit, what are the sharp edges." Same
   schema, different [templates](templates/).

3. **Staleness is first-class.** A stale doc is worse than no doc — it makes agents
   confidently wrong. Every doc anchors to the source files it describes and records
   the commit it was last verified against, so
   [`skills/docs-router/scripts/check_staleness.py`](skills/docs-router/scripts/check_staleness.py)
   can flag drift with a single `git log`. See
   [`reference/staleness-convention.md`](reference/staleness-convention.md).

4. **Progressive disclosure.** Docs form a shallow hierarchy
   (`architecture → subsystem → component`, `overview → feature → workflow`). The
   router loads only the branch a task needs, keeping context lean — the same shape
   Agent Skills use, including a description-per-doc discovery layer.

Docs grow **demand-driven**: seed the top of each tree, then graduate proven
understanding into shared docs as real tasks surface it (the write-loop skills come
later — this pilot ships the read loop only).

## Configuring the corpus

The router looks for the documentation corpus (the actual docs) in this order:

1. `$CLARIZIO_DOCS_ROOT`, if set — point this at the vended docs location in your
   working repo.
2. Otherwise the bundled [`examples/`](examples/), for demonstration only.

## Layout

```
.claude-plugin/plugin.json        plugin manifest
reference/
  frontmatter-schema.md           the shared frontmatter contract (the router's API)
  staleness-convention.md         source anchors + the drift check + trust states
templates/
  code-doc.template.md            code-tree body skeleton
  product-doc.template.md         product-tree body skeleton
skills/docs-router/
  SKILL.md                        the read-loop router
  scripts/check_staleness.py      drift detection against the code repo
examples/                         one worked doc per tree (illustrative content)
  code/ppro-playback-engine.md
  product/prod-playback-and-scrubbing.md
```

## Status

Pilot. Read loop (routing + staleness) only. The write loop — capture/graduate,
verify/ground, style validation — is intentionally deferred until there's enough
corpus to justify it.
