#!/usr/bin/env node
// SessionStart hook: inject personal voice/style preferences into every session.
//
// Reads the sibling VOICE.md and returns it as additionalContext so the
// preferences apply to all conversations, in any repository, without being
// checked into that repository. Edit VOICE.md to change the style — no code
// change required. Uses Node (ships with Claude Code) for cross-platform
// reliability.

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const pluginRoot = dirname(dirname(fileURLToPath(import.meta.url)));
const voicePath = join(pluginRoot, "VOICE.md");

let voice = "";
try {
  voice = readFileSync(voicePath, "utf8").trim();
} catch (err) {
  // Fail quiet: a missing/unreadable style file must never break a session.
  process.stderr.write(`clarizio-housestyle-voice: could not read VOICE.md: ${err.message}\n`);
  process.exit(0);
}

if (voice) {
  process.stdout.write(
    JSON.stringify({
      hookSpecificOutput: {
        hookEventName: "SessionStart",
        additionalContext: voice,
      },
    }),
  );
}
