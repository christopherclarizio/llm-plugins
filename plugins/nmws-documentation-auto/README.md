# nmws-documentation-auto

An opt-in companion that reminds the agent to offer capture of durable findings
from the current conversation. Requires **nmws-documentation 0.4.0 or newer**,
a configured `NMWS_DOCS_CORPUS_ROOT`, and Node.js 20 or newer on `PATH`.
It does not capture findings or write corpus documents itself.

## How it works

- **SessionStart** injects a reminder to consider
  [offer-documentation-capture](../nmws-documentation/skills/offer-documentation-capture/SKILL.md)
  at natural task boundaries, including read-only investigations. This is an
  instruction-based fallback, not guaranteed completion detection.
- **PostToolUse** nudges after an observed Git commit completion summary. It
  parses hook JSON structurally, recognizes simple POSIX `git commit` commands
  (including `-C`, `-c`, quoted arguments, and `&&` sequences), and checks available
  completion status. Failed commits, interrupted or still-running results, and
  dry runs do not trigger reminders.

The skill assesses whether there is new, evidenced understanding worth preserving,
checks likely document homes, and asks a specific, brief question. Only user
acceptance invokes the existing capture workflow. Silence or unattended operation
is not consent. Corrections to existing claims retain accuracy verification's
separate exact-diff approval.

The hooks never read `transcript_path`, scan other conversations, run the received
shell command, fetch repositories, or write documentation. They do nothing when
`NMWS_DOCS_CORPUS_ROOT` is unset or empty. Directly invoking the offer skill without
configuration instead reports "documentation corpus not configured"; a user-provided
corpus root also works for direct invocation.

## Offers versus reminders

The agent tracks **actual offers** in conversation context: at most two unsolicited
offers per session, no repeat findings, and no further offers after a decline.
Explicit review or capture requests remain available. Normal compaction summaries
should retain this history; if it is unavailable after resume or compaction, the
agent suppresses unsolicited offers rather than resetting the allowance.

Separately, the commit hook emits at most **two commit reminders** per session and
deduplicates the same commit summary and working directory. Its private temporary
state contains only hashed session/commit identifiers and reminder slots, never
findings or transcripts. Exclusive file creation prevents concurrent hooks from
exceeding the reminder budget or duplicating the same reminder. State survives
resume and compaction with the same session ID; host temporary-directory cleanup
eventually removes it. The SessionStart reminder does not consume this budget.
Neither reminder count proves that the agent made an offer or that the user declined.

## Installation

Configure the corpus with nmws-documentation's **set-me-up** skill first.
Install both plugins in the host you use.

### Claude Code

```text
/plugin install nmws-documentation@llm-plugins
/plugin install nmws-documentation-auto@llm-plugins
/plugin reload
```

### Codex

```sh
codex plugin add nmws-documentation@llm-plugins
codex plugin add nmws-documentation-auto@llm-plugins
```

Review and trust the companion's hooks with `/hooks` in Codex before using them.
Claude uses `hooks/hooks.json` and `CLAUDE_PLUGIN_ROOT`; Codex uses
`hooks.codex.json` and its documented `PLUGIN_ROOT`. Both commands quote the
installed plugin path and work independently of the session working directory.
The Node.js implementation does not require Bash to launch the hook on Windows;
commit recognition still expects POSIX-style shell text.

Disable or uninstall this companion to stop automatic reminders. The base plugin's
offer and capture skills remain available on request.

## Completion checks and limitations

Claude's successful `PostToolUse` event supplies a structured Bash result with
`stdout` and `interrupted`. Codex can fire the event on failures as well; its
unified-exec hook currently supplies raw completed-command output without a
structured exit code. The hook therefore also requires Git's successful
`[branch commit-sha] subject` summary. When structured exit codes or shell status
headers are supplied, a nonzero code prevents a reminder.
Without an exit status, the summary indicates commit completion, not success of
every other command in a chained shell invocation.

Quiet commits, output truncated before the summary, wrappers, pipelines,
redirections, substitutions, and other ambiguous shell syntax may not produce
a commit nudge. The task-boundary reminder and explicit offer skill remain
available. This is a best-effort reminder, not a security gate or an audit of Git
activity. Host event and response shapes follow the
[Claude hook reference](https://code.claude.com/docs/en/hooks) and
[Codex hook reference](https://developers.openai.com/codex/hooks/).

Malformed payloads, unrecognized completion objects, and state read/write failures
produce a labeled stderr diagnostic and exit `1` without a success-shaped fallback.
The hooks never return a blocking decision, exit `2`, or register a Stop hook.

## Development

```sh
node --test plugins/nmws-documentation-auto/tests/hooks.test.mjs
```

Tests use temporary directories and local Git repositories; no remote source
access is needed. See the base plugin's
[contributor guidance](../nmws-documentation/CONTRIBUTING.md) for its Python suite.
