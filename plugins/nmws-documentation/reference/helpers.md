# Helper commands

Use these commands for deterministic discovery, freshness checks, and validation.
Load only the section needed for the current operation.

## Contents

- [Execution](#execution)
- [Discover documents](#discover-documents)
- [Check freshness](#check-freshness)
- [Refresh source for grounding](#refresh-source-for-grounding)
- [Validate structure](#validate-structure)
- [Confirm helper availability](#confirm-helper-availability)

## Execution

Resolve `PLUGIN_ROOT` from `CLAUDE_PLUGIN_ROOT` when available; otherwise derive it
from the loaded skill's location beneath `<plugin-root>/skills/<skill-name>/`.
Use the corpus root selected by the skill, never the bundled examples as a fallback.

Run executable helpers with `uv run --locked --script`. uv provisions compatible
Python and locked dependencies in an isolated cache, without pip, manual virtualenvs,
or changes to the user's Python project. Initial use may need network access.
Missing tools, denied permissions, and failed downloads are explicit failures,
not permission to skip a check. Use `set-me-up` if prerequisites are missing.

The commands below use POSIX shell syntax and placeholders. Supply actual paths
as quoted literal arguments; adapt quoting and continuation for PowerShell.
Do not assume an environment assignment in one tool subprocess survives into another.

## Discover documents

```sh
uv run --locked --script "${PLUGIN_ROOT}/skills/retrieve-relevant-documentation/scripts/discover_docs.py" \
  --corpus-root "<corpus-root>" --query "<task question or component>" --mode focused --limit 5
```

Use `focused` for narrow questions and `--mode orientation` for broad introductions.
Query-free orientation finds entry points. `--tree code` or `--tree product` limits
the tree; `--id <document-id>` resolves navigation links.

Focused ranking prefers exact ID/title/keyword matches, then query-term coverage
and weighted field matches; finer tiers break relevance ties. Orientation prefers
coarser tiers among matches. Ranking is lexical and advisory: refine weak queries
and choose candidates for the actual task.

JSON returns corpus-relative paths, routing metadata, navigation IDs, match evidence,
scanned/matched counts, and `truncated`. Default limit is 5; maximum is 20.
The local metadata scan is linear in corpus size, but only the shortlist enters
model context. No bodies, saved index, repository access, or freshness assertions.

Exit `0` includes an empty shortlist. Exit `2` reports a read/configuration/metadata
error in JSON and stderr; it is not evidence of a coverage gap.

## Check freshness

```sh
uv run --locked --script "${PLUGIN_ROOT}/skills/retrieve-relevant-documentation/scripts/check_staleness.py" \
  "<doc-path>" "<other-loaded-doc-path>" --registry "<corpus-root>/repositories.yaml"
```

Pass one or more documents. Add
`--override "<corpus-root>/repositories.local.yaml"` if that file exists.
Each referenced repository is refreshed once for the batch, so do not run the
refresh helper separately for the same lookup.

| Exit | Meaning |
| --- | --- |
| `0` | All references checked; no detected drift. |
| `1` | All references checked; at least one is potentially stale. |
| `2` | A reference or refresh failed; results are incomplete. |

Errors take precedence over staleness, but known per-repository results remain
useful. A failed refresh means **not confirmed current**, never fresh.
Report trust separately: no detected drift does not prove correctness.

## Refresh source for grounding

```sh
uv run --locked --script "${PLUGIN_ROOT}/skills/retrieve-relevant-documentation/scripts/refresh_repositories.py" \
  <repository-id> <other-id> --registry "<corpus-root>/repositories.yaml"
```

Pass one or more repository IDs and the local override when present.
Exit `0` means all requested repositories refreshed; `2` means at least one failed.

Both refresh and freshness helpers validate the configured checkout root, remote,
authoritative branch, and clean state, then fetch and fast-forward only.
They never switch branches, reset, stash, rebase, discard edits, or clone a repair
checkout. Missing access/configuration is a gap, not permission to guess another
checkout or bypass authentication/network restrictions.

Reuse session SHAs only while HEAD and clean state remain unchanged. Rerun if
checkouts change during source reads. Keep checked SHAs in tool/conversation output,
not saved lookup snapshots; refreshing does not advance document metadata or
establish release compatibility between independently updated repositories.

## Validate structure

```sh
uv run --locked --script "${PLUGIN_ROOT}/skills/retrieve-relevant-documentation/scripts/validate_docs.py" \
  --corpus-root "<corpus-root>"
```

The default registry is `<corpus-root>/repositories.yaml`; `--registry` selects
another file. Local overrides are unnecessary because validation does not access
source checkouts, Git, or the network. uv dependency provisioning can still need
downloads.

Exit `0` means no structural errors, `1` means invalid documents, and `2` means
configuration/read/dependency failure. Warnings are heuristics; review them
manually. `--strict` makes warnings fail CI when that policy is intentional.

## Confirm helper availability

Run each command with `--help`; this provisions dependencies without accessing
source repositories:

```sh
uv run --locked --script "${PLUGIN_ROOT}/skills/retrieve-relevant-documentation/scripts/discover_docs.py" --help
uv run --locked --script "${PLUGIN_ROOT}/skills/retrieve-relevant-documentation/scripts/check_staleness.py" --help
uv run --locked --script "${PLUGIN_ROOT}/skills/retrieve-relevant-documentation/scripts/refresh_repositories.py" --help
uv run --locked --script "${PLUGIN_ROOT}/skills/retrieve-relevant-documentation/scripts/validate_docs.py" --help
```
