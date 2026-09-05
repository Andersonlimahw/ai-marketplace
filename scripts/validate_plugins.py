#!/usr/bin/env python3
"""validate_plugins.py — Cross-harness plugin/skill conformance validator.

Single source of truth for what "a valid plugin" means in this repo, across
every supported AI harness (Claude Code, Codex, Gemini, Agy/Antigravity,
OpenCode).

Canonical layout
----------------
    plugins/<name>/
    |-- plugin.json              REQUIRED  marketplace entry (Claude Code)
    |-- SKILL.md                 REQUIRED  root skill -> discovered by every
    |                                      harness that symlinks ~/.X/skills
    |                                      to plugins/ (Codex, Gemini, Agy,
    |                                      OpenCode resolve <dir>/SKILL.md)
    `-- skills/<sub>/SKILL.md    OPTIONAL  sub-skills, one dir per skill

Why the root SKILL.md is mandatory
----------------------------------
scripts/setup-symlinks.sh links ~/.claude/skills, ~/.codex/skills,
~/.gemini/skills, ~/.agy/skills and ~/.opencode/skills all to plugins/.
Non-Claude harnesses do not read plugin.json; they enumerate immediate
subdirectories and look for <dir>/SKILL.md. A plugin whose only skill lives
under skills/<sub>/SKILL.md is therefore invisible outside Claude Code.

Why skills/<sub>.md (flat) is invalid
-------------------------------------
No harness discovers a bare markdown file inside skills/. Claude Code requires
skills/<sub>/SKILL.md; the other harnesses require <dir>/SKILL.md. A flat
skills/<name>.md is dead weight in all five regimes.

Usage
-----
    validate_plugins.py                 report all findings, exit 1 on ERROR
    validate_plugins.py --json          machine-readable report
    validate_plugins.py --severity warn exit 1 on WARN too
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = REPO_ROOT / "plugins"
MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"

# Directories under plugins/ that are not user-facing plugins.
EXCLUDED = {".system"}

# Claude Code caps the injected skill description; keep headroom.
MAX_DESCRIPTION = 1024
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


@dataclass
class Finding:
    severity: str  # ERROR | WARN
    plugin: str
    code: str
    message: str

    def __str__(self) -> str:
        return f"[{self.severity}] {self.plugin}: {self.code} — {self.message}"


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)

    def error(self, plugin: str, code: str, message: str) -> None:
        self.findings.append(Finding("ERROR", plugin, code, message))

    def warn(self, plugin: str, code: str, message: str) -> None:
        self.findings.append(Finding("WARN", plugin, code, message))

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "ERROR"]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "WARN"]


def parse_frontmatter(path: Path) -> dict[str, str] | None:
    """Minimal YAML frontmatter reader.

    Only handles the flat `key: value` shape (plus folded continuation lines)
    that SKILL.md files use. Returns None when no frontmatter block is present.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end < 0:
        return None

    data: dict[str, str] = {}
    key: str | None = None
    for line in text[4:end].split("\n"):
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match:
            key = match.group(1)
            data[key] = match.group(2).strip()
        elif key and line.strip():
            data[key] = f"{data[key]} {line.strip()}".strip()
    return data


def check_skill_file(report: Report, plugin: str, path: Path, expected_name: str) -> None:
    fm = parse_frontmatter(path)
    rel = path.relative_to(REPO_ROOT)
    if fm is None:
        report.error(plugin, "SKILL_NO_FRONTMATTER", f"{rel} has no YAML frontmatter block")
        return

    name = fm.get("name", "").strip()
    if not name:
        report.error(plugin, "SKILL_NO_NAME", f"{rel} frontmatter is missing `name`")
    else:
        # `name: "foo"` is valid YAML. Only doubled quotes (`name: ""foo""`)
        # are pathological — most YAML readers parse that as an empty string
        # followed by garbage.
        if name.startswith('""') or name.startswith("''"):
            report.error(
                plugin,
                "SKILL_NAME_QUOTED",
                f"{rel} frontmatter `name` has doubled quotes: {name}",
            )
        clean = name.strip("\"'")
        if clean != expected_name:
            report.error(
                plugin,
                "SKILL_NAME_MISMATCH",
                f'{rel} frontmatter name "{clean}" != directory "{expected_name}"',
            )
        if not SLUG_RE.match(clean):
            report.error(
                plugin,
                "SKILL_NAME_NOT_SLUG",
                f'{rel} frontmatter name "{clean}" is not lowercase-kebab-case',
            )

    description = fm.get("description", "").strip().strip("\"'")
    if not description:
        report.error(plugin, "SKILL_NO_DESCRIPTION", f"{rel} frontmatter is missing `description`")
    elif len(description) > MAX_DESCRIPTION:
        report.warn(
            plugin,
            "SKILL_DESCRIPTION_LONG",
            f"{rel} description is {len(description)} chars (max {MAX_DESCRIPTION})",
        )


