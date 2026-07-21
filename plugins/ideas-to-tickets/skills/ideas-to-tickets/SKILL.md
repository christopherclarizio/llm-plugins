---
name: ideas-to-tickets
description: Use when the user has one or more rough, half-formed ideas they want turned into concise, well-organized Jira tickets that stay honest about the actual state of the codebase. Runs a staged orchestrator (intake, refine, ground, structure, verify and emit) that writes one Markdown ticket per file and offers best-effort Jira creation only when a Jira/Atlassian MCP is connected.
---

# ideas-to-tickets

Convert rough idea(s) into concise, codebase-grounded Jira tickets through five stages:
Intake -> Refine -> Ground -> Structure -> Verify and Emit.

Announce at the start: "I'm using the ideas-to-tickets skill to turn your idea(s)
into tickets."

Create a five-item task/todo tracker for the stages below, using whatever task tooling
the current host provides (Claude Code or Codex). Mark each stage in progress, then
complete, as you reach it. The flow can loop backward: a failed grounding check in
Stage 3 can send an idea back to Stage 1 or Stage 2 for another pass, so leave earlier
stages re-enterable rather than treating them as one-shot.

## Stage 1: Intake

Gather every idea and the codebase scope needed to ground them later.

- **Capture each idea distinctly.** A single freeform idea becomes one intake item.
  When the user gives several ideas together (a list, or multiple paragraphs), split
  them into separate, individually-labeled intake items instead of merging them into
  one blob. Each item keeps its own text, scope, and later refinement state.
- **Follow file/notes pointers.** If an idea references a file or notes path (an
  `@path` mention, "see notes.md", or any path-like string), read that file and fold
  its content into the idea before moving on. If the path cannot be read, say so and
  ask the user for the content directly rather than guessing at it.
- **Confirm codebase scope.** Ask which repository root(s) to ground the ideas
  against, unless the user already named some. If the user names none, default to the
  current working directory's repo and state that default explicitly. If the user
  names additional roots, the grounding scope is the current working directory's repo
  plus every named root; echo that complete list of roots back so the user can correct
  it.
- **Note Jira MCP presence (informational only).** Check whether a Jira/Atlassian MCP
  appears connected and note it as a heads-up for the Emit stage; do not act on it here.
  This note is only a heads-up, not a cached result: Emit re-detects the MCP fresh at
  emit time and relies on that check, not on this note.
- **Record before advancing.** Write the captured ideas and the confirmed scope into
  the tracker or working notes before moving to Stage 2.

## Stage 2: Refine

Turn each captured idea into ticket-ready intent with a light clarification pass. This
is deliberately shallower than `ed3d-plan-and-execute`'s brainstorming: a few
well-chosen questions per idea, not an exhaustive interrogation.

- **Clarify per idea.** For each intake item, ask targeted questions that pin down its
  scope and settle a concrete, per-idea "done" (what result makes this idea complete).
  Prefer `AskUserQuestion` for discrete choices; when it is unavailable (Codex), fall
  back to asking the same questions in plain prose.
- **Reconcile contradictions before structuring.** If an idea contains two
  requirements that conflict, surface the contradiction explicitly and have the user
  reconcile it. Do not silently pick one side.
- **Blocking-ambiguity gate.** Do not advance an idea to Stage 3 (Ground) or Stage 4
  (Structure) while a blocking ambiguity remains unresolved for it, since structuring
  an idea whose scope, "done", or a core requirement is still undefined produces a
  ticket that will need to be redone. A non-blocking uncertainty (a detail that will
  not change the shape of the ticket) can carry forward as a noted assumption instead
  of stopping the flow; a blocking one (unclear scope, a contradictory core
  requirement, or no stated "done") must be resolved first.
- **Record before advancing.** On completion, each surviving idea has a clear scope, a
  stated "done", and no unresolved blocking ambiguity; record this in the tracker.

## Codebase grounding

Stage 3 and the Stage 5 per-ticket verification sub-step both ground claims against
the codebase scope from Stage 1. This section is the shared mechanism both stages
apply, at different scopes (Stage 3 scans per idea; Stage 5 checks per ticket claim).

**Default mechanism (always available).** Use `Glob` to map the relevant part of the
repo structure, `Grep` for the symbols/features/strings the claim names, and `Read` to
confirm any hit in context before treating it as evidence. This built-in path needs no
plugin beyond the host's own tools, so it is always available and is the default.

**Optional delegate.** If `ed3d-research-agents:codebase-investigator` is available as
a subagent type in the current host, dispatch it (`subagent_type:
ed3d-research-agents:codebase-investigator`) for a deeper dive instead of doing the
Glob/Grep/Read pass by hand. This is a soft dependency: check availability first, and
if it is not present, fall back to the built-in mechanism silently, with no error and
no interruption to the flow. Never claim to have delegated to it when the built-in
path was actually used.

**Honesty rules (hard rules, apply to every grounding claim):**

- A search that finds nothing is reported as **"not found"** - the searched scope
  produced no evidence. Never report a miss as **"does not exist"**; that overclaims
  certainty a local search cannot provide. "Searched X, Y, Z and found no matches" is
  honest phrasing; "the codebase has no X" is not, and must not appear in grounding
  output.
