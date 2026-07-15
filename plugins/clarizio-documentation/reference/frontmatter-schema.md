# Frontmatter schema — the router's contract

Every documentation file, in **both** the code tree and the product tree, opens with
the same YAML frontmatter block. This uniformity is deliberate: the `docs-router`
skill and `check_staleness.py` consume these fields, so the frontmatter is an **API**,
not decoration. The rule of thumb — **if a field is not read by the router or the
staleness check, it does not belong here.**

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
| `related` | — | list of ids | — | Cross-links. **Include the counterpart in the other tree** — the code↔product bridge. |
| `keywords` | — | list of strings | — | Extra matching signal for the router. |
| `sources` | ✅ | list of strings | repo-relative paths/globs | The code the doc's claims derive from. The staleness anchor. For product docs, these point at the **implementing** code. |
| `verified_at.commit` | ✅ | string | git SHA | HEAD of the code repo when the doc was last checked against reality. |
| `verified_at.date` | ✅ | string | `YYYY-MM-DD` | When that check happened. |
| `verified_at.by` | ✅ | string | a person, or `agent` | Who verified. A person implies human authority; `agent` means generated and unverified. |
| `trust` | ✅ | enum | `draft` \| `agent-generated` \| `human-reviewed` | How much weight the router should give the doc. See [`staleness-convention.md`](staleness-convention.md). |

## Why this set and not more

The temptation is to add owner, tags, review dates, per-section metadata, and so on.
Resist it for the pilot: every required field above is consumed by the router or the
staleness check, and a heavy frontmatter suppresses the demand-driven capture the
whole system depends on. Grow the schema only when a *consumer* needs a new field.

## Decisions (pilot)

- **Per-doc anchors, not per-claim.** `sources` covers the whole doc. Per-claim
  anchoring is more precise but too heavy for v1; revisit if a doc gets large.
- **No generated index.** At pilot scale the router globs frontmatter directly, so
  there is no index artifact that can itself go stale. Introduce a generated index
  only when globbing gets expensive.
- **Relative-path links in prose, `id` as the router's key.** Bodies link with
  clickable relative paths; the router and cross-references use `id`.
