---
id: <stable-kebab-slug>              # required. Router key; links resolve to it. Don't rename casually.
title: <Human Readable Title>        # required.
tree: product                        # required. Always `product` for this template.
tier: feature                        # required. One of: overview | feature | workflow.
description: >                       # required. THE routing hook: the question this answers + when to read it.
  <One to three sentences, in the user's language. Lead with what the feature lets a user
  do. End with "Read before <the tasks this is relevant to>.">
parent: <id-of-parent-doc>           # optional. The next tier up.
children: [<id>, <id>]               # optional. The tier(s) down.
related: [<id>, <id>]                # optional. Cross-links; include the code-tree counterpart.
keywords: [<term>, <term>]           # optional. Extra matching signal for the router.

sources:                             # required. Repo-relative paths/globs for the IMPLEMENTING code.
  - <path/or/glob/**>                #   product docs anchor at the code that implements the feature.
verified_at:                         # required.
  commit: <sha>                      #   HEAD of the code repo when last checked against reality.
  date: <YYYY-MM-DD>
  by: <person-or-"agent">            #   product docs should reach human-reviewed via someone who knows the product.
trust: draft                         # required. One of: draft | agent-generated | human-reviewed.
---

<!-- PRODUCT tree body. One concept per section. Written for understanding the product as
     users experience it — not its implementation. Delete these comments when you fill it. -->

## Purpose & scope
<!-- purpose: The one user-facing capability this doc covers, and — explicitly — what it
     does not (point elsewhere). -->

## What it is
<!-- purpose: The feature from the user's point of view — the capability and the value it
     delivers, in the user's language, not the code's. -->

## How it's used
<!-- purpose: The typical path a user takes — the steps and the entry points in the
     UI/workflow. Concrete enough to reflect real usage, not a guess. -->

## Where it fits
<!-- purpose: How this slots into larger user workflows and relates to adjacent features —
     the context that makes an isolated feature make sense. -->

## Known limitations & sharp edges
<!-- purpose: What doesn't work, common user confusions, and gotchas — from the user's
     perspective. Usually the highest-value section: it exists nowhere in the code. -->

## Implemented by
<!-- purpose: The bridge into the code tree. Link the code-tree docs and name the entry
     points that implement this feature. Keep this doc's `sources` anchored at that
     implementing code so drift is detectable. -->

## Drill down / see also
<!-- purpose: Progressive-disclosure links: down to sub-features/workflows, across to the
     code-tree counterpart. Relative-path links. -->
