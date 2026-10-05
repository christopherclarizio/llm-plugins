# Staleness convention - how docs stay honest

A stale doc can make agents confidently wrong. Each document therefore identifies
the code it describes and the commits against which it was verified, making changes
cheaply detectable.

## Code references

Each `code_references` entry supplies:

- `repository`: an ID in the [repository registry](repository-registry.md).
- `paths`: repo-relative files/globs relevant to the document.
- `verified_at`: that repository's verification commit, date, and verifier.

See [frontmatter-schema.md](frontmatter-schema.md) for the complete contract.

## The check

```sh
python3 <plugin-root>/skills/docs-router/scripts/check_staleness.py \
  <doc.md> [<another-doc.md> ...] --registry <corpus-root>/repositories.yaml
```

Add `--override <corpus-root>/repositories.local.yaml` when a local override exists.
The checker refreshes each referenced repository once for the entire batch, using
fetch and fast-forward-only updates of configured clean checkouts on the authoritative
branch. It never switches branches, discards edits, or creates merge commits.

For each reference it checks that the verified commit is an ancestor of the updated
checkout's revision, then runs:

```sh
git -C <checkout> log --oneline <verified-commit>..<updated-commit> -- <paths...>
```

No matching commits means **fresh** for this reference. Matching commits mean
**possibly stale**: the code changed, not necessarily the doc's claims. The checker
prints each reference's result, verified commit, and checked SHA.

| Document result | Meaning | Exit code |
|---|---|---|
| Fresh | All references checked successfully; none changed | `0` |
| Stale | All references checked successfully; at least one changed | `1` |
| Incomplete | Any refresh or verification failed | `2` |

For multiple documents, errors take precedence over staleness, which takes precedence
over fresh. Known stale references are still reported alongside failed ones.

A missing checkout or commit, unknown repository, non-ancestor verification commit,
wrong branch, dirty checkout, local-only/divergent history, or network/authentication
failure cannot produce an unqualified fresh result. If source is consulted from an
unrefreshed checkout, explicitly say **not confirmed current**.

The checked SHA is returned in output and retained in process/conversation memory
only. It does not update `verified_at`, the registry, or a separate snapshot file.
Assume refreshed working files stay unchanged during lookup; detected referenced
working-file or HEAD changes during checking are errors. Rerun if the checkout
changes while subsequently reading source.

## What freshness does not prove

- Correctness or completeness of the prose, or adequate coverage by its paths.
- Compatibility between independently refreshed repositories at a product release.
- That upstream has not advanced after the fetch.
- Applicability to a developer's feature branch. Changes on that branch are separate
  from documentation freshness against authoritative `main`.

Refreshing code does not re-verify documentation. Re-derive claims before updating
`verified_at`; do not simply copy the fetched SHA into it.

## Trust states

| `trust` | fresh (no detected drift) | stale (drift detected) |
|---|---|---|
| `human-reviewed` | Use directly within the verified scope. | Re-verify changed areas against source. |
| `agent-generated` | Corroborate load-bearing claims against source. | Lead only; prefer source. |
| `draft` | Lead only. | Lead only. |

Incomplete verification never grants authority, regardless of `trust`. Report both
trust and freshness with every document citation.

## Product documentation and maintenance

Product docs reference the code implementing the feature, across as many repositories
as necessary. This lets implementation changes flag product docs for re-verification.
It does not let code alone establish product knowledge: `human-reviewed` product docs
need someone who knows the product (PM/QE/support/experienced engineer).

Keep code references tightly scoped. When drift is detected, re-verify the affected
claims and update the corresponding repository's `verified_at`. Keep document-wide
trust honest; a verification entry naming a person does not automatically promote it.

Use `docs-verify` for deep grounding and explicit human review. `docs-capture` and
`docs-verify` prepare validated diffs for approval; neither silently stamps fetched
SHAs. Substantive agent changes to reviewed prose or evidentiary scope require renewed
human review. See [write-loop.md](write-loop.md) for trust transitions and write safety.
