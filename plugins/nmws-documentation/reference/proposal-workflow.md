# Proposal and approval workflow

Use this protocol for both capture and accuracy-verification updates. The skill
establishes the evidence and drafts the change; this protocol governs persistence.
Permission to investigate, document, or verify is not approval of an unseen diff.

## 1. Validate the proposal privately

Retain the original contents or absence of every target document and the checked
SHAs of consulted repositories. Materialize a temporary private copy of the corpus,
preserving document paths and the registry; source checkouts need not be copied.
Apply the complete proposed diff there and run `validate_docs.py`.

Resolve all errors introduced by the proposal and review altitude warnings manually.
Report pre-existing errors explicitly; do not claim the corpus passes while they
remain. An incomplete proposal may be discussed with its gaps, but unsupported new
claims and fabricated verification metadata must not be persisted.

## 2. Request exact-diff approval

Present the **exact validated diff**, affected document IDs, source evidence/SHAs,
trust changes, verification gaps, and any remaining structural errors.
Ask for yes/no approval of that proposal, not an open-ended writing assignment.
Respect rejection without modifying the corpus.

Approval to save agent changes does not constitute human review or authorize
staging, committing, pushing, or promoting trust.

## 3. Check for concurrent changes

Before applying, compare each target to its original contents or absence.
Check every consulted source checkout against its examined SHA and clean state:

```sh
git -C "<checkout>" rev-parse HEAD
git -C "<checkout>" status --porcelain --untracked-files=all
```

A changed target, changed SHA, or dirty checkout invalidates the proposal.
Re-derive and revalidate it, then obtain renewed approval; never overwrite intervening
edits or repair a checkout to force the proposal through.

## 4. Apply and confirm the result

Apply only the approved diff. Run validation in the real corpus and inspect the
resulting diff. Report the exact paths written, trust/freshness, grounding gaps,
and any failure. Do not represent an applied but failing change as complete.

Remove only the temporary artifacts created for this proposal.
Do not stage, commit, push, or promote trust without separate authorization.

## Completion checklist

- Evidence and verification metadata cover the proposed claims.
- The exact diff was validated and explicitly approved.
- Targets and source baselines are unchanged since proposal preparation.
- Only the approved diff was applied, and the real-corpus result was checked.

Distinguish **proposal prepared**, **approved diff applied**, and **fully grounded**.
Approval or structural validity alone does not establish grounding.
