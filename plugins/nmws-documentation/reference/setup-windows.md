# Windows setup

Use PowerShell syntax and literal escaping for paths, including embedded quotes.
The setup skill handles corpus selection, permissions, and final reporting.

## Inspect and install tools

Use `Get-Command uv` and `Get-Command git`, then verify present tools with
`uv --version` and `git --version`. Preserve working installations; investigate
failing executables rather than replacing them.

With existing WinGet, install only missing tools:

```powershell
winget install --id astral-sh.uv --exact
winget install --id Git.Git --exact
```

Without WinGet, follow
[Astral's standalone installation instructions](https://docs.astral.sh/uv/getting-started/installation/).
Download `https://astral.sh/uv/install.ps1` to a specific temporary file, inspect it,
then execute it with PowerShell under permitted execution policy. Delete only that
downloaded file afterward. Do not bypass policy, run unapproved elevation, use pip,
or bootstrap another package manager.

For missing Git without a package manager, use the
[official Windows instructions](https://git-scm.com/downloads/win) and report any
required user interaction as pending.

Use actual installer output to locate executables and verify persistent PATH.
Update the command environment if needed; a terminal restart may be required.
Check `uv --version` and `git --version` again rather than relying on installer
exit codes.

## Persist and confirm the corpus path

Read the existing user value before changing it. Set the resolved absolute path
as a literal, using PowerShell escaping for the actual path:

```powershell
[Environment]::SetEnvironmentVariable('NMWS_DOCS_CORPUS_ROOT', '<absolute-path>', 'User')
$env:NMWS_DOCS_CORPUS_ROOT = '<absolute-path>'
```

Read it back with:

```powershell
[Environment]::GetEnvironmentVariable('NMWS_DOCS_CORPUS_ROOT', 'User')
```

Confirm the stored value matches the selected readable directory. The current
subprocess assignment does not update the parent agent; pass the path explicitly
until restart. Print no unrelated environment variables.
