# Repository registry

Keep `repositories.yaml` at the documentation corpus root. Repository IDs are stable;
checkout paths are developer-specific. This file configures existing checkouts, not
automatic cloning or remote API access.

```yaml
repositories:
  scripting-napi:
    remote: https://example.invalid/team/scripting-napi.git
    authoritative_branch: main
    local: ../scripting-napi
  scripting-types:
    remote: https://example.invalid/team/scripting-types.git
    authoritative_branch: main
    local: ../scripting-types
  scripting-gateway:
    remote: https://example.invalid/team/scripting-gateway.git
    authoritative_branch: main
    local: ../scripting-gateway
```

These URLs and paths are illustrative. Replace them with real repositories before use.
Each entry requires exactly `remote`, `authoritative_branch`, and `local`:

- `remote`: canonical repository URL, matching a fetch URL reported by
  `git remote get-url` in the selected checkout. Use the same URL spelling; the helper
  does not equate SSH and HTTPS URLs. Git's existing authentication handles access.
  Do not include credentials in the registry.
- `authoritative_branch`: normally `main`; this branch is the documentation baseline.
- `local`: path to an existing checkout root (including a linked Git worktree).
  Relative paths resolve against this configuration file's directory. Absolute paths
  and `~` paths are supported; environment-variable expansion is not.

If you have multiple checkouts of the same repository, `local` selects exactly one.
Use a clean checkout on the authoritative branch for documentation lookup and keep
feature work in another checkout. The plugin does not search other checkouts or
switch branches.

## Local overrides

Optionally create `repositories.local.yaml` at the corpus root:

```yaml
repositories:
  scripting-napi:
    local: /Users/developer/checkouts/scripting-napi-main
```

An override may change only `local` for an existing ID, not the remote or branch.
Relative paths resolve against the override file's directory. Add the override file
to the **corpus repository's** `.gitignore`; do not commit personal paths. The router
passes it as `--override` if it exists. Other locations can be passed explicitly.

## Refresh behavior

The registry-mode staleness checker refreshes each needed repository once per batch
of documents. It validates the checkout root, remote, branch, and clean state, then
fetches the configured branch and fast-forwards the local branch to the fetched
commit. No merge commits, resets, rebases, stashes, branch switches, or automatic
clones are performed. Untracked files count as dirty.

A wrong branch, detached HEAD, dirty checkout, local-only/divergent commits, missing
checkout, or fetch failure is an explicit error. Other repositories are still checked.
Fetching can update Git objects even when a later fast-forward check fails, but
failed safety checks do not intentionally change the branch or working files.

Successful refresh prints the resulting SHA. It is retained only in process memory
and tool/conversation output, not written to a snapshot file, registry, or doc.
Ordinary Git fetch/fast-forward operations still update Git's own metadata.

For checkout maintenance without checking documents:

```sh
uv run --locked --script <plugin-root>/skills/retrieve-relevant-documentation/scripts/refresh_repositories.py \
  scripting-napi scripting-types scripting-gateway \
  --registry <corpus-root>/repositories.yaml
```

Exit `0` means all requested repositories were refreshed; `2` means at least one
failed. The documentation checker already performs this step, so do not run both
helpers for the same lookup.

The checkout matched upstream when fetched; it is not continuously synchronized.
Assume it remains unchanged while reading code. If it changes, rerun the lookup.
Fetch requires network/authentication permission; if unavailable, report
**not confirmed current**, not an unqualified fresh result. Do not bypass permission
restrictions or repair a developer's checkout automatically.
