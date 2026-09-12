#!/usr/bin/env node
// validate-static-native-imports.mjs — flag native modules imported at top-of-file.
// Root cause: requireNativeModule() runs at Metro import-time, before the root
// component mounts, so a broken native link crashes on launch with no JS stack
// trace and no boot-time try/catch ever seeing it. Zero deps, ESM, Node >= 18.
// Flags: --project --output --strict --json
import { readFileSync, existsSync, readdirSync, statSync } from "node:fs";
import { join, resolve } from "node:path";

const args = parseArgs(process.argv.slice(2));
const project = resolve(args.project || process.cwd());
const findings = [];
const add = (severity, area, message, file, line) =>
  findings.push({ severity, area, message, file, line });

// Matches a top-level `import ... from "expo-x"` or `const x = require("expo-x")`.
// Deliberately excludes bare "react-native" (core) — only flags native *packages*.
const RE = /^(?:import\s.+\sfrom\s+|.*=\s*require\()\s*['"](expo-[^'"]+|@expo\/[^'"]+|react-native-[^'"]+)['"]/;
const SKIP = /[\\/](node_modules|\.git|dist|build|coverage)[\\/]/;
const EXT = /\.(tsx|ts|jsx|js)$/;

let scanned = 0;
let hits = 0;
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
      const lines = readFileSync(p, "utf8").split("\n");
      for (let i = 0; i < lines.length; i++) {
        const m = RE.exec(lines[i]);
        if (m) {
          hits++;
          add(
            args.strict ? "WARNING" : "INFO",
            "static-native-import",
            `Top-level import of native package "${m[1]}" — if this package was added recently, a broken native link crashes on launch before the root component mounts and before any boot-time try/catch runs. Move it behind a function-scoped dynamic import (\`await import(...)\`) or confirm it has been import-time-safe across at least one prior release.`,
            p,
            i + 1
          );
        }
      }
    }
  }
})(join(project, "src"));

if (hits === 0) {
  add("INFO", "static-native-import", "No top-level native-module imports found under src/.", null);
}

const decision = decide(findings);
const report = render(findings, decision, project);
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
function render(list, decision, project) {
  const lines = [];
  lines.push("# Static Native Import Audit");
  lines.push(`**Project:** ${project}`);
  lines.push(`**Decision:** ${decision}`);
  lines.push("");
  lines.push("This is a heuristic, not proof of a crash — confirm each hit against the package's actual add date and native-linking behavior. Cold-launch a Release build 5× regardless; this bug does not reproduce in Debug/dev-client builds.");
  lines.push("");
  lines.push("| Severity | Area | Message | File:Line |");
  lines.push("| --- | --- | --- | --- |");
  for (const f of list) lines.push(`| ${f.severity} | ${f.area} | ${f.message} | ${f.file || "-"}${f.line ? ":" + f.line : ""} |`);
  if (!list.length) lines.push("| (none) | - | No findings. | - |");
  return lines.join("\n");
}
