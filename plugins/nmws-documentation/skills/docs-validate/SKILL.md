---
name: docs-validate
description: Runs deterministic validation of documentation frontmatter, repository references, hierarchy, body structure, scope exclusions, and Markdown links. Use before approving capture/verification diffs, on demand, or in corpus CI. Reports altitude heuristics as warnings; does not prove prose correctness or refresh source.
---

# docs-validate

Resolve `PLUGIN_ROOT` from `CLAUDE_PLUGIN_ROOT`, otherwise this skill's location.
Use `$NMWS_DOCS_CORPUS_ROOT` or a corpus root provided by the user. To validate illustrative docs,
use the bundled examples with `--registry <plugin-root>/examples/repositories.example.yaml`.
`uv` is required; [set-me-up](../set-me-up/SKILL.md) installs missing tools and
configures the corpus. uv manages Python and isolated dependencies from the script's
metadata and bundled lockfile; no pip or manual virtualenv setup is needed. Initial
use may require downloads. Report missing tools or failed downloads instead of
skipping checks.

Run:

```sh
uv run --locked --script "${PLUGIN_ROOT}/skills/docs-router/scripts/validate_docs.py" \
  --corpus-root <corpus-root>
```

The default registry is `<corpus-root>/repositories.yaml`. `--registry` can select
another file. No local override is needed: validation never accesses source checkouts,
Git, or the network.

Report errors with their document and field/link. Exit `0` means no structural errors,
`1` means validation failures, and `2` means configuration/read/dependency failure.
Warnings are not proof of low quality: inspect altitude manually. Use `--strict` in
CI only if the corpus deliberately requires zero heuristic warnings.

Do not auto-fix, rewrite prose, update verification metadata, or promote trust.
An explicitly requested fix follows the approval-gated capture/verification workflow.
Structural success does not establish correctness, adequate source coverage, freshness,
or human review.

See the [validation contract](../../reference/validation.md) for exact checks and limits.
