---
name: offer-documentation-capture
description: Reviews durable findings in the current conversation and offers to capture them in nmws-style documentation. Use when asked to review a conversation for capture, or when nmws-documentation-auto supplies a reminder. Asks for consent before writing; does not capture automatically.
---

# Offer to capture conversation findings

Preserve understanding that will prevent a future wrong turn, not the conversation
itself. Reviewing findings or receiving a hook reminder is not permission to write.

## Before starting

Require `$NMWS_DOCS_CORPUS_ROOT` or a user-provided corpus root. If neither is
available, report **"documentation corpus not configured"** and stop without
creating files or substituting bundled examples. Use
[Helper commands](../../reference/helpers.md) for discovery and freshness checks.

Use only findings and evidence available in the current conversation. Do not read
transcript files, search other sessions, or save a findings queue. Conversation
assertions are leads to verify, not verified source or product evidence.

## Workflow

1. **Check session etiquette.** For unsolicited offers, stop if the user declined
   capture this session, two actual offers have already been made, or the same
   finding was offered or captured already. Hook nudges do not count as offers.
   Track actual offers, their findings, the pending offer, and any decline in
   conversation context; retain them in the normal compaction summary if available.
   If that history is unavailable after compaction or resume, suppress unsolicited
   offers rather than assuming a fresh allowance. An explicit user request to
   review or capture overrides these unsolicited-offer limits.
2. **Identify durable understanding.** Look for evidenced invariants, non-obvious
   relationships, root causes with general applicability, corrected misconceptions,
   and product workflows or limitations. Name the question answered and what a
   future reader would otherwise misunderstand. Skip routine edits, transient
   debugging notes, speculative conclusions, already-captured findings, and
   documentation-only housekeeping. A retrieval miss alone does not warrant capture.
   If nothing qualifies, stay silent for a hook reminder; for an explicit review,
   say no capture is warranted.
3. **Find likely homes.** Run `discover_docs.py` in `focused` mode. Refine weak or
   truncated results and read likely overlaps and adjacent parents/counterparts.
   Resolve navigation IDs with `--id`; establish freshness for documents read using
   the retrieval workflow. Prefer an existing document. Do not create a new document
   merely because lexical discovery missed a match. Batch related findings into one
   offer; do not write drafts to the corpus during assessment.
4. **Offer and pause.** Briefly name the specific finding, why it matters, and its
   likely document or tree/tier when known. For example:
   "We uncovered an undocumented ordering constraint that could cause stale reads.
   Capture it in the existing cache component documentation?"
   Ask using the host's user-question tool when available, otherwise ask in chat.
   Record an actual offer only when the question is presented. Stop and wait for
   an affirmative response; silence, cancellation, unrelated replies, and a hook
   reminder are not consent. A decline suppresses further unsolicited offers for
   this session.
5. **Hand off accepted findings.** Invoke
   [Capture](../capture-information-in-documentation/SKILL.md) for the accepted
   additions, carrying their scope, likely homes, evidence, examined SHAs, and known
   gaps. Recheck sources and target baselines through its existing workflow before
   writing. If the finding instead contradicts an existing document's claims or
   only updates verification metadata, use
   [Verify](../verify-documentation-accuracy/SKILL.md): accepting the offer authorizes
   investigation, not application of an unseen correction diff. Obtain its separate
   exact-diff approval. Do not include unrelated findings in either handoff.

## Boundaries

Explicitly asking to review a conversation for capture is not asking to write;
explicitly asking to capture named findings can go directly to the capture skill.
Do not let general task authorization or unattended operation substitute for capture
consent. Keep the offer pending until the user responds.

Capture retains the existing templates, hierarchy, evidence, trust, source safety,
concurrent-change checks, and validation rules. Missing configuration, insufficient
evidence, and helper failures are explicit limitations, never reasons to invent
claims or verification metadata. Report a likely destination as tentative until
grounding and overlap checks establish it.

Acceptance does not authorize staging, committing, pushing, or promoting trust.
Do not duplicate the capture implementation or relax the
[documentation update workflow](../../reference/proposal-workflow.md).
