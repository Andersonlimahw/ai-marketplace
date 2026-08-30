# Lemon AI Hub Scripts

This directory contains utility scripts to help manage and configure your AI agents with the Lemon AI Hub ecosystem.

## Available Scripts

### `menu.sh`
An interactive menu that provides a guided way to:
- Add the marketplace to Claude Code
- Setup symlinks for all your local AI agents
- Setup symlinks for a specific agent (e.g., only Gemini or OpenCode)
- Update the Marketplace Manifest
- Normalize Plugins Configs

**Usage:**
```bash
./scripts/menu.sh
```
*Or directly via curl without cloning:*
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Andersonlimahw/lemon-ai-hub/main/scripts/menu.sh)"
```

### `setup-symlinks.sh`
Automatically creates symlinks in the correct directories for all supported agents (`~/.claude/skills`, `~/.codex/skills`, `~/.gemini/skills`, etc.) pointing to this repository's `plugins/` directory.

**Usage:**
```bash
./scripts/setup-symlinks.sh
```

### `add-skill.sh`
Installs one skill from the public Lemon AI Hub repository through the `npx skills` CLI. The helper targets the selected plugin directory, so it does not install the entire hub.

**Usage:**
```bash
./scripts/add-skill.sh logo-creator-expert --global --yes --agent claude-code
```

Override the source repository or branch when needed with `LEMON_AI_HUB_REPO_URL` and `LEMON_AI_HUB_REF`.

### Marketplace & Maintenance Scripts
- `validate_plugins.py`: Checks every plugin against the canonical cross-harness layout. Source of truth for what a valid plugin is. Exits non-zero on any violation, so it works as a CI gate.
- `normalize_plugins.py`: Repairs violations the validator reports — moves flat `skills/<n>.md` into `skills/<n>/SKILL.md`, derives a missing root `SKILL.md`, generates `plugin.json`, and fixes frontmatter `name`. Idempotent.
- `update_marketplace.py`: Generates/updates the `marketplace.json` manifest and the README plugin table from the plugins on disk.
- `sync-agents.py`: Materializes per-harness agent frontmatter from the canonical files in `plugins/cli-wrapper/agents/`.

#### Canonical plugin layout

Every plugin must match this shape:

```
plugins/<name>/
├── plugin.json              # marketplace metadata (Claude Code)
├── SKILL.md                 # root skill — REQUIRED
└── skills/<sub>/SKILL.md    # sub-skills (optional), one directory each
```

The root `SKILL.md` is mandatory because `setup-symlinks.sh` points
`~/.claude/skills`, `~/.codex/skills`, `~/.gemini/skills`, `~/.agy/skills` and
`~/.opencode/skills` all at `plugins/`. Non-Claude harnesses do not read
`plugin.json` — they enumerate subdirectories and look for `<dir>/SKILL.md`. A
plugin whose only skill lives under `skills/<sub>/SKILL.md` is therefore
invisible outside Claude Code.

#### Maintenance loop

```bash
python3 scripts/normalize_plugins.py --dry-run   # preview repairs
python3 scripts/normalize_plugins.py             # apply
python3 scripts/update_marketplace.py            # refresh manifest + README
python3 scripts/validate_plugins.py              # must exit 0
```

#### Tests

Unit + integration tests for the normalizer and validator live in `scripts/tests/`
(stdlib `unittest`, no dependencies; pytest also collects them):

```bash
python3 -m unittest discover -s scripts/tests
```

The integration test asserts the contract between the two scripts: a messy
plugin run through `normalize_plugins.py` must pass `validate_plugins.py`
with zero errors.
