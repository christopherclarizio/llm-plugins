import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { spawn, spawnSync } from "node:child_process";
import { copyFileSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, rmSync, symlinkSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

const plugin = dirname(dirname(fileURLToPath(import.meta.url)));
const repository = dirname(dirname(plugin));
const script = join(plugin, "hooks/capture-reminder.mjs");
const summary = "[main abc1234] capture finding\n 1 file changed, 1 insertion(+)\n";

function fixture(t) {
  const root = mkdtempSync(join(tmpdir(), "nmws capture tests-"));
  const corpus = join(root, "corpus");
  const cwd = join(root, "unrelated working directory");
  mkdirSync(corpus);
  mkdirSync(cwd);
  t.after(() => {
    try {
      assert.deepEqual(readdirSync(corpus), []);
    } finally {
      rmSync(root, { recursive: true, force: true });
    }
  });
  const env = {
    ...process.env,
    NMWS_DOCS_CORPUS_ROOT: corpus,
    TMPDIR: root,
    TEMP: root,
    TMP: root,
  };
  const options = (input, overrides) => ({
    cwd, env: { ...env, ...overrides }, encoding: "utf8",
    input: typeof input === "string" ? input : JSON.stringify(input),
    timeout: 10000,
  });
  const run = (input, host = "claude", overrides = {}) =>
    spawnSync(process.execPath, [script, host], options(input, overrides));
  const runAsync = (input) => new Promise((resolveResult, reject) => {
    const child = spawn(process.execPath, [script, "claude"], { cwd, env, timeout: 10000 });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (data) => { stdout += data; });
    child.stderr.on("data", (data) => { stderr += data; });
    child.on("error", reject);
    child.on("close", (status) => resolveResult({ status, stdout, stderr }));
    child.stdin.end(JSON.stringify(input));
  });
  const event = (overrides = {}) => ({
    hook_event_name: "PostToolUse", session_id: "session-a", cwd,
    tool_name: "Bash", tool_input: { command: "git commit -m 'capture finding'" },
    tool_response: { stdout: summary, stderr: "", interrupted: false },
    transcript_path: join(root, "must-not-be-read.jsonl"),
    ...overrides,
  });
  const stateBase = join(root, `nmws-documentation-auto-${process.getuid?.() ?? "user"}`);
  const stateDirectory = (session = "session-a") =>
    join(stateBase, createHash("sha256").update(session).digest("hex"));
  return { root, corpus, cwd, run, runAsync, event, stateBase, stateDirectory };
}

function emitted(result, event = "PostToolUse") {
  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stderr, "");
  const output = JSON.parse(result.stdout);
  assert.deepEqual(Object.keys(output), ["hookSpecificOutput"]);
  assert.equal(output.hookSpecificOutput.hookEventName, event);
  const context = output.hookSpecificOutput.additionalContext;
  assert.ok(context.startsWith("[nmws-documentation-auto]"));
  assert.ok(context.length < 5000);
  assert.match(context, /offer-documentation-capture/);
  assert.match(context, /wait for explicit user consent/);
  assert.match(context, /at most two unsolicited offers/);
  assert.match(context, /no more after a decline/);
  assert.match(context, /This reminder is not an offer/);
  assert.match(context, /Do not read transcript files or other sessions/);
  assert.match(context, /exact-diff approval/);
  return output;
}

function silent(result) {
  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stdout, "");
  assert.equal(result.stderr, "");
}

test("both hosts inject nonblocking session reminders without creating state", (t) => {
  const f = fixture(t);
  for (const host of ["claude", "codex"]) {
    for (const source of ["startup", "resume", "compact", "clear"]) {
      const output = emitted(f.run(f.event({ hook_event_name: "SessionStart", source }), host), "SessionStart");
      assert.match(output.hookSpecificOutput.additionalContext, /including read-only investigations/);
      assert.match(output.hookSpecificOutput.additionalContext, /suppress unsolicited offers/);
    }
  }
  assert.deepEqual(readdirSync(f.root).sort(), ["corpus", "unrelated working directory"]);
});

