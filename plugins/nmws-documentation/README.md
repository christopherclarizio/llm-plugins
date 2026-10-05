# nmws-documentation

Agent-first documentation for a codebase **and** the product it ships, structured
for progressive disclosure and designed so it can be trusted.

This plugin holds the **machinery**, not the docs themselves:

- a **router skill** (`docs-router`) that assembles the relevant docs for a task
  before an agent starts reading code;
- a **staleness contract** (code references + per-repository verification commits) so drift is
  cheaply detectable rather than silent;
- a **repository registry and safe refresh** for local checkouts on authoritative branches;
- two **body templates** (code tree, product tree) that share one frontmatter schema;
- a **write loop** (`docs-capture`, `docs-verify`) that prepares source-grounded diffs
  for approval and requires explicit human review before promoting trust;
- **validation** (`docs-validate`) and an on-demand paired evaluation workflow
  (`docs-evaluate`).

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
understanding into shared docs as real tasks surface it. Capture is selective, not an
automatic offer after every task.

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
updates document verification metadata. Only per-repository `code_references` are
supported; there is no local-only or top-level `sources`/`verified_at` mode.

## Write loop

Use `docs-capture` after a meaningful investigation uncovers reusable understanding,
especially after a router miss or corrected assumption. It deduplicates against the
corpus, grounds claims in configured authoritative checkouts, fills the appropriate
template, and presents a concrete validated diff for approval.

Use `docs-verify` to re-derive an existing doc's claims and report supported,
contradicted, and unresolved assertions. A fetched SHA or fresh staleness result is
not verification. Metadata advances only after checking that repository's full
contribution. Explicit human acceptance of the full grounded document is required
to promote trust; approval to save an agent diff is not human review.

Both workflows require an explicit private corpus destination and check source/target
stability before applying approved changes. They never default writes to bundled examples,
automatically commit, or push. See the [write-loop contract](reference/write-loop.md).

`docs-validate` runs offline structural and link checks:

```sh
python3 <plugin-root>/skills/docs-router/scripts/validate_docs.py \
  --corpus-root <corpus-root>
```

It reads docs under `code/` and `product/` and defaults to the corpus's
`repositories.yaml`. Exit `0` means structurally valid, `1` means document errors,
and `2` means configuration/read/dependency failure. Altitude warnings require human
or agent judgment; `--strict` also fails on warnings. This does not prove correctness
or freshness. See [validation](reference/validation.md) for checks and CI usage.

`docs-evaluate` provides an explicitly requested paired-task pilot with and without
the corpus, recording correctness, wrong turns, and measured tokens when available.
It requires isolated contexts and keeps all source-derived evidence private.

## Requirements and tests

Git, Python 3.9+, PyYAML, and markdown-it-py are required. Use your Python environment or a virtual
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
  write-loop.md                   approval, grounding, and human-review contract
  validation.md                   deterministic checks and heuristic limits
templates/
  code-doc.template.md            code-tree body skeleton
  product-doc.template.md         product-tree body skeleton
skills/docs-router/
  SKILL.md                        the read-loop router
  scripts/check_staleness.py      batched refresh + per-repository drift detection
  scripts/refresh_repositories.py standalone safe checkout refresh
  scripts/repositories.py         shared parsing + Git operations
  scripts/validate_docs.py        offline corpus validation (shared by write skills)
skills/docs-capture/SKILL.md      selective, approval-gated capture
skills/docs-verify/SKILL.md       deep grounding and human-review workflow
skills/docs-validate/SKILL.md     on-demand / CI validation
skills/docs-evaluate/SKILL.md     private paired-task evaluation pilot
requirements.txt                 Python dependencies
tests/                           temporary-repository regression tests
examples/                        illustrative single- and multi-repository docs
  code/ppro-playback-engine.md
  code/ppro-scripting-architecture.md
  product/prod-playback-and-scrubbing.md
  product/prod-scripting.md
  repositories.example.yaml
```

## Status

Pilot. Read loop, approval-gated capture/verification, offline validation, and an
on-demand evaluation workflow are available. The workflows are agent skills, not
autonomous prose generators; semantic grounding and human review remain explicit.