- Cite `file:line` wherever a claim rests on code actually read. A claim without a
  citation is a guess, not a grounding result.
- State confidence explicitly rather than implying it through phrasing. Say what was
  searched and what was found (or not found); do not round a partial search up to a
  universal claim.
- Grounding surfaces evidence; it does not decide. Present conflicts and let the user
  choose keep/drop/adjust per idea or ticket. Never unilaterally delete an idea or
  ticket based on a grounding result.

## Stage 3: Ground (up-front, light)

For each idea that passed Stage 2, run a quick scan against the codebase scope from
Stage 1 using the shared mechanism above. Answer three cheap questions per idea:

1. **Already implemented?** Search for the feature, symbols, or behavior the idea
   describes. If found, flag the idea "may not be needed" and cite `file:line`
   (ideas-to-tickets.AC3.1).
2. **Still needed?** Note anything the search turns up suggesting the idea is
   obsolete or already superseded by other work.
3. **Do the landing assumptions hold?** Check that the files or modules the idea
   assumes it will touch actually exist and look as assumed.

Report results honestly per the honesty rules above: a clean search that turns up
nothing is "not found," not proof the feature is absent. Then surface any conflicts to
the user and let them decide, per idea: drop, adjust, or keep with a note. An idea with
no conflicting evidence passes the scan as genuinely novel and proceeds to Stage 4
(ideas-to-tickets.AC3.2).

If grounding invalidates an idea's premise (the "done" no longer makes sense, or a
core assumption is false), loop that idea back to Stage 1 or Stage 2 rather than
forcing it forward; other ideas continue independently.

## Stage 4: Structure

For each idea that survived Stage 3, decide a ticket hierarchy for that idea alone.
The decision is per-idea, so a single batch commonly mixes flat and hierarchical
results (AC4.4) - a small fix next to a large redesign should not be forced into the
same shape.

- **Flat (default for small ideas).** One or a few sibling tickets, no epic. Use this
  unless the idea is genuinely large; most ideas land here (AC4.1).
- **Epic -> story (larger ideas).** One epic ticket plus child stories. Each child's
  front-matter sets `parent: <epic-slug>` to the epic's slug, so the link survives as
  plain text even before any Jira key exists (AC4.2).
- **Deeper only when warranted.** Do not force a third level. A story earns sub-tasks
  only when it holds several genuinely separable units of work that different people
  could pick up in parallel; if it is really one coherent chunk, keep it a single
  story. When a story keeps sprouting sub-tasks, that usually means it should have been
  its own epic, so promote it rather than nesting a third level.

Set each ticket's `type` from its place in the hierarchy: a flat, top-level ticket
(no `parent`) uses `type: task`; the top of an epic->story tree uses `type: epic`; a
child under an epic uses `type: story`. This keeps the Jira issue-type mapping at emit
time unambiguous.

Once each idea's tickets are drafted, **order all tickets in the batch so dependencies
precede dependents** (AC4.3): if ticket B needs ticket A, A comes first. Represent this
ordering two ways so both a human skimming files and the emit step reading the index
see it consistently:

- **Filenames/index order.** Assign tickets in dependency order when naming or listing
  them, so a directory listing or the README's ticket list reads top-to-bottom in the
  order work should happen.
- **Parents before children.** An epic is listed and named before its child stories,
  since a story implicitly depends on its epic existing.

Every ticket is generated from the template at
`${CLAUDE_PLUGIN_ROOT}/templates/ticket.template.md`, whose front-matter contract is
exactly `type` (`epic | story | task`), `parent` (the parent ticket's slug, omitted
entirely for top-level tickets), and `key` (blank until the ticket is created in Jira).
Ticket content stays concise regardless of hierarchy: a title, a 2-4 sentence
description, and a few acceptance-criteria bullets. Add the template's adaptive
Context / Implementation-notes sections only when the idea's complexity or the
grounding findings actually warrant them (AC5.2), and never add story points,
components, or priority - those stay out of scope in every ticket (AC5.4).

## Stage 5: Verify and Emit

### Per-ticket verification

Once a ticket is drafted, verify it before it is emitted. This check is narrower than
Stage 3: instead of scanning per idea, check each drafted ticket's specific claims and
acceptance-criteria bullets against the code, using the same shared mechanism above.

When a ticket's claim contradicts the code - for example, the ticket says "add field
Y" but Y already exists at some `file:line` - either **adjust** the ticket (rewrite the
claim to match reality) or **annotate** it with the finding and its citation
(ideas-to-tickets.AC3.3). Do not emit a ticket whose premise the code contradicts
without at least annotating it; a silently wrong ticket is worse than one flagged for
the user to resolve.

Apply the same honesty rules as Stage 3: cite `file:line` for anything read, and report
a clean miss as "not found," never "does not exist."

This sub-step runs before any ticket file is written; the emit sub-step below is what
actually writes ticket files.

### Emit

