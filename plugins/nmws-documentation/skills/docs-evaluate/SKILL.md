---
name: docs-evaluate
description: Runs a small paired evaluation of representative tasks with versus without the documentation corpus, measuring correctness, wrong turns, and tokens when available. Use explicitly to evaluate corpus value; keeps source-derived tasks and results private and does not build a permanent evaluation platform.
---

# docs-evaluate

A demand-driven pilot, not an automatic benchmark on every capture.

1. Require an explicitly selected private artifact destination and a real configured
   corpus. Choose a small representative set of actual understanding tasks, including
   at least one covered task and one coverage gap. Establish the expected answer and
   a correctness rubric from source/human evidence **before** running either condition.
   Keep prompts, expected answers, outputs, and evidence out of this public plugin repo.
2. Run each task twice in independent fresh contexts with the same model, prompt, tool
   permissions, source baseline, and budget. In `with-corpus`, enable `docs-router`;
   in `without-corpus`, disable corpus access. Do not let one condition see the other
   output, rubric answers, or source-derived notes. Pin/check source SHAs so moving
   checkouts do not confound results. Counterbalance run order across tasks.
   If isolated contexts or comparable baselines are unavailable, stop and report the
   evaluation as blocked; do not simulate a control from the same informed context.
3. Score against the pre-established rubric. Count wrong turns (concrete mistaken
   hypotheses or irrelevant investigations), not mere extra tool calls. Record token
   usage only from available runtime counters; use `null` plus an explanation when
   unavailable. Never estimate tokens from character counts and present them as measured.
4. Save a private JSON result per task with this shape:
   ```json
   {
     "task_id": "task-slug",
     "prompt": "...",
     "rubric": "...",
     "model": "...",
     "source_shas": {"repository-id": "checked-sha"},
     "runs": {
       "with_corpus": {
         "correctness": {"passed": 0, "total": 1},
         "wrong_turns": [],
         "tokens": null,
         "token_note": "Runtime counters unavailable",
         "output_path": "with-corpus.txt"
       },
       "without_corpus": {
         "correctness": {"passed": 0, "total": 1},
         "wrong_turns": [],
         "tokens": null,
         "token_note": "Runtime counters unavailable",
         "output_path": "without-corpus.txt"
       }
     },
     "limitations": []
   }
   ```
   Use real observations, not the placeholder scores. Validate that both runs and
   source SHAs are recorded and all output paths resolve before reporting completion.
5. Report paired correctness, wrong turns, measured tokens, and limitations. Establish
   a baseline before choosing improvement thresholds. One small pilot is not statistical
   evidence of general improvement. Recommend corpus/tooling changes only from observed
   failures; do not generate more documents automatically.
