# Unix setup

Read only the applicable tool-installation and shell-configuration sections.
The setup skill handles corpus selection, permissions, and final reporting.

## Contents

- [Inspect tools](#inspect-tools)
- [macOS tools](#macos-tools)
- [Linux tools](#linux-tools)
- [Standalone uv installer](#standalone-uv-installer)
- [Persist the corpus path](#persist-the-corpus-path)
- [Confirm persistence](#confirm-persistence)

## Inspect tools

Check `command -v uv` and `command -v git`, then verify present executables with
`uv --version` and `git --version`. Preserve working installations; a failing
executable needs investigation, not automatic replacement.

## macOS tools

With existing Homebrew, install only missing tools using `brew install uv` or
`brew install git`. Do not bootstrap Homebrew.

Without Homebrew, use the standalone uv installer below. For missing Git, use
`xcode-select --install`. A user-operated dialog may be required; report setup
pending until installation finishes and `git --version` succeeds.

## Linux tools

For missing uv, use the standalone installer below. For missing Git, use the
existing package manager for the distribution:

| Distribution | Command |
| --- | --- |
| Debian/Ubuntu | `sudo apt-get update`, then `sudo apt-get install git` |
| Fedora/RHEL | `sudo dnf install git`, or `sudo yum install git` if dnf is absent |
| Arch | `sudo pacman -S --needed git` |
| openSUSE | `sudo zypper install git` |
| Alpine | `sudo apk add git` |

Omit sudo when already running as root. Respect privilege approval; if unavailable,
report the blocker. For other distributions or missing package managers, use the
platform's official Git instructions rather than installing a new package manager.

## Standalone uv installer

Follow [Astral's installation instructions](https://docs.astral.sh/uv/getting-started/installation/).
Download `https://astral.sh/uv/install.sh` with
`curl --fail --location --show-error` to a specific temporary file, inspect it, then
execute it with `sh` when permitted. Delete only that downloaded file afterward.
Do not use pip, install a Python environment, or bootstrap another package manager.

Use the installer's reported executable location to make uv available to subsequent
commands. Inspect whether it persisted PATH for the user's shell and correct that
only when necessary. Verify `uv --version` and `git --version` after installation;
an installer exit code alone is not proof that the tools work.

## Persist the corpus path

Read the user's existing configuration before editing. Use a single managed block
delimited by `# >>> nmws-documentation >>>` and
`# <<< nmws-documentation <<<`; update it on repeated setup.
Preserve unrelated contents and permissions. Surface conflicting unmanaged assignments
and obtain approval before changing them.

The following are literal-assignment templates. Escape the actual absolute path for
the user's shell, including embedded quotes; never treat the path as executable input.

| Shell | Location | Assignment |
| --- | --- | --- |
| zsh | `${ZDOTDIR:-$HOME}/.zshenv` | `export NMWS_DOCS_CORPUS_ROOT='<absolute-path>'` |
| bash | `~/.bashrc` and active login file | `export NMWS_DOCS_CORPUS_ROOT='<absolute-path>'` |
| fish | `$XDG_CONFIG_HOME/fish/conf.d/nmws-documentation.fish`, defaulting to `~/.config/fish/conf.d/nmws-documentation.fish` | `set -gx NMWS_DOCS_CORPUS_ROOT '<absolute-path>'` |

For bash, the active login file is the first existing of `~/.bash_profile`,
`~/.bash_login`, and `~/.profile`; otherwise create `~/.bash_profile`.
Set the variable in both files unless the login file already sources `.bashrc`.
For an unsupported shell, ask how the user wants persistence configured.

## Confirm persistence

Start a fresh instance of the user's shell and print only `NMWS_DOCS_CORPUS_ROOT`,
covering login and interactive startup where applicable. Verify it matches the
resolved readable directory. A temporary export does not change the parent agent's
environment; use explicit command arguments/environments until restart.
