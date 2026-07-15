# Staleness convention — how docs stay honest

A stale doc is worse than no doc: agents (and people) trust it and become confidently
wrong. So every doc is anchored to the code it describes, and drift is made **cheaply
detectable** rather than left silent.

## The anchor

Two frontmatter fields do the work (see [`frontmatter-schema.md`](frontmatter-schema.md)):

- `sources` — the repo-relative files/globs the doc's claims derive from.
- `verified_at.commit` — HEAD of the code repo the last time a human or agent checked
  the doc against reality.

## The check

Drift detection is one command — no heuristics:

```sh
git -C <code-repo> log --oneline <verified_at.commit>..HEAD -- <sources...>
```

- **Empty output** → the described code hasn't changed since verification → the doc is
  *fresh*.
- **Non-empty** → the described code has moved → the doc is *possibly stale* and must
  be treated as a lead, not an authority, until re-verified.

[`../skills/docs-router/scripts/check_staleness.py`](../skills/docs-router/scripts/check_staleness.py)
runs exactly this, reading `sources` and `verified_at.commit` from the doc's
frontmatter. Exit code `0` = fresh, `1` = stale, `2` = error.

## Trust states

`trust` and freshness combine into how much weight a doc gets:

| `trust` | fresh (no drift) | stale (drift detected) |
|---|---|---|
| `human-reviewed` | **Authoritative.** Use directly. | Use with caution; re-verify the changed areas against source. |
| `agent-generated` | Useful, but unverified by a human — corroborate load-bearing claims against source. | Lead only. Prefer the source of truth. |
| `draft` | Lead only. | Lead only. |

The router never hands a claim to a caller without its trust + freshness attached, and
when a doc is flagged stale it tells the caller to prefer the code and note the conflict.

## Product docs anchor at the implementing code

Product-tree docs have no in-repo source of truth of their own, so their `sources`
point at the **code that implements the feature**. This does double duty: the same
`git log` drift check works, *and* the code↔product bridge is maintained mechanically —
when the implementing code changes, the product doc is flagged for re-verification too.

Because product knowledge is only lossily inferable from code, product docs should reach
`trust: human-reviewed` via someone who actually knows the product (PM/QE/support/
long-tenured engineer). Do not let an agent bootstrap product docs from code alone — that
launders code-inferred guesses into authoritative-looking prose.

## Keeping it fresh

- Re-verify a doc when the staleness check flags it, and bump `verified_at`.
- Prefer tightly-scoped docs: fewer, more focused `sources` make drift detection sharper
  and point at less. (This is why the templates ask each doc to state what it does *not*
  cover.)
