# Jira MCP detection

Heuristics the Emit sub-step uses to decide, at runtime, whether a Jira or
Atlassian MCP is connected and safe to use for best-effort ticket creation.

## Detection: tool-list inspection only

Detection means scanning the names of tools that are CURRENTLY AVAILABLE in
this session - nothing more. Never call a REST endpoint, never read an
environment variable looking for a token, and never ask the user for a
credential in order to decide whether Jira is connected. The presence check
is answered entirely by looking at the tool list already exposed to the
model.

- Scan the available tool names for a case-insensitive substring match on
  `jira` or `atlassian`.
- Tools exposed by a connected MCP server typically follow the shape
  `mcp__<server>__<tool>`, so a match commonly looks like
  `mcp__jira__create_issue` or `mcp__atlassian__createIssue`.
- Narrow to create/issue-style verbs for the tool that will actually be
  called to create a ticket. Example create-tool names seen in the wild:
  `createJiraIssue`, `jira_create_issue`, `atlassian_create_issue`.
- A server counts as "present" only if such a tool is actually in the
  available tool list right now, in this session. A tool that merely might
  exist, existed in a prior session, or is documented somewhere does not
  count - only what is currently listed.

If no tool name matches, treat Jira as not connected and take the no-MCP
path: no retry, no polling, no alternate discovery method.

## Never do this during detection or creation

- Never call a REST endpoint (e.g. `https://*.atlassian.net/rest/api/...`)
  directly. All interaction goes through an already-connected MCP tool call,
  never a raw HTTP request.
- Never read an environment variable, config file, or secret store looking
  for a Jira token, API key, or password.
- Never ask the user to paste a credential, token, or password. If a create
  call fails for a reason that looks like a missing credential, report the
  failure and stop - do not prompt the user for one.

## Create-issue call mapping

Map a drafted ticket file to the connected MCP's create-issue call:

| Ticket field | MCP call field |
|---|---|
| `type` (epic / story / task) | issue type |
| title | summary |
| description + acceptance-criteria bullets | description body |
| `parent` (parent ticket's slug, resolved to its Jira key) | parent / epic link, where the MCP supports one |

Field names differ across MCP implementations (an `epic_link` field on one
server may be a generic `parent` field on another). Adapt to the actual
tool's schema at call time - read its declared parameters and populate what
it accepts - rather than inventing a field the tool does not declare.

## Parents before children

Create epics (or other parent tickets) before their children:

1. Create each parent ticket first and capture the key the MCP call
   returns.
2. Create each child next, passing the captured parent key into whatever
   parent/epic-link field the MCP call accepts.

Creating a child before its parent exists leaves nothing for the parent
link to point at, so this order is not optional.

## Ambiguity: multiple candidate tools

If more than one available tool matches the Jira/Atlassian heuristics above
(for example, two different MCP servers both expose a create-issue tool, or
one server exposes both a "simple create" and a "bulk create" tool), do not
guess which one to use. Ask the user which candidate to use before making
any create call.
