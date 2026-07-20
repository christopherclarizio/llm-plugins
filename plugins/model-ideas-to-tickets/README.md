# model-ideas-to-tickets

Turn rough, half-formed ideas into concise, well-organized Jira tickets that stay
honest about the actual state of your codebase.

This plugin ships a single orchestrator **skill** (`model-ideas-to-tickets`) that runs
identically in Claude Code and Codex. It walks five stages:

1. **Intake** - gather the raw idea(s) and confirm which repo(s) to ground against.
2. **Refine** - a lightweight clarification loop that resolves contradictions and
   settles a per-idea "done".
3. **Ground** - a quick, honest feasibility scan against the codebase (already
   implemented? still needed? do the landing assumptions hold?).
4. **Structure** - break each surviving idea into a concise ticket hierarchy
   (flat, or epic -> story only when warranted), ordered by dependency.
5. **Verify and Emit** - verify each ticket's specifics against the code, write one
   Markdown file per ticket plus an index, then offer best-effort Jira creation.

## Output

Tickets are written **files-first** to a run-scoped directory
(`./tickets/<date>-<batch-slug>/`), one Markdown file per ticket plus a `README.md`
index. Each ticket carries YAML front-matter (`type`, `parent`, `key`) so hierarchy
and Jira mapping survive.

## Example

Say you give it two ideas at once:

> 1. Build a notifications center: in-app notifications for comments and mentions,
>    plus a settings page to control which types you get and whether they're emailed.
> 2. Add an unread-count badge on the header bell icon.

The skill splits these into separate intake items, grounds each against your repo,
and structures them independently - idea 1 is large enough to become an epic with
child stories, idea 2 stays a single flat ticket. Because the badge (idea 2) can't
count notifications that don't exist yet, it's ordered after idea 1's tickets in
both the file listing and the README index:

```
tickets/2026-07-21-notifications/
  epic-notifications-center.md
  story-notification-delivery.md
  story-notification-settings.md
  task-unread-badge.md
  README.md
```

`README.md` in that run directory ties the tree together with a one-line summary
per ticket and any grounding caveats:

```markdown
# notifications tickets (2026-07-21)

- epic-notifications-center.md - Build a notifications center: in-app delivery
  plus a settings page for types and email.
  - story-notification-delivery.md - Deliver in-app notifications for comments
    and mentions.
  - story-notification-settings.md - Let users toggle notification types and
    email delivery.
- task-unread-badge.md - Show an unread-count badge on the header bell icon;
  depends on story-notification-delivery's data existing.

Jira: no Jira/Atlassian MCP detected. Create these manually in the order listed
above (epic before its stories, badge task last).
```

Each `.md` file carries `type` and `key` front-matter, plus `parent` for tickets
that sit under an epic (top-level tickets omit it), so the hierarchy and any later
Jira key survive as plain text even before a ticket is ever created in Jira. A single
ticket file looks like this (here, the flat badge task):

```markdown
---
type: task
key:
---

# Show an unread-count badge on the header bell icon

Display a live unread-notification count on the header bell. The badge reads from the
in-app notification store and clears when the user opens the notifications center.

## Acceptance criteria

- The bell shows a numeric badge when unread notifications exist, and none when zero.
- Opening the notifications center marks them read and clears the badge.
```

A child story would instead carry `type: story` and `parent: notifications-center`;
the epic carries `type: epic`.

## Jira creation (best-effort)

At emit time the skill checks whether a Jira/Atlassian MCP is connected. If one is,
it offers to create the tickets (parents before children) and writes the returned
issue keys back into the files. If none is connected, the files are the deliverable
and manual-creation guidance is shown. There is no REST integration and no credential
handling.

## Install

Install from the `llm-plugins` marketplace (Claude Code) or the LLM Agent Plugins
marketplace (Codex).

## Usage

- Claude Code: run `/model-ideas-to-tickets` (or just describe your ideas and ask for
  tickets).
- Codex: invoke the `model-ideas-to-tickets` skill directly.

## Optional enhancement

If `ed3d-research-agents` is installed, the grounding stage may delegate a deeper
codebase dive to its `codebase-investigator` agent. This is a soft dependency: the
skill works fully with only built-in tools.