test("unconfigured corpus suppresses all reminders and state", (t) => {
  const f = fixture(t);
  for (const root of ["", " \t"]) {
    for (const event of [f.event(), f.event({ hook_event_name: "SessionStart" })]) {
      silent(f.run(event, "claude", { NMWS_DOCS_CORPUS_ROOT: root }));
    }
  }
  assert.deepEqual(readdirSync(f.root).sort(), ["corpus", "unrelated working directory"]);
});

test("Claude accepts completed structured Bash responses and optional exit codes", async (t) => {
  for (const response of [
    { stdout: summary, stderr: "", interrupted: false },
    { stdout: summary, exit_code: 0 },
    { output: summary, exitCode: 0 },
  ]) {
    await t.test(JSON.stringify(response), (t) => {
      const f = fixture(t);
      emitted(f.run(f.event({ tool_response: response })));
    });
  }
});

test("Codex accepts canonical command, legacy cmd, raw completed output and status headers", async (t) => {
  for (const [toolName, commandField, response] of [
    ["Bash", "command", summary],
    ["exec_command", "cmd", `Chunk ID: abcd\nWall time: 0.1 seconds\nProcess exited with code 0\nOutput:\n${summary}`],
    ["shell_command", "command", `Process exited with code 0\nFinal output:\n${summary}`],
    ["Bash", "command", { output: summary, exit_code: 0 }],
  ]) {
    await t.test(`${toolName} ${commandField}`, (t) => {
      const f = fixture(t);
      emitted(f.run(f.event({
        tool_name: toolName, tool_input: { [commandField]: "git commit -m fix" },
        tool_response: response,
      }), "codex"));
    });
  }
});

test("simple quoted commands, Git global options, comments and chains are recognized", async (t) => {
  for (const command of [
    "git commit -m \"fix the 'cache'\"",
    "git -C '/some repo' -c user.name=Agent --no-pager commit -m fix",
    "git --git-dir='.git' --work-tree . --literal-pathspecs commit -m fix",
    "cd '/some repo' && git add . && git commit -m fix",
    "# previous investigation\ngit commit -m fix",
    "git add .;\ngit commit -m 'literal $variable and `backticks`'",
    "git \\\ncommit -m fix",
    "/usr/bin/git commit -m fix",
    "GIT_AUTHOR_NAME=Agent git commit -m fix",
    "git commit -m ''",
  ]) {
    await t.test(command, (t) => {
      const f = fixture(t);
      emitted(f.run(f.event({ tool_input: { command } })));
    });
  }
});

test("mentions, other Git commands, dry runs and ambiguous shell syntax do not nudge", (t) => {
  const f = fixture(t);
  for (const command of [
    "echo 'git commit -m fix'",
    'printf "%s\\n" "git commit -m fix"',
    "git status", "git log --oneline", "git show abc1234",
    "git commit --dry-run -m fix",
    "git commit -m fix | cat",
    "git commit -m fix || true",
    "git commit -m fix &",
    "git commit -m fix > output.txt",
    "echo $(git commit -m fix)",
    "bash -c 'git commit -m fix'",
    "git commit -m \"$message\"",
    "git commit -m 'unterminated",
    "git commit -m fix\\",
    "echo here # git commit -m fix",
  ]) {
    silent(f.run(f.event({ tool_input: { command } })));
  }
  silent(f.run(f.event({ tool_name: "Read" })));
  silent(f.run(f.event({ hook_event_name: "Stop" })));
});

test("failed, interrupted, running, no-op and summary-free results do not nudge", (t) => {
  const f = fixture(t);
  for (const response of [
    { stdout: summary, exit_code: 1 },
    { stdout: summary, exitCode: 0, exit_code: 1 },
    { stdout: summary, interrupted: true },
    { stdout: summary, interrupted: false, timed_out: true },
    { stdout: summary, interrupted: false, backgroundTaskId: "background" },
    { stdout: summary, exit_code: 0, process_id: 123 },
    { stdout: summary, exit_code: 0, process_id: 0 },
    { stdout: summary, exit_code: 0, session_id: 123 },
    { stdout: "nothing to commit, working tree clean\n", interrupted: false },
    { stdout: "fatal: not a git repository\n", interrupted: false },
    { stdout: "", interrupted: false },
  ]) {
    silent(f.run(f.event({ tool_response: response })));
  }
  for (const response of [
    `Process exited with code 1\nOutput:\n${summary}`,
    `Process exited with code 1: failed\n${summary}`,
    `Process exited with code -1\nFinal output:\n${summary}`,
    `Process running with session ID 123\nOutput:\n${summary}`,
    "nothing to commit, working tree clean\n",
  ]) {
    silent(f.run(f.event({ tool_response: response }), "codex"));
  }
});

