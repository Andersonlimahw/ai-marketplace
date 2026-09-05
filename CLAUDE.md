# CLAUDE.md
<!-- Lemon AI Hub: Karpathy Standards -->
Single source of truth: `@AGENTS.md`

Read on start a new session:

1. `@AGENTS.md`
2. `@README.md`

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).

## 🔌 CLI Wrapper Ecosystem

This project IS the canonical source for the `cli-wrapper` plugin — the multi-harness CLI wrapper ecosystem. Claude Code = single source of truth. Other CLIs (Codex, Gemini, Agy, OpenCode) access via symlink.

**When developing in this repo**: prefer wrapped CLI access.
- `/cli-wrapper:cli-wrapper-setup` — one-shot ecosystem setup
- `/cli-wrapper wrap <cli>` — wrap a new CLI
- `/cli-wrapper list` — all wrapped CLIs + stats
- `/cli-wrapper audit all` — ecosystem-wide savings

**Plugin structure** (this project):
```
plugins/cli-wrapper/        ← CANONICAL SOURCE (git)
├── SKILL.md                ← main skill
├── plugin.json             ← v2.0.0
├── skills/                 ← sub-skills (cli-wrapper-setup, *-cli wrappers)
├── agents/                 ← wrapper agents (one per CLI)
└── templates/              ← symlink-map.json + config templates
```

**`plugin.json` component fields** — see [`docs/rules/plugin-manifest.md`](docs/rules/plugin-manifest.md). Claude Code validates the manifest *before* registering anything, so one bad field silently removes every skill and agent the plugin ships:
- `agents` MUST be an array of file paths. `"agents": "./agents/"` fails with `agents: Invalid input` and the plugin never installs — it stays invisible in Claude Code and Codex while still working in Antigravity, which never parses `plugin.json`.
- Every declared `skills` / `commands` / `hooks` path MUST exist and be non-empty.
- **Prefer omitting these fields.** Components are discovered by convention from `agents/`, `skills/` and the root `SKILL.md`; 158 of 166 plugins here declare nothing.
- Verify before committing: `python3 scripts/validate_plugins.py` (MANIFEST_* codes) and `claude plugin validate plugins/<name>/plugin.json`.

**Global topology** (managed by `scripts/setup-symlinks.sh`; verified by `scripts/harness-doctor.sh`):
- Skills hub = this project's `plugins/`. Claude consumes it via the `lemon-ai-hub` plugin marketplace (no `~/.claude/skills` — it would duplicate every skill).
- Codex/Agy: `~/.codex/skills` and `~/.agy/skills` → dir symlinks to `plugins/`
- OpenCode (`~/.config/opencode/skills`) and Gemini (`~/.gemini/skills`): curated per-skill symlinks into `plugins/`

- Use the `git-expert` and `gh-expert` plugins for git workflows. Prefer `/git-commit` for semantic commits.
