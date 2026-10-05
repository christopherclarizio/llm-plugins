---
id: prod-scripting
title: Premiere Scripting - Product Documentation Example
tree: product
tier: feature
description: >
  Where user-facing scripting behavior belongs in a cross-repository documentation
  corpus. Read before documenting scripting capabilities or limitations.
  This is an illustrative layout, not verified product guidance.
related: [ppro-scripting-architecture]
keywords: [scripting, automation, cross-repository]
code_references:
  - repository: scripting-napi
    paths: [src/bindings/**]
    verified_at:
      commit: "0000000"
      date: 2026-10-05
      by: agent
  - repository: scripting-types
    paths: [types/**]
    verified_at:
      commit: "0000000"
      date: 2026-10-05
      by: agent
  - repository: scripting-gateway
    paths: [src/gateway/**, config/allowlist/**]
    verified_at:
      commit: "0000000"
      date: 2026-10-05
      by: agent
trust: draft
---

<!-- ILLUSTRATIVE ONLY. All code references are placeholders. This is not verified
     Premiere product guidance; human review is required before treating it as such. -->

## Purpose & scope

Demonstrates a product document referencing implementing code across repositories.
It does not establish supported APIs, workflows, or actual product limitations.

## What it is

Describe the scripting capability in users' language after checking it with someone
who knows the product, rather than deriving the entire account from code or types.

## How it's used

Capture confirmed user entry points and workflows here.

## Where it fits

Explain the capability's relationship to the larger automation workflow.

## Known limitations & sharp edges

Record verified user-visible limitations, including cross-layer discrepancies if any.
Do not assume that a declared type alone establishes an available capability.

## Implemented by

[Scripting architecture example](../code/ppro-scripting-architecture.md) illustrates
the bridge to code documentation. Each repository has a separate verification commit.

## Drill down / see also

- [Code: Scripting architecture example](../code/ppro-scripting-architecture.md)
