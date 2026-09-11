#!/usr/bin/env node
// SessionStart hook: inject personal coding preferences into every session.
//
// Reads the sibling CODING.md and returns it as additionalContext so the
// preferences apply to all conversations, in any repository, without being
// checked into that repository. Edit CODING.md to change the preferences — no
// code change required. Uses Node (ships with Claude Code) for cross-platform
// reliability.

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const pluginRoot = dirname(dirname(fileURLToPath(import.meta.url)));
const codingPath = join(pluginRoot, "CODING.md");

let coding = "";
try {
  coding = readFileSync(codingPath, "utf8").trim();
} catch (err) {
  // Fail quiet: a missing/unreadable preferences file must never break a session.
  process.stderr.write(`clarizio-housestyle-coding: could not read CODING.md: ${err.message}\n`);
  process.exit(0);
}

if (coding) {
  process.stdout.write(
    JSON.stringify({
      hookSpecificOutput: {
        hookEventName: "SessionStart",
        additionalContext: coding,
      },
    }),
  );
}
