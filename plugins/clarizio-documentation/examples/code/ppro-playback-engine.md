---
id: ppro-playback-engine
title: Premiere Pro Playback Engine
tree: code
tier: subsystem
description: >
  How Premiere turns a sequence into frames on screen in real time: the split between
  the sequence model and the render pipeline, the frame-request flow, and the threading
  model. Read before touching playback, scrubbing, or preview rendering.
parent: ppro-architecture-overview
children: [ppro-render-graph, ppro-frame-cache]
related: [prod-playback-and-scrubbing]
keywords: [playback, preview, scrubbing, render pipeline, frame cache, real-time]

sources:
  - PremierePro/Playback/**
  - MediaCore/MediaFoundation/RenderPipeline/**
verified_at:
  commit: 76fa570afb88
  date: 2026-07-15
  by: agent
trust: draft
---

<!-- ILLUSTRATIVE EXAMPLE. The content below is fabricated to demonstrate the code-tree
     template shape and the router loop. It is NOT verified against the codebase — note
     `trust: draft` and `by: agent`. Replace before treating any of it as real. -->

## Purpose & scope

Explains how a sequence becomes displayed frames during playback and scrubbing. Covers the
sequence-model / render-pipeline split, the frame-request flow, and threading. It does
**not** cover the render graph's node internals (see [render graph](../code/ppro-render-graph.md))
or the frame cache's eviction policy (see [frame cache](../code/ppro-frame-cache.md)).

## Concept

Playback is a pull system. The sequence model is a passive description of clips and
effects; it never pushes frames. A player owns a clock and, on each tick, *requests* the
frame for the current time. That request is resolved by the render pipeline, which walks
the effect graph for the frame and returns a rendered buffer. The invariant that matters:
the sequence model is read-only during a render pass — a frame request must see a
consistent snapshot, so edits are applied between passes, never during one.

## Key entry points

- `SequencePlayer` — `PremierePro/Playback/SequencePlayer.h` (owns the clock, issues requests)
- `FrameRequest` — `PremierePro/Playback/FrameRequest.h` (the unit of work)
- `RenderPipeline::Resolve()` — `MediaCore/MediaFoundation/RenderPipeline/RenderPipeline.cpp`

## Complicated / confusing things

The clock and the render pipeline run on different threads. `SequencePlayer` requests
frame N while the pipeline may still be resolving frame N-1; results can arrive out of
order and are reordered against the request's timestamp before display. Reading the
sequence model from the player thread mid-pass is the classic source of tearing bugs.

## Constraints & historical rationale

The read-only-during-pass rule exists because an earlier design mutated the model in place
and produced non-deterministic frames when an edit landed mid-render. Snapshotting was
chosen over locking to keep the UI thread from stalling during heavy renders.

## Drill down / see also

- ↓ [Render graph](../code/ppro-render-graph.md) *(not yet written)*
- ↓ [Frame cache](../code/ppro-frame-cache.md) *(not yet written)*
- ↔ [Product: Playback & scrubbing](../product/prod-playback-and-scrubbing.md)
