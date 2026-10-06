---
name: validate-documentation-form
description: Checks documentation metadata, repository references, hierarchy, body structure, scope exclusions, and links. Use before approving documentation diffs, on demand, or in corpus CI. Reports structural errors and heuristic warnings; does not verify claims or refresh source.
---

# Validate documentation form

Check the corpus's structure, not whether its claims are true.

## Workflow

1. **Select the corpus.** Use `$NMWS_DOCS_CORPUS_ROOT` or a user-provided root.
   For an explicit example/demo check, use bundled `examples/` with
   `examples/repositories.example.yaml` as the registry.
2. **Run validation.** Follow [Helper commands](../../reference/helpers.md) to run
   `validate_docs.py --corpus-root <corpus-root>`. The registry defaults to
   `<corpus-root>/repositories.yaml`; use `--registry` to select another.
   No local override or source checkout is needed. uv may provision dependencies,
   but validation itself does not access Git or the network.
3. **Report results.** Identify errors by document and field/link. Exit `0` means
   no structural errors, `1` means invalid documents, and `2` means the check could
   not complete. Review altitude warnings manually: they are not proof of poor
   quality. Use `--strict` in CI only when zero heuristic warnings are required.

## Boundaries

Do not auto-fix prose, update verification metadata, or promote trust.
Requested repairs follow [Capture](../capture-information-in-documentation/SKILL.md)
or [Verify](../verify-documentation-accuracy/SKILL.md) and the
[Proposal and approval workflow](../../reference/proposal-workflow.md).
Structural success does not establish correctness, source coverage, freshness,
or human review. Report missing tools or failed downloads, never a skipped check
as success.