def check_component_declarations(report: Report, plugin_dir: Path, data: dict) -> None:
    """Validate the optional component fields of plugin.json.

    Claude Code refuses to install a plugin whose manifest fails schema
    validation, and it aborts before registering any component — so one bad
    field silently removes every skill and agent the plugin ships. Two shapes
    have bitten this repo:

        "agents": "./agents/"     -> `agents: Invalid input`, install fails
        "skills": "./skills/"     -> accepted, but a load failure at runtime
                                     when the directory does not exist

    `agents` must be an array of file paths. Every declared path must exist.
    Omitting a field entirely is always safe: components are discovered by
    convention from agents/, skills/ and the root SKILL.md.
    """
    plugin = plugin_dir.name

    agents = data.get("agents")
    if isinstance(agents, str):
        report.error(
            plugin,
            "MANIFEST_AGENTS_NOT_ARRAY",
            f'plugin.json declares "agents": "{agents}" — Claude Code rejects a '
            "bare directory string here (`agents: Invalid input`) and the whole "
            "plugin fails to install. Use an array of file paths, or drop the "
            "field and let agents/ be discovered by convention",
        )
        agents = None

    declared: list[tuple[str, str]] = []
    if isinstance(agents, list):
        declared += [("agents", str(p)) for p in agents]
    for key in ("skills", "commands", "hooks"):
        value = data.get(key)
        if isinstance(value, str):
            declared.append((key, value))
        elif isinstance(value, list):
            declared += [(key, str(p)) for p in value]

    for key, rel_path in declared:
        target = (plugin_dir / rel_path).resolve()
        if not target.exists():
            report.error(
                plugin,
                "MANIFEST_PATH_NOT_FOUND",
                f'plugin.json declares "{key}": "{rel_path}" but that path does '
                "not exist — the runtime loader reports this as a load failure. "
                "Fix the path or drop the field",
            )
        elif target.is_dir() and not any(
            child for child in target.iterdir() if not child.name.startswith(".")
        ):
            report.warn(
                plugin,
                "MANIFEST_PATH_EMPTY",
                f'plugin.json declares "{key}": "{rel_path}" but the directory is '
                "empty — drop the field rather than announce components the "
                "plugin does not ship",
            )


