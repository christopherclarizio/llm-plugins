import { createHash } from "node:crypto";
import { lstatSync, mkdirSync, readFileSync, unlinkSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const policy = [
  "Use nmws-documentation's offer-documentation-capture skill, not the writing skill,",
  "to review durable findings available in the current conversation.",
  "If that skill is unavailable, report that nmws-documentation 0.4.0 or newer is",
  "required; do not substitute an improvised capture workflow.",
  "Offer only understanding that prevents a future wrong turn; skip routine edits,",
  "speculation, already-covered findings, and documentation-only housekeeping.",
  "Name the finding and likely document, batch related findings, and wait for explicit",
  "user consent before capture. Do not read transcript files or other sessions.",
  "Track actual offers and declines in conversation context: at most two unsolicited",
  "offers per session, no repeat findings, and no more after a decline.",
  "This reminder is not an offer and does not consume that allowance.",
  "Preserve this etiquette in normal compaction summaries; if prior offer/decline",
  "history is unavailable after resume or compaction, suppress unsolicited offers.",
  "Explicit review or capture requests remain available. Never treat unattended",
  "operation as consent. Report missing configuration or evidence instead of inventing",
  "documentation. Capture uses its existing grounding and validation safeguards;",
  "corrections to existing claims require the verification skill's exact-diff approval.",
  "No automatic staging, committing, pushing, or trust promotion.",
].join(" ");

function record(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

// Recognize simple POSIX command sequences without evaluating shell text.
// Ambiguous shell syntax is deliberately left to the session-boundary reminder.
function commandsFrom(command) {
  const commands = [];
  let words = [];
  let word = "";
  let active = false;
  let quote = "";
  const endWord = () => {
    if (active) words.push(word);
    word = "";
    active = false;
  };
  const endCommand = () => {
    endWord();
    if (words.length) commands.push(words);
    words = [];
  };
  for (let i = 0; i < command.length; i += 1) {
    const char = command[i];
    if (quote === "'") {
      if (char === "'") quote = "";
      else word += char;
    } else if (char === "\\" && quote !== "'") {
      const next = command[++i];
      if (next === undefined) return [];
      if (next !== "\n") {
        word += next;
        active = true;
      }
    } else if (quote === '"') {
      if (char === '"') quote = "";
      else if (char === "$" || char === "`") return [];
      else word += char;
    } else if (char === "'" || char === '"') {
      quote = char;
      active = true;
    } else if (char === "#" && !active) {
      while (i < command.length && command[i] !== "\n") i += 1;
      endCommand();
    } else if (char === "&" && command[i + 1] === "&") {
      endCommand();
      i += 1;
    } else if (char === ";" || char === "\n") {
      endCommand();
    } else if (/\s/.test(char)) {
      endWord();
    } else if ("|&<>`$(){}".includes(char)) {
      return [];
    } else {
      word += char;
      active = true;
    }
  }
  if (quote) return [];
  endCommand();
  return commands;
}

function isCommit(words) {
  let i = 0;
  while (/^[A-Za-z_]\w*=/.test(words[i] ?? "")) i += 1;
  if (!/^(?:.*\/)?git$/.test(words[i] ?? "")) return false;
  i += 1;
  while (i < words.length) {
    if (["-C", "-c", "--git-dir", "--work-tree", "--namespace"].includes(words[i])) {
      i += 2;
    } else if (["--no-pager", "--literal-pathspecs"].includes(words[i]) ||
      /^--(?:git-dir|work-tree|namespace)=/.test(words[i])) {
      i += 1;
    } else {
      break;
    }
  }
  return words[i] === "commit" && !words.slice(i + 1).includes("--dry-run");
}

function completedOutput(response, host) {
  if (record(response)) {
    if (response.interrupted === true || response.timed_out === true ||
      response.backgroundTaskId || response.process_id != null || response.session_id != null) return null;
    const codes = ["exit_code", "exitCode"].filter((key) => key in response);
    if (codes.some((key) => !Number.isInteger(response[key]))) {
      throw new Error("shell exit status must be an integer");
    }
    if (codes.some((key) => response[key] !== 0)) return null;
    const output = response.stdout ?? response.output;
    if (typeof output !== "string") {
      throw new Error("unsupported shell response; cannot confirm commit completion");
    }
    if (codes.length || (host === "claude" && response.interrupted === false)) {
      return output;
    }
    throw new Error("shell response has no completion status");
  }
  if (host !== "codex" || typeof response !== "string") {
    throw new Error("unsupported shell response; cannot confirm commit completion");
  }
  // Codex unified exec currently sends raw completed-command output to hooks.
  // Some shell versions include a status header; never accept a failing header.
  const header = response.split(/^(?:Final output|Output):\r?$/m, 1)[0];
  if (/^Process running with session ID /m.test(header)) return null;
  const codes = [...header.matchAll(/^Process exited with code (-?\d+)(?::.*)?\r?$/gm)];
  if (codes.some((match) => match[1] !== "0")) return null;
  return response;
}

function digest(value) {
  return createHash("sha256").update(value).digest("hex");
}

function privateDirectory(path) {
  mkdirSync(path, { recursive: true, mode: 0o700 });
  const stat = lstatSync(path);
  if (!stat.isDirectory() || stat.isSymbolicLink() ||
    (process.getuid && (stat.uid !== process.getuid() || (stat.mode & 0o077) !== 0))) {
    throw new Error("reminder state directory is not private");
  }
}

function claimReminder(session, fingerprint) {
  const base = join(tmpdir(), `nmws-documentation-auto-${process.getuid?.() ?? "user"}`);
  privateDirectory(base);
  const directory = join(base, digest(session));
  privateDirectory(directory);
  const key = digest(fingerprint);
  const slots = [join(directory, "reminder-1"), join(directory, "reminder-2")];
  const prior = slots.map((path) => {
    try {
      return readFileSync(path, "utf8");
    } catch (error) {
      if (error.code === "ENOENT") return null;
      throw error;
    }
  });
  if (prior.includes(key) || prior.every((value) => value !== null)) return false;
  const claim = join(directory, `commit-${key}`);
  try {
    writeFileSync(claim, "", { flag: "wx", mode: 0o600 });
  } catch (error) {
    if (error.code === "EEXIST") return false;
    throw error;
  }
  let reserved = false;
  try {
    for (const path of slots) {
      try {
        writeFileSync(path, key, { flag: "wx", mode: 0o600 });
        reserved = true;
        return true;
      } catch (error) {
        if (error.code !== "EEXIST") throw error;
      }
    }
    return false;
  } finally {
    if (!reserved) unlinkSync(claim);
  }
}

function reminder(event, host) {
  if (!record(event)) throw new Error("hook input must be a JSON object");
  if (!["claude", "codex"].includes(host)) throw new Error("expected claude or codex host");
  if (!process.env.NMWS_DOCS_CORPUS_ROOT?.trim()) return null;
  if (typeof event.session_id !== "string" || !event.session_id.trim()) {
    throw new Error("hook input is missing session_id");
  }
  let context;
  if (event.hook_event_name === "SessionStart") {
    context = `At natural task boundaries, including read-only investigations, consider whether to offer documentation capture. This is a reminder, not guaranteed completion detection. ${policy}`;
  } else if (event.hook_event_name === "PostToolUse") {
    if (!["Bash", "exec_command", "shell_command"].includes(event.tool_name)) return null;
    const command = event.tool_input?.command ?? event.tool_input?.cmd;
    if (typeof command !== "string") throw new Error("shell input is missing command");
    if (!commandsFrom(command).some(isCommit)) return null;
    const output = completedOutput(event.tool_response, host);
    if (output === null) return null;
    const summary = output.match(/^\[[^\]\r\n]+ [0-9a-f]{7,64}\] .+$/m)?.[0].trimEnd();
    if (!summary) return null;
    if (!claimReminder(event.session_id, `${event.cwd ?? ""}\n${summary}`)) return null;
    context = `A Git commit completion summary was observed. Consider the findings from the current conversation, not just the committed diff. ${policy}`;
  } else {
    return null;
  }
  return {
    hookSpecificOutput: {
      hookEventName: event.hook_event_name,
      additionalContext: `[nmws-documentation-auto] ${context}`,
    },
  };
}

try {
  const event = JSON.parse(readFileSync(0, "utf8"));
  const output = reminder(event, process.argv[2]);
  if (output) process.stdout.write(`${JSON.stringify(output)}\n`);
} catch (error) {
  const message = error instanceof SyntaxError ? "invalid hook JSON" : error.message;
  process.stderr.write(`[nmws-documentation-auto] ${message}\n`);
  process.exitCode = 1;
}
