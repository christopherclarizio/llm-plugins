---
name: set-me-up
description: Sets up nmws-documentation without manual Python or virtualenv management. Use when the user asks to set up the plugin, install its prerequisites, or configure its corpus location. Checks for uv and Git, installs missing tools when permitted, and persistently sets NMWS_DOCS_CORPUS_ROOT to the user's specified directory.
---

# set-me-up

Set up the tools and corpus location, not the documentation or source checkouts.
Resolve `PLUGIN_ROOT` from `CLAUDE_PLUGIN_ROOT` when available, otherwise from this
skill's location beneath the plugin root.

## Procedure

1. **Get the corpus path.** Use the directory explicitly provided by the user.
   If none was provided, ask for it before changing settings; an existing
   `NMWS_DOCS_CORPUS_ROOT` may be offered for confirmation, not silently selected.
   Resolve relative paths against the user's working directory, expand a leading
   `~`, and resolve the existing directory to an absolute path. Treat the path as
   data, never executable shell input. Preserve spaces, quotes, and special characters
   using shell-appropriate literal escaping. Require an existing readable directory;
   do not create one or substitute the bundled examples. Check for `code/` or
   `product/` and `repositories.yaml`; report missing corpus structure as a separate
   configuration gap rather than fabricating documents or repository entries.
2. **Inspect the platform and tools.** Determine the OS and the user's shell, not
   just the temporary command runner's shell. On Unix check `command -v uv` and
   `command -v git`; on PowerShell use `Get-Command uv` and `Get-Command git`.
   Verify available tools with `uv --version` and `git --version`. A present but
   failing executable is an error to investigate, not a reason to overwrite it.
   Preserve existing installations; do not upgrade or reinstall working tools.
3. **Install uv only if missing.** Choose one supported method:
   - macOS with existing Homebrew: `brew install uv`.
   - Windows with existing WinGet: `winget install --id astral-sh.uv --exact`.
   - Otherwise use the official standalone installer from
     [Astral's installation instructions](https://docs.astral.sh/uv/getting-started/installation/).
     On macOS/Linux, download `https://astral.sh/uv/install.sh` with
     `curl --fail --location --show-error` to a specific temporary file, inspect it,
     then execute it with `sh`. On Windows, download
     `https://astral.sh/uv/install.ps1` to a specific temporary file, inspect it,
     then run it with PowerShell under permitted execution policy.
     Delete only that downloaded file afterward. Do not use pip, install a Python
     environment, or bootstrap a second package manager to install uv.

   Respect network, installation, and privilege permissions. Request approval when
   required; never bypass execution policy, run unapproved elevation, or continue
   after a failed installer as if it succeeded. The standalone installer normally
   adds its installation directory to shell startup configuration; inspect its
   output and ensure PATH is persisted for the user's shell if it did not.
4. **Install Git only if missing.** Use the platform's existing package manager,
   choosing only the applicable command:
   - macOS with Homebrew: `brew install git`. Without Homebrew, use
     `xcode-select --install` for Apple's Command Line Tools. This can require a
     user-operated dialog; report setup as pending until installation actually
     finishes and `git --version` succeeds.
   - Debian/Ubuntu: `sudo apt-get update` then `sudo apt-get install git`.
   - Fedora/RHEL: `sudo dnf install git` (or `sudo yum install git` if dnf is absent).
   - Arch: `sudo pacman -S --needed git`.
   - openSUSE: `sudo zypper install git`.
   - Alpine: `sudo apk add git` (omit sudo if already running as root).
   - Windows with WinGet: `winget install --id Git.Git --exact`.

   For another platform or a missing package manager, report the blocker and use
   the platform's official Git installation instructions. Do not install Homebrew,
   change Git identity/authentication, or clone anything. Respect privilege approval;
   if approval is unavailable, leave the step explicitly blocked.
5. **Make tools available and verify.** New installations may not be on the command
   runner's current PATH. Use the installer's actual reported location, update PATH
   in subsequent command environments as needed, and check `uv --version` and
   `git --version` again. On Windows the current process may need an updated PATH
   or a terminal restart. Do not guess an executable path or report success based
   only on an installer exit code.
6. **Persist the user's corpus location.** Read the appropriate existing startup
   configuration before editing it. On Unix, add or update a single managed block
   delimited by `# >>> nmws-documentation >>>` and
   `# <<< nmws-documentation <<<`, containing the correctly escaped literal
   assignment. Preserve all unrelated contents and permissions; repeated setup
   must update the block rather than append duplicates.
   - zsh: use `${ZDOTDIR:-$HOME}/.zshenv` with
     `export NMWS_DOCS_CORPUS_ROOT='<absolute-path>'`.
   - bash: use `~/.bashrc` and the active login file (the first existing of
     `~/.bash_profile`, `~/.bash_login`, `~/.profile`, otherwise create
     `~/.bash_profile`). Set `export NMWS_DOCS_CORPUS_ROOT='<absolute-path>'`
     in both, unless the login file already sources `.bashrc`.
   - fish: use `$XDG_CONFIG_HOME/fish/conf.d/nmws-documentation.fish`
     (default `~/.config/fish/conf.d/nmws-documentation.fish`) with
     `set -gx NMWS_DOCS_CORPUS_ROOT '<absolute-path>'`.
   - Windows: use PowerShell
     `[Environment]::SetEnvironmentVariable('NMWS_DOCS_CORPUS_ROOT', '<absolute-path>', 'User')`
     and `$env:NMWS_DOCS_CORPUS_ROOT = '<absolute-path>'` for the current process.
     Use PowerShell literal escaping rather than Unix escaping.

   The examples above use placeholders: generate a literal appropriate for the
   actual path, including embedded quotes. If another startup assignment would
   override this setting, surface the conflict and get approval before changing
   unmanaged configuration. For an unsupported shell, ask how the user wants the
   variable persisted instead of writing bash syntax into its configuration.

   An export inside a tool subprocess cannot update the parent agent's environment.
   Until restart, pass `NMWS_DOCS_CORPUS_ROOT` explicitly in subsequent tool
   environments (or use the chosen absolute path in corpus arguments). Do not claim
   that a one-off export makes the setting available to the already-running agent.
7. **Verify and report accurately.** Check that the persisted setting matches the
   resolved directory: on Unix, start a fresh instance of the user's shell and
   print the variable, covering login and interactive startup where applicable.
   On Windows, read it back with
   `[Environment]::GetEnvironmentVariable('NMWS_DOCS_CORPUS_ROOT', 'User')`.
   Do not log unrelated environment variables or shell configuration contents.
   Check the uv-managed helpers without refreshing checkouts:
   ```sh
   uv run --locked --script "${PLUGIN_ROOT}/skills/retrieve-relevant-documentation/scripts/check_staleness.py" --help
   uv run --locked --script "${PLUGIN_ROOT}/skills/retrieve-relevant-documentation/scripts/refresh_repositories.py" --help
   uv run --locked --script "${PLUGIN_ROOT}/skills/retrieve-relevant-documentation/scripts/validate_docs.py" --help
   ```
   These commands also provision the isolated Python dependencies and may download
   Python/packages. Report failed downloads explicitly; do not fall back to pip or
   skip checks. Report tool versions, the exact corpus path, where the setting was
   saved, outstanding corpus/configuration gaps, and whether a terminal/agent restart
   is needed. A pending installer or failed check means setup is not complete.

## Boundaries

Do not modify corpus documents, create repository configuration, refresh or repair
checkouts, or commit anything. Setup permission does not authorize those operations.
Helpers manage their own Python environments through uv; no `.venv`, dependency
installation, or project setup should be added to the user's working repository.
