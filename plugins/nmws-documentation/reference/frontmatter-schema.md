# Frontmatter schema — the router's contract

Every documentation file, in **both** the code tree and the product tree, opens with
the same YAML frontmatter block. This uniformity is deliberate: the `docs-router`
skill and `check_staleness.py` consume these fields, so the frontmatter is an **API**,
not decoration. The rule of thumb — **a field needs a real read-loop or write-loop
consumer; otherwise it does not belong here.**

The *body* below the frontmatter differs by tree (see the two files in
[`../templates/`](../templates/)); the frontmatter does not.

## Fields

| Field | Required | Type | Allowed / format | Purpose |
|---|---|---|---|---|
| `id` | ✅ | string | stable kebab-case slug | The doc's stable handle. The router keys on it and links resolve to it. Prose links use relative paths (clickable); `id` is the durable identity that survives a file move. Don't rename casually. |
| `title` | ✅ | string | — | Human-readable title. |
| `tree` | ✅ | enum | `code` \| `product` | Which hierarchy the doc belongs to. Selects the body template. |
| `tier` | ✅ | enum | code: `architecture` \| `subsystem` \| `component`; product: `overview` \| `feature` \| `workflow` | Altitude. Lets the router filter and rank locally ("start coarse, then drill") without walking the parent chain, and selects which tier vocabulary/body applies. |
| `description` | ✅ | string | 1–3 sentences | **The routing hook.** Lead with the question the doc answers; end with "Read before &lt;the tasks this is relevant to&gt;." This is what the router matches on without loading the body. |
| `parent` | — | id | — | The next tier up. Navigation, not altitude (that's `tier`). |
| `children` | — | list of ids | — | The tier(s) down. |
| `related` | — | list of ids | — | Cross-links. **Include an existing counterpart in the other tree** — the code↔product bridge. Do not invent a missing counterpart. |
| `keywords` | — | list of strings | — | Extra matching signal for the router. |
| `code_references` | ✅ | list of mappings | one entry per repository | The code the doc's claims derive from. Product docs reference the **implementing** code. |
| `code_references[].repository` | ✅ | string | registry repository ID | Identifies a repository independently of its checkout path. |
| `code_references[].paths` | ✅ | list of strings | repo-relative paths/globs | The files relevant to this doc in that repository. No absolute paths, `..` segments, or Git pathspec magic. |
| `code_references[].verified_at.commit` | ✅ | string | git SHA (quote it) | The commit in this repository when its contribution to the doc was last verified. |
| `code_references[].verified_at.date` | ✅ | string | `YYYY-MM-DD` | When that check happened. Dates may also be unquoted YAML dates. |
| `code_references[].verified_at.by` | ✅ | string | a person, or `agent` | Who verified this repository's contribution; does not automatically promote document trust. |
| `trust` | ✅ | enum | `draft` \| `agent-generated` \| `human-reviewed` | How much weight the router should give the doc. See [`staleness-convention.md`](staleness-convention.md). |

### Code references

```yaml
code_references:
  - repository: scripting-napi
    paths:
      - src/bindings/**
    verified_at:
      commit: "<sha-in-napi-repository>"
      date: 2026-10-05
      by: agent
  - repository: scripting-types
    paths:
      - types/**
    verified_at:
      commit: "<sha-in-types-repository>"
      date: 2026-10-05
      by: agent
trust: agent-generated
```

These are illustrative paths. Each repository has its own verification commit and
date; top-level `sources` and `verified_at` are not supported. `trust` remains
document-wide. A single-repository doc uses a one-entry list.

Repository IDs resolve through the [repository registry](repository-registry.md).
Hierarchy and `related` IDs are corpus-wide, not scoped to a repository, so one
architecture doc can connect components implemented in different repositories.

## Why this set and not more

The temptation is to add owner, tags, review dates, per-section metadata, and so on.
Resist it for the pilot: every required field above has a read-loop or validation
consumer, and a heavy frontmatter suppresses the demand-driven capture the
whole system depends on. Grow the schema only when a *consumer* needs a new field.

## Decisions (pilot)

- **Per-document code references, not per-claim.** Each entry covers this doc's
  relevant code in one repository. Per-claim references are deferred.
- **No generated index.** At pilot scale the router globs frontmatter directly, so
  there is no index artifact that can itself go stale. Introduce a generated index
  only when globbing gets expensive.
- **Relative-path links in prose, `id` as the router's key.** Bodies link with
  clickable relative paths; the router and cross-references use `id`.
- **Reciprocal hierarchy.** Parent and children IDs resolve within the same tree,
  with parents coarser than children. Update both ends together.
- **No write-loop metadata expansion.** Capture/verification reports remain private
  artifacts or conversation output. See [write-loop.md](write-loop.md) and
  [validation.md](validation.md).