1. **Write files first.** Generate every ticket file and the run's `README.md` using
   the File-layout rules below. Confirm to the user the run directory path and the
   files written. This step alone is the guaranteed deliverable: it happens whether or
   not Jira is reachable, and nothing later in this sub-step can undo it.
2. **Detect a Jira MCP.** Follow the detection heuristics in
   `${CLAUDE_PLUGIN_ROOT}/reference/jira-mcp-detection.md` (scan currently available
   tool names; never call a REST endpoint, read env vars for tokens, or ask for
   credentials). That reference file is the source of truth for how detection and
   creation calls work - do not re-derive or inline the heuristics here.
3. **No-MCP path.** If detection finds no matching tool, say plainly that no
   Jira/Atlassian MCP is connected, point back to the files just written, and give
   manual-creation guidance: create parents (epics) before their children, and create
   any ticket a `parent` field depends on before that child. Make no API attempt of any
   kind and never ask the user for a credential.
4. **MCP-present path: offer creation.** If detection finds a matching tool, offer to
   create tickets before touching it: use `AskUserQuestion` with choices all / choose /
   skip (when `AskUserQuestion` is unavailable, as in Codex, ask the same three-way
   choice in plain prose). Creation proceeds only on the user's explicit confirmation;
   "skip" or no response leaves the written files as the only output, same as the
   no-MCP path.
5. **Idempotency guard.** Before creating anything, check each ticket file's `key:`
   front-matter. A ticket that already carries a non-empty `key:` was already created in
   a prior run, so skip it - do not create a duplicate issue - unless the user
   explicitly asks to force re-creation of that ticket. State this guard to the user
   (for example, when reporting which tickets were skipped) so a re-run's behavior is
   never a surprise.
6. **Parents before children, with write-back.** Among the tickets confirmed for
   creation, create every epic/parent first and capture the key each create call
   returns, then create children next, passing the captured parent key into whatever
   parent/epic-link field the MCP call accepts (see the field-mapping table in
   `${CLAUDE_PLUGIN_ROOT}/reference/jira-mcp-detection.md`). Immediately after each successful create call,
   write the returned key back into that ticket's own `key:` front-matter field and add
   it next to that ticket's entry in the run's `README.md`, so the two stay in sync as
   creation proceeds rather than only at the end.
7. **Per-ticket failure handling.** If a single create call fails, report which ticket
   failed and why, then continue creating the remaining tickets where doing so still
   makes sense (for example, keep creating sibling stories under an epic that already
   has a key; do not attempt a child whose specific parent failed to get a key). A
   creation failure never deletes, truncates, or otherwise corrupts the ticket files or
   the index - the files written in step 1 remain intact and are still the deliverable
   even when Jira creation is partial or fully unavailable.

The skill never calls a REST endpoint or requests a Jira credential, in the no-MCP path
above or the MCP-present path here - every Jira interaction, if one happens at all,
goes through an already-connected MCP tool call.

## File layout

Once verification passes, each ticket becomes one Markdown file in a run-scoped
directory, with a generated index. The rules below define that layout; the Emit
sub-step above is what applies them.

- **Run-scoped directory.** Default `./tickets/<YYYY-MM-DD>-<batch-slug>/`, where
  `<batch-slug>` is derived from the batch of ideas (for example, its shared theme or
  the user's own name for it). This default is configurable; if the user names a
  different location, write there instead.
- **Non-destructive (AC5.5).** A second run must write to a distinct run-scoped
  directory and must never overwrite a prior run's directory implicitly. If the target
  directory already exists, disambiguate it (append `-2`, or another short suffix)
  rather than write into or over it.
- **One file per ticket.** The filename encodes type and slug: `epic-<slug>.md`,
  `story-<slug>.md`, `task-<slug>.md`. A flat idea (Stage 4) has no epic, so it omits
  the epic file entirely.
- **Each ticket file** is generated from `${CLAUDE_PLUGIN_ROOT}/templates/ticket.template.md`
  (Task 1): front-matter (`type`, `parent`, `key`), a title, a 2-4 sentence description,
  and a few acceptance-criteria bullets (AC5.1), plus the adaptive Context /
  Implementation-notes sections only when warranted (AC5.2).
- **Generated index `README.md`** in the run directory (AC5.3): a tree of the tickets
  showing the hierarchy (epics with their child stories nested under them), a one-line
  summary per ticket, and any grounding caveats surfaced in Stage 3 or the Stage 5
  per-ticket verification (for example, "story-search-cache: partially implemented
  already, see `file:line`").

Example run directory for one epic with two child stories:

```
tickets/2026-07-20-search-revamp/
  epic-search-revamp.md
  story-search-index-refresh.md
  story-search-result-ranking.md
  README.md
```

Example `README.md` contents for that run:

```markdown
# search-revamp tickets (2026-07-20)

- epic-search-revamp.md - Rebuild search indexing and ranking.
  - story-search-index-refresh.md - Refresh the index on a schedule instead of on demand.
  - story-search-result-ranking.md - Rank results by recency as well as relevance.

Grounding caveats:
- story-search-index-refresh: an ad-hoc refresh script already exists at
  `scripts/reindex.sh:1`; the ticket adjusts scope to "schedule it" rather than "build it".
```
