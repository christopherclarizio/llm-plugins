---
id: <stable-kebab-slug>              # required. Router key; links resolve to it. Don't rename casually.
title: <Human Readable Title>        # required.
tree: code                           # required. Always `code` for this template.
tier: subsystem                      # required. One of: architecture | subsystem | component.
description: >                       # required. THE routing hook: the question this answers + when to read it.
  <One to three sentences. Lead with the question this doc answers. End with
  "Read before <the tasks this is relevant to>.">
parent: <id-of-parent-doc>           # optional. The next tier up.
children: [<id>, <id>]               # optional. The tier(s) down.
related: [<id>, <id>]                # optional. Cross-links; include the product-tree counterpart.
keywords: [<term>, <term>]           # optional. Extra matching signal for the router.

sources:                             # required. Repo-relative paths/globs the claims derive from.
  - <path/or/glob/**>
verified_at:                         # required.
  commit: <sha>                      #   HEAD of the code repo when last checked against reality.
  date: <YYYY-MM-DD>
  by: <person-or-"agent">            #   a person if human-reviewed; "agent" if generated & unverified.
trust: draft                         # required. One of: draft | agent-generated | human-reviewed.
---

<!-- CODE tree body. One concept per section. Say only what code cannot cheaply
     self-describe: concepts, relationships, invariants, and *why*. Delete these
     comments when you fill the template. -->

## Purpose & scope
<!-- purpose: State the one question this doc answers, and — explicitly — what it does
     NOT cover, with a pointer to where that lives. This boundary is an anti-hallucination
     and anti-overlap signal: it stops agents inventing coverage or assuming silence means
     "irrelevant." -->

## Concept
<!-- purpose: The mental model. The relationships, invariants, and the *why* — pitched
     above the code. Do not restate signatures or line-by-line behavior; an agent reads
     those faster from source. -->

## Key entry points
<!-- purpose: The concept→code bridge. Named files, types, and functions so an agent can
     jump from this doc straight to the right place in the tree. -->

## Complicated / confusing things
<!-- purpose: The non-obvious mechanics that trip people up — surprising control flow,
     easy-to-misread interactions, sharp corners. The single place for "here's what will
     bite you." -->

## Constraints & historical rationale
<!-- purpose: Hard limits and the reasons behind them — why it's built this way, what a
     past approach broke on, what must not change without care. The "why" no diff records. -->

## Drill down / see also
<!-- purpose: Progressive-disclosure links: down to children, across to the product-tree
     counterpart. Use relative-path links so they're clickable. -->