test("commit reminders are deduplicated and capped independently of session reminders", (t) => {
  const f = fixture(t);
  emitted(f.run(f.event()));
  silent(f.run(f.event()));
  emitted(f.run(f.event({ hook_event_name: "SessionStart", source: "compact" })), "SessionStart");
  emitted(f.run(f.event({ tool_response: { stdout: summary.replace("abc1234", "def5678"), interrupted: false } })));
  silent(f.run(f.event({ tool_response: { stdout: summary.replace("abc1234", "aaa1234"), interrupted: false } })));
  emitted(f.run(f.event({ session_id: "session-b" })));
  const files = readdirSync(f.stateDirectory());
  assert.equal(files.filter((name) => name.startsWith("reminder-")).length, 2);
  assert.equal(files.filter((name) => name.startsWith("commit-")).length, 2);
  for (const path of files) {
    const content = readFileSync(join(f.stateDirectory(), path), "utf8");
    assert.ok(content === "" || /^[0-9a-f]{64}$/.test(content));
  }
});

test("arbitrary session identifiers cannot escape the private state directory", (t) => {
  const f = fixture(t);
  const session = "../escape/../../malformed session";
  emitted(f.run(f.event({ session_id: session })));
  assert.deepEqual(readdirSync(f.stateBase), [createHash("sha256").update(session).digest("hex")]);
});

test("concurrent duplicate commits emit only one reminder", async (t) => {
  const f = fixture(t);
  const results = await Promise.all(Array.from({ length: 8 }, () => f.runAsync(f.event())));
  const reminders = results.filter((result) => result.stdout !== "");
  assert.equal(reminders.length, 1);
  for (const result of results) {
    if (result.stdout) emitted(result);
    else silent(result);
  }
});

test("concurrent distinct commits never exceed two reminders", async (t) => {
  const f = fixture(t);
  const results = await Promise.all(Array.from({ length: 8 }, (_, i) =>
    f.runAsync(f.event({ tool_response: { stdout: summary.replace("abc1234", `abc123${i}`), interrupted: false } }))));
  assert.equal(results.filter((result) => result.stdout !== "").length, 2);
  for (const result of results) {
    if (result.stdout) emitted(result);
    else silent(result);
  }
  assert.equal(readdirSync(f.stateDirectory()).length, 4);
});

test("malformed payloads and unconfirmed response objects report explicit nonblocking errors", (t) => {
  const f = fixture(t);
  for (const [input, host] of [
    ["{invalid", "claude"], [[], "claude"], [null, "claude"],
    [f.event({ session_id: "" }), "claude"],
    [f.event({ tool_input: {} }), "claude"],
    [f.event({ tool_response: {} }), "claude"],
    [f.event({ tool_response: { stdout: summary, exit_code: "0" } }), "claude"],
    [f.event({ tool_response: { stdout: summary, exit_code: null } }), "codex"],
    [f.event({ tool_response: { stdout: summary } }), "claude"],
    [f.event({ tool_response: { stdout: summary, interrupted: false } }), "codex"],
    [f.event({ tool_response: summary }), "claude"],
    [f.event(), "unknown"],
  ]) {
    const result = f.run(input, host);
    assert.equal(result.status, 1);
    assert.equal(result.stdout, "");
    assert.match(result.stderr, /^\[nmws-documentation-auto\] .+\n$/);
  }
});

test("state failures surface rather than emitting a success-shaped fallback", (t) => {
  const f = fixture(t);
  writeFileSync(f.stateBase, "not a directory");
  const result = f.run(f.event());
  assert.equal(result.status, 1);
  assert.equal(result.stdout, "");
  assert.match(result.stderr, /^\[nmws-documentation-auto\]/);
});

test("symlink state directories are refused", { skip: process.platform === "win32" }, (t) => {
  const f = fixture(t);
  symlinkSync(f.corpus, f.stateBase, "dir");
  const result = f.run(f.event());
  assert.equal(result.status, 1);
  assert.equal(result.stdout, "");
  assert.match(result.stderr, /state directory is not private/);
});