def check_plugin(report: Report, plugin_dir: Path) -> None:
    plugin = plugin_dir.name

    # --- plugin.json -----------------------------------------------------
    plugin_json = plugin_dir / "plugin.json"
    if not plugin_json.exists():
        report.error(
            plugin,
            "NO_PLUGIN_JSON",
            "missing plugin.json — plugin cannot be published to the marketplace",
        )
        data = None
    else:
        try:
            data = json.loads(plugin_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            report.error(plugin, "PLUGIN_JSON_INVALID", f"plugin.json is not valid JSON: {exc}")
            data = None

    if data is not None:
        if data.get("name") != plugin:
            report.error(
                plugin,
                "PLUGIN_JSON_NAME_MISMATCH",
                f'plugin.json name "{data.get("name")}" != directory "{plugin}"',
            )
        if not data.get("description"):
            report.error(plugin, "PLUGIN_JSON_NO_DESCRIPTION", "plugin.json has no description")
        if not data.get("version"):
            report.warn(plugin, "PLUGIN_JSON_NO_VERSION", "plugin.json has no version")
        check_component_declarations(report, plugin_dir, data)

    # --- root SKILL.md ---------------------------------------------------
    root_skill = plugin_dir / "SKILL.md"
    if root_skill.exists():
        check_skill_file(report, plugin, root_skill, plugin)
    else:
        report.error(
            plugin,
            "NO_ROOT_SKILL",
            "missing SKILL.md at the plugin root — invisible to Codex, Gemini, "
            "Agy and OpenCode, which resolve <skills-dir>/<plugin>/SKILL.md",
        )

    # --- skills/ ---------------------------------------------------------
    skills_dir = plugin_dir / "skills"
    if skills_dir.is_dir():
        for entry in sorted(skills_dir.iterdir()):
            if entry.name.startswith("."):
                continue
            if entry.is_dir():
                sub_skill = entry / "SKILL.md"
                if sub_skill.exists():
                    check_skill_file(report, plugin, sub_skill, entry.name)
                else:
                    report.error(
                        plugin,
                        "SUBSKILL_NO_SKILL_MD",
                        f"skills/{entry.name}/ has no SKILL.md",
                    )
            elif entry.suffix == ".md":
                report.error(
                    plugin,
                    "FLAT_SKILL_FILE",
                    f"skills/{entry.name} is a flat markdown file — no harness "
                    f"discovers it; move it to skills/{entry.stem}/SKILL.md",
                )


def check_marketplace(report: Report, plugin_dirs: list[Path]) -> None:
    if not MARKETPLACE.exists():
        report.error("<marketplace>", "NO_MARKETPLACE", f"{MARKETPLACE} does not exist")
        return
    try:
        data = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        report.error("<marketplace>", "MARKETPLACE_INVALID", f"not valid JSON: {exc}")
        return

    entries = data.get("plugins", [])
    listed = {e.get("name") for e in entries}
    on_disk = {d.name for d in plugin_dirs}

    for name in sorted(on_disk - listed):
        report.error(
            "<marketplace>",
            "PLUGIN_NOT_LISTED",
            f'plugin "{name}" exists on disk but is absent from marketplace.json',
        )
    for name in sorted(listed - on_disk):
        report.error(
            "<marketplace>",
            "PLUGIN_MISSING_ON_DISK",
            f'marketplace.json lists "{name}" but plugins/{name}/ does not exist',
        )
    for entry in entries:
        source = entry.get("source")
        if isinstance(source, str):
            target = REPO_ROOT / source.lstrip("./")
            if not target.exists():
                report.error(
                    "<marketplace>",
                    "SOURCE_NOT_FOUND",
                    f'entry "{entry.get("name")}" points at missing source {source}',
                )


def collect_plugin_dirs() -> list[Path]:
    return sorted(
        d
        for d in PLUGINS_DIR.iterdir()
        if d.is_dir() and d.name not in EXCLUDED and not d.name.startswith(".")
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="emit a machine-readable report")
    parser.add_argument(
        "--severity",
        choices=["error", "warn"],
        default="error",
        help="minimum severity that makes the run fail (default: error)",
    )
    parser.add_argument("--plugin", help="restrict the check to a single plugin")
    args = parser.parse_args()

    plugin_dirs = collect_plugin_dirs()
    if args.plugin:
        plugin_dirs = [d for d in plugin_dirs if d.name == args.plugin]
        if not plugin_dirs:
            print(f"No such plugin: {args.plugin}", file=sys.stderr)
            return 2

    report = Report()
    for plugin_dir in plugin_dirs:
        check_plugin(report, plugin_dir)
    if not args.plugin:
        check_marketplace(report, plugin_dirs)

    if args.json:
        print(
            json.dumps(
                {
                    "plugins_checked": len(plugin_dirs),
                    "errors": len(report.errors),
                    "warnings": len(report.warnings),
                    "findings": [f.__dict__ for f in report.findings],
                },
                indent=2,
            )
        )
    else:
        by_code: dict[str, list[Finding]] = {}
        for finding in report.findings:
            by_code.setdefault(finding.code, []).append(finding)
        for code, items in sorted(by_code.items(), key=lambda kv: -len(kv[1])):
            print(f"\n{items[0].severity} {code} ({len(items)})")
            for finding in items[:20]:
                print(f"  {finding.plugin}: {finding.message}")
            if len(items) > 20:
                print(f"  ... and {len(items) - 20} more")
        print(
            f"\n{len(plugin_dirs)} plugins checked — "
            f"{len(report.errors)} errors, {len(report.warnings)} warnings"
        )

    if report.errors:
        return 1
    if args.severity == "warn" and report.warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
