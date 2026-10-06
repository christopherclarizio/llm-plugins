# Documentation update workflow

The skill establishes the evidence and drafts the change; this protocol governs
persistence. Capture writes to the configured corpus. Accuracy-verification
updates require exact-diff approval.

## Capture

1. **Retain the baseline.** Keep the original contents or absence of every target
   document and the examined SHAs of consulted repositories. Run `validate_docs.py`
   in the selected corpus to identify pre-existing structural errors.
2. **Check for concurrent changes.** Before writing, compare targets to their
   original contents or absence, and check consulted source checkouts against
   their examined SHAs and clean state using the commands below. If a target or
   source changed, re-read it and re-derive the update; never overwrite intervening
   edits or repair a checkout to force the change through.
3. **Write to the corpus.** Write the complete evidence-backed update
   beneath `$NMWS_DOCS_CORPUS_ROOT` or the user-provided corpus root, preserving
   document paths and updating navigation links together.
4. **Validate and report.** Run `validate_docs.py` in the real corpus and inspect
   the resulting diff. Resolve errors introduced by the update and review altitude
   warnings manually. Report exact paths written, trust/freshness, grounding gaps,
   pre-existing errors, and any failure. Do not represent a saved but failing
   change as complete.

Saving agent changes is not human review. Do not stage, commit, push, or promote
trust without separate authorization. Never persist unsupported new claims or
fabricated verification metadata; a `draft` must state its grounding gaps.

## Accuracy verification

Permission to investigate or verify is not approval of an unseen diff.

### 1. Validate the proposal privately

Retain the original contents or absence of every target document and the checked
SHAs of consulted repositories. Materialize a temporary private copy of the corpus,
preserving document paths and the registry; source checkouts need not be copied.
Apply the complete proposed diff there and run `validate_docs.py`.

Resolve all errors introduced by the proposal and review altitude warnings manually.
Report pre-existing errors explicitly; do not claim the corpus passes while they
remain. An incomplete proposal may be discussed with its gaps, but unsupported new
claims and fabricated verification metadata must not be persisted.

### 2. Request exact-diff approval

Present the **exact validated diff**, affected document IDs, source evidence/SHAs,
trust changes, verification gaps, and any remaining structural errors.
Ask for yes/no approval of that proposal, not an open-ended writing assignment.
Respect rejection without modifying the corpus.

Approval to save agent changes does not constitute human review or authorize
staging, committing, pushing, or promoting trust.

### 3. Check for concurrent changes

Before applying, compare each target to its original contents or absence.
Check every consulted source checkout against its examined SHA and clean state:

```sh
git -C "<checkout>" rev-parse HEAD
git -C "<checkout>" status --porcelain --untracked-files=all
```

A changed target, changed SHA, or dirty checkout invalidates the proposal.
Re-derive and revalidate it, then obtain renewed approval; never overwrite intervening
edits or repair a checkout to force the proposal through.

### 4. Apply and confirm the result

Apply only the approved diff. Run validation in the real corpus and inspect the
resulting diff. Report the exact paths written, trust/freshness, grounding gaps,
and any failure. Do not represent an applied but failing change as complete.

Remove only the temporary artifacts created for this proposal.
Do not stage, commit, push, or promote trust without separate authorization.

### Completion checklist

- Evidence and verification metadata cover the proposed claims.
- The exact diff was validated and explicitly approved.
- Targets and source baselines are unchanged since proposal preparation.
- Only the approved diff was applied, and the real-corpus result was checked.

Distinguish **proposal prepared**, **approved diff applied**, and **fully grounded**.
Approval or structural validity alone does not establish grounding.
