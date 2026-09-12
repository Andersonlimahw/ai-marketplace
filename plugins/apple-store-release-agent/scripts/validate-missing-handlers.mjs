#!/usr/bin/env node
// validate-missing-handlers.mjs — find interactive elements that signal
// "button" to VoiceOver/the reviewer but have no handler, plus nested
// confirmation-sheet calls that race each other's dismiss animation on iPad.
// Zero deps, ESM, Node >= 18. Flags: --project --output --strict --json
import { readFileSync, existsSync, readdirSync, statSync } from "node:fs";
import { join, resolve } from "node:path";

const args = parseArgs(process.argv.slice(2));
const project = resolve(args.project || process.cwd());
const findings = [];
const add = (severity, area, message, file, line) =>
  findings.push({ severity, area, message, file, line });

const WINDOW = 6;
const TOUCHABLE_RE = /TouchableOpacity|Pressable/;
const ROLE_RE = /accessibilityRole\s*=\s*["']button["']/;
const PRESS_RE = /onPress\s*=/;
const CONFIRM_RE = /confirmAction\s*\(/g;
const SKIP = /[\\/](node_modules|\.git|dist|build|coverage)[\\/]/;
const EXT = /\.tsx$/;

let scanned = 0;
let deadButtons = 0;
let nestedConfirms = 0;

(function walk(dir) {
  let entries = [];
  try { entries = readdirSync(dir); } catch { return; }
  for (const e of entries) {
    if (e === "node_modules" || e === ".git" || e === "dist" || e === "build") continue;
    const p = join(dir, e);
    let st; try { st = statSync(p); } catch { continue; }
    if (SKIP.test(p)) continue;
    if (st.isDirectory()) walk(p);
    else if (EXT.test(e) && scanned < 2000) {
      scanned++;
      const text = readFileSync(p, "utf8");
      const lines = text.split("\n");

      // (a) dead interactive element: accessibilityRole="button" with no onPress
      // in the surrounding block (mirrors: rg TouchableOpacity|Pressable -A6 | rg -B6 accessibilityRole | rg -v onPress)
      for (let i = 0; i < lines.length; i++) {
        if (!ROLE_RE.test(lines[i])) continue;
        const start = Math.max(0, i - WINDOW);
        const end = Math.min(lines.length, i + WINDOW + 1);
        const block = lines.slice(start, end).join("\n");
        if (TOUCHABLE_RE.test(block) && !PRESS_RE.test(block)) {
          deadButtons++;
          add(
            "BLOCKER",
            "dead-interactive-element",
            `accessibilityRole="button" with no onPress in the surrounding ${WINDOW}-line window — signals interactive to VoiceOver and to App Review, does nothing when tapped.`,
            p,
            i + 1
          );
        }
      }

      // (b) nested confirmation sheets: 2+ confirmAction() calls in the same file
      // race the first sheet's dismiss animation, mostly reproducing on iPad.
      const confirmCount = (text.match(CONFIRM_RE) || []).length;
      if (confirmCount >= 2) {
        nestedConfirms++;
        add(
          "WARNING",
          "nested-confirmation-sheet",
          `${confirmCount} confirmAction() calls in one file — a second confirmation fired from inside the first's onConfirm can collide with the first sheet's dismiss animation (reproduces mainly on iPad). Use one confirmation at a time.`,
          p,
          null
        );
      }
    }
  }
})(join(project, "src"));

if (findings.length === 0) {
  add("INFO", "missing-handlers", "No dead interactive elements or nested confirmation sheets found under src/.", null);
}

const decision = decide(findings);
const report = render(findings, decision, project, deadButtons, nestedConfirms);
if (args.output) {
  const { writeFileSync } = await import("node:fs");
  writeFileSync(resolve(args.output), report, "utf8");
} else if (!args.json) console.log(report);
if (args.json) console.log(JSON.stringify({ project, decision, findings }, null, 2));
process.exit(decision === "NO_GO" ? 1 : 0);

function parseArgs(argv) {
  const a = {};
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    if (k === "--strict") a.strict = true;
    else if (k === "--json") a.json = true;
    else if (k === "--project") a.project = argv[++i];
    else if (k === "--output") a.output = argv[++i];
  }
  return a;
}
function decide(list) {
  if (list.some((f) => f.severity === "BLOCKER")) return "NO_GO";
  if (list.some((f) => f.severity === "WARNING")) return "GO_WITH_WARNINGS";
  return "GO";
}
function render(list, decision, project, deadButtons, nestedConfirms) {
  const lines = [];
  lines.push("# Missing Handler / Nested Confirmation Audit");
  lines.push(`**Project:** ${project}`);
  lines.push(`**Decision:** ${decision}`);
  lines.push(`**Summary:** ${deadButtons} dead interactive element(s), ${nestedConfirms} file(s) with nested confirmAction() calls.`);
  lines.push("");
  lines.push("This is Guideline 2.1(a) territory: a reviewer tapping a styled, accessible-looking element that does nothing is an instant rejection. Smoke-test destructive actions on a physical iPad — nested-sheet races reproduce there more than on iPhone.");
  lines.push("");
  lines.push("| Severity | Area | Message | File:Line |");
  lines.push("| --- | --- | --- | --- |");
  for (const f of list) lines.push(`| ${f.severity} | ${f.area} | ${f.message} | ${f.file || "-"}${f.line ? ":" + f.line : ""} |`);
  if (!list.length) lines.push("| (none) | - | No findings. | - |");
  return lines.join("\n");
}
