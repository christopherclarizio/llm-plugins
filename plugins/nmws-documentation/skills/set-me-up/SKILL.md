---
name: set-me-up
description: Configures the nmws-documentation corpus location and installs missing Git/uv prerequisites when permitted. Use when the user asks to set up the plugin or configure its corpus. Does not create documentation or configure source repositories.
---

# Set up nmws-documentation

Prepare tools and the corpus location, not documents or source checkouts.

## Workflow

1. **Confirm the corpus.** Use a user-provided directory; if none was provided,
   ask before changing settings. An existing `NMWS_DOCS_CORPUS_ROOT` may be offered
   for confirmation, not silently selected. Expand a leading `~`, resolve relative
   paths against the user's working directory, and require an existing readable
   directory. Report missing `code/` or `product/` and `repositories.yaml` as
   configuration gaps; do not create or substitute them.
2. **Inspect the environment.** Identify the OS and user's shell, not just the
   command runner's shell. Follow only the applicable sections of
   [Unix setup](../../reference/setup-unix.md) or
   [Windows setup](../../reference/setup-windows.md). Check Git and uv, preserving
   working installations. Investigate failing executables instead of overwriting them.
3. **Install missing tools.** Use the platform reference and existing package
   manager or official installer. Respect network, installation, and privilege
   permissions. Verify executable versions after installation; pending dialogs,
   failed downloads, or unavailable approval leave setup incomplete.
4. **Persist the corpus path.** Read existing settings and use the platform
   reference's managed configuration. Treat paths as literal data, preserving
   spaces, quotes, and special characters. Keep unrelated contents and permissions;
   repeated setup must update rather than duplicate settings. Get approval before
   changing conflicting unmanaged settings; ask for unsupported-shell instructions.
5. **Confirm readiness.** Verify the persisted value from a fresh shell or Windows
   user environment, and run all four [helpers](../../reference/helpers.md) with
   `--help`. Report tool versions, corpus path, settings location, remaining gaps,
   and any required restart. Do not report complete setup while checks are pending.

## Boundaries

A subprocess export cannot change the parent agent's environment. Until restart,
pass the chosen path explicitly to subsequent commands. Do not print unrelated
environment variables or shell configuration.

Do not create a corpus, configure/clone/refresh source repositories, commit, or
change Git identity/authentication. Do not install project dependencies or create
a `.venv`; helpers use isolated uv-managed environments.
