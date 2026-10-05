---
id: ppro-scripting-architecture
title: Premiere Scripting - Cross-Repository Documentation Example
tree: code
tier: architecture
description: >
  How to organize understanding of a scripting feature across NAPI bindings,
  TypeScript types, and a gateway/allowlist. Read before investigating cross-layer
  scripting changes. This is an illustrative documentation layout, not verified architecture.
related: [prod-scripting]
keywords: [scripting, NAPI, TypeScript, gateway, allowlist, cross-repository]
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

<!-- ILLUSTRATIVE ONLY. Paths, commits, and descriptions are placeholders, not verified
     implementation details. Configure real repositories and verify claims before use.
     The placeholder commits intentionally cannot establish freshness. -->

## Purpose & scope

Demonstrates a single architecture document with code references in three repositories.
It does not document actual entry points, control flow, or release compatibility.

## Concept

For a cross-repository scripting investigation, distinguish the native bindings,
the declared TypeScript API, and the gateway/allowlist. Verify their actual relationships
against code rather than inferring implementation from names or type declarations alone.

## Key entry points

Replace the placeholder paths in each code reference with the real entry points in
that repository. Repository IDs select configured checkouts, not directories relative
to this Markdown file.

## Complicated / confusing things

A gateway-only change can make this document potentially stale even when the bindings
and types have not changed. Per-repository results identify which code needs rechecking.

## Constraints & historical rationale

Independent latest-main revisions do not establish a compatible product release.
Document actual cross-layer invariants only after verifying them.

## Drill down / see also

- [Product: Scripting example](../product/prod-scripting.md)
