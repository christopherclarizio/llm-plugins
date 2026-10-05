# Write-loop contract

The read loop supplies coverage gaps and source baselines; the write loop graduates
durable understanding into approved, grounded documents. Machinery lives in this public
plugin; source-derived content and evaluation/review artifacts stay private.

## Workflows

| Need | Entry point | Output |
|---|---|---|
| Preserve a durable discovery | `docs-capture` | Deduplicated, grounded, validated diff for approval |
| Re-derive a doc's claims | `docs-verify` | Supported/contradicted/unresolved evidence report and proposed diff |
| Check the corpus contract | `docs-validate` | Deterministic errors and heuristic warnings |
| Measure corpus value | `docs-evaluate` | Private paired-task results |

Capture is selective. A router miss only nominates a candidate; useful understanding
must actually emerge. No automatic end-of-task offers, saved gap queues, generated
indexes, or new frontmatter fields are required.

## Writes and verification

Writes require an explicit corpus destination and approval of the concrete diff.
Bundled examples are never a default write target. Changes to navigation are included
in the same proposal. Source checkouts and target documents must remain unchanged
between grounding, approval, and application; otherwise re-derive and seek renewed
approval. Do not overwrite concurrent edits or automatically stage/commit/push.

Use the current `code_references` format only. Each repository has an independent
verification commit/date/verifier. Advancing that commit asserts that the document's
entire contribution from that repository was checked, including the adequacy of paths.
Partial investigation does not justify copying a fetched SHA into metadata.
Unknown repositories, inaccessible source, checkout mutation, or unresolved assertions
must remain explicit gaps, never success-shaped verification.

Source is necessary but may not establish historical rationale, product usage, or
user-visible limitations. Require independent evidence or knowledgeable human confirmation.
Latest-main revisions across repositories do not establish release compatibility.

## Trust transitions

| Event | Trust outcome |
|---|---|
| Incomplete proposal | `draft`; no fabricated verification metadata |
| New fully grounded agent document | `agent-generated` |
| Metadata-only re-verification; prose and evidence scope unchanged | Preserve existing trust |
| Substantive agent change to reviewed prose or evidence scope | `agent-generated`, or `draft` if material gaps remain |
| Explicit human acceptance of the exact full grounded document | `human-reviewed` |

Approval to persist an agent diff is not human review. Human review requires an
identified reviewer accepting the full scope with no material unresolved claims.
Product documents need a reviewer with product knowledge. `verified_at.by` records
who actually verified that repository's contribution; it is not a trust-promotion switch.

## Validation

Validate the full proposed corpus in a private temporary copy before approval, then the
real corpus after application. Review warnings rather than treating them as semantic
proof. Validation, grounding, freshness, and human review are separate results.
See [validation.md](validation.md) and [staleness-convention.md](staleness-convention.md).
