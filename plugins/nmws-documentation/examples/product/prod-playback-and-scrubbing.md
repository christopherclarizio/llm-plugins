---
id: prod-playback-and-scrubbing
title: Playback & Scrubbing
tree: product
tier: feature
description: >
  What a user experiences when they play a sequence or drag the playhead to preview it:
  real-time playback, scrubbing, and preview quality. Read before working on anything that
  affects how edits are previewed in the timeline.
parent: prod-timeline-overview
children: []
related: [ppro-playback-engine]
keywords: [playback, scrubbing, preview, playhead, timeline, dropped frames]

sources:
  - PremierePro/Playback/**
verified_at:
  commit: 76fa570afb88
  date: 2026-07-15
  by: agent
trust: draft
---

<!-- ILLUSTRATIVE EXAMPLE. Fabricated to demonstrate the product-tree template shape and
     the code↔product bridge. NOT verified with anyone who knows the product — note
     `trust: draft`. Product docs should reach `human-reviewed` via a real product expert. -->

## Purpose & scope

Covers previewing a sequence during editing — pressing play and dragging the playhead
(scrubbing). It does **not** cover final export/render (a separate feature) or audio-only
monitoring.

## What it is

Playback lets an editor watch their sequence exactly as it will look, in real time, without
rendering it first. Scrubbing lets them drag the playhead and see the frame under it update
live, so they can find an exact moment quickly.

## How it's used

An editor presses the spacebar to play from the playhead, or drags the playhead across the
timeline to scrub. The program monitor shows the composited result of every clip and effect
at that time. Editors typically scrub to locate a cut point, then play a few seconds to
judge timing.

## Where it fits

Playback is the feedback loop at the center of the editing workflow — every trim, effect,
and transition is judged by playing it back. It sits between timeline editing (what the user
changes) and export (the final output), and shares the same rendering path as export so that
"what you preview is what you get."

## Known limitations & sharp edges

- On heavy sequences the engine drops frames to keep real-time playback in sync; the preview
  looks choppy even though the sequence itself is fine. Users often mistake this for a
  project problem.
- Scrubbing a section with un-cached, effect-heavy frames lags behind the playhead, because
  each frame is rendered on demand.
- Preview quality can be reduced automatically under load, which some users read as a
  quality bug rather than a deliberate trade-off.

## Implemented by

- [Premiere Pro Playback Engine](../code/ppro-playback-engine.md) — the pull-based
  request/render loop behind both play and scrub.

## Drill down / see also

- ↔ [Code: Playback engine](../code/ppro-playback-engine.md)
