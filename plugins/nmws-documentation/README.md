# nmws-documentation

Agent-first documentation for a codebase **and** the product it ships, structured
for progressive disclosure and designed so it can be trusted.

This plugin holds the **machinery**, not the docs themselves:

- a **router skill** (`docs-router`) that assembles the relevant docs for a task
  before an agent starts reading code;
- a **staleness contract** (code references + per-repository verification commits) so drift is
  cheaply detectable rather than silent;
- a **repository registry and safe refresh** for local checkouts on authoritative branches;
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
   confidently wrong. Every doc references the code it describes and records
   the commit it was last verified against in each repository, so
   [`skills/docs-router/scripts/check_staleness.py`](skills/docs-router/scripts/check_staleness.py)
   can refresh configured checkouts and flag drift with a `git log` per repository. See
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

## Multiple repositories

One corpus can describe a feature whose implementation spans several repositories.
Docs use `code_references`, with repository IDs, paths, and independent verification
commits. Code and product hierarchy links remain corpus-wide.

Create `repositories.yaml` in the corpus root, mapping each ID to `remote`,
`authoritative_branch` (normally `main`), and `local` (a checkout path). See the
[registry contract](reference/repository-registry.md) and the illustrative
[`examples/repositories.example.yaml`](examples/repositories.example.yaml).
Optional `repositories.local.yaml` overrides let developers choose different paths.

The router batches loaded docs into one check:

```sh
python3 <plugin-root>/skills/docs-router/scripts/check_staleness.py \
  <doc.md> [<another-doc.md> ...] --registry <corpus-root>/repositories.yaml
```

The checker fetches and fast-forwards each referenced checkout once. It requires a
clean checkout on the configured branch with no local-only/divergent commits; it
never switches branches, resets, stashes, or discards edits. Multiple worktrees are
fine: `local` selects the one used for authoritative source reads. Use a separate
checkout for feature work.

Refresh/check failures are **incomplete / not confirmed current**, not fresh.
Successful refresh prints the checked SHA but saves no separate snapshot and never
updates document verification metadata. Existing `sources` + `verified_at` docs
remain supported with `--repo <checkout>`; that mode checks local HEAD without fetching.

## Requirements and tests

Git, Python 3.9+, and PyYAML are required. Use your Python environment or a virtual
environment, then install:

```sh
python3 -m pip install -r <plugin-root>/requirements.txt
python3 -m unittest discover -s <plugin-root>/tests -v
```

Tests use temporary local Git repositories; they need no network or proprietary code.

## Layout

```
.claude-plugin/plugin.json        plugin manifest
reference/
  frontmatter-schema.md           the shared frontmatter contract (the router's API)
  repository-registry.md          logical repositories + selected local checkouts
  staleness-convention.md         code references + the drift check + trust states
templates/
  code-doc.template.md            code-tree body skeleton
  product-doc.template.md         product-tree body skeleton
skills/docs-router/
  SKILL.md                        the read-loop router
  scripts/check_staleness.py      batched refresh + per-repository drift detection
  scripts/refresh_repositories.py standalone safe checkout refresh
  scripts/repositories.py         shared parsing + Git operations
requirements.txt                 Python dependency
tests/                           temporary-repository regression tests
examples/                        illustrative legacy + multi-repository docs
  code/ppro-playback-engine.md
  code/ppro-scripting-architecture.md
  product/prod-playback-and-scrubbing.md
  product/prod-scripting.md
  repositories.example.yaml
```

## Status

Pilot. Read loop (routing + staleness) only. The write loop — capture/graduate,
verify/ground, style validation — is intentionally deferred until there's enough
corpus to justify it.