test("real successful and failed Git commits exercise both host adapters", (t) => {
  const f = fixture(t);
  const git = (...args) => {
    const result = spawnSync("git", ["-C", f.cwd, ...args], { encoding: "utf8" });
    assert.equal(result.error, undefined);
    return result;
  };
  assert.equal(git("init", "--quiet").status, 0);
  const settings = ["-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
    "-c", "commit.gpgsign=false", "-c", "core.hooksPath="];
  const success = git(...settings, "commit", "--allow-empty", "-m", "Capture fixture finding");
  assert.equal(success.status, 0, success.stderr);
  const command = `git -C '${f.cwd}' commit --allow-empty -m 'Capture fixture finding'`;
  emitted(f.run(f.event({
    tool_input: { command },
    tool_response: { stdout: success.stdout, stderr: success.stderr, interrupted: false },
  })));
  emitted(f.run(f.event({
    session_id: "codex-session", tool_input: { cmd: command }, tool_response: success.stdout,
  }), "codex"));
  const failed = git(...settings, "commit", "-m", "No changes");
  assert.notEqual(failed.status, 0);
  silent(f.run(f.event({
    tool_input: { command },
    tool_response: { stdout: failed.stdout, stderr: failed.stderr, exit_code: failed.status },
  })));
  silent(f.run(f.event({ tool_response: failed.stdout }), "codex"));
});

test("manifests, marketplaces, release notes and host hook entry points agree", (t) => {
  const claude = JSON.parse(readFileSync(join(plugin, ".claude-plugin/plugin.json")));
  const codex = JSON.parse(readFileSync(join(plugin, ".codex-plugin/plugin.json")));
  assert.equal(claude.name, "nmws-documentation-auto");
  assert.equal(claude.version, codex.version);
  const marketplace = JSON.parse(readFileSync(join(repository, ".claude-plugin/marketplace.json")));
  const entry = marketplace.plugins.find((item) => item.name === claude.name);
  assert.equal(entry.version, claude.version);
  assert.equal(resolve(repository, entry.source), plugin);
  const codexMarketplace = JSON.parse(readFileSync(join(repository, ".agents/plugins/marketplace.json")));
  const codexEntry = codexMarketplace.plugins.find((item) => item.name === codex.name);
  assert.equal(resolve(repository, codexEntry.source.path), plugin);
  assert.match(readFileSync(join(repository, "CHANGELOG.md"), "utf8"), new RegExp(`${claude.name} ${claude.version}`));
  const f = fixture(t);
  const installed = join(f.root, "installed plugin");
  mkdirSync(join(installed, "hooks"), { recursive: true });
  copyFileSync(script, join(installed, "hooks/capture-reminder.mjs"));
  for (const [host, config, variable] of [
    ["claude", "hooks/hooks.json", "CLAUDE_PLUGIN_ROOT"],
    ["codex", codex.hooks, "PLUGIN_ROOT"],
  ]) {
    const hooks = JSON.parse(readFileSync(join(plugin, config))).hooks;
    assert.deepEqual(Object.keys(hooks).sort(), ["PostToolUse", "SessionStart"]);
    assert.ok(new RegExp(hooks.PostToolUse[0].matcher).test("Bash"));
    for (const event of Object.keys(hooks)) {
      const handler = hooks[event][0].hooks[0];
      assert.equal(handler.timeout, 5);
      assert.equal(handler.type, "command");
      assert.equal(handler.command, `node "\${${variable}}/hooks/capture-reminder.mjs" ${host}`);
      const command = handler.command.replace(`\${${variable}}`, installed);
      const result = spawnSync(command, {
        shell: true, cwd: f.cwd,
        env: { ...process.env, NMWS_DOCS_CORPUS_ROOT: f.corpus, TMPDIR: f.root, TEMP: f.root, TMP: f.root },
        input: JSON.stringify(f.event({
          session_id: `packaging-${host}-${event}`, hook_event_name: event,
          tool_response: host === "codex" ? summary : { stdout: summary, interrupted: false },
        })),
        encoding: "utf8", timeout: 10000,
      });
      emitted(result, event);
    }
  }
});
