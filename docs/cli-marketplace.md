---
title: Marketplace CLI Utility
status: active
updated: 2026-06-14
related: [docs/index.md, docs/architecture.md]
---

# Marketplace CLI Utility

The `marketplace` script located in the `scripts/` directory serves as the command-line control panel for this workspace.

## 🛠️ Commands

### 1. `list-skills`
Scans the repository's `skills/` folder and lists all active skills along with the description parsed from their markdown front-matter.
```bash
./scripts/marketplace list-skills
```

### 2. `list-plugins`
Reads the global `~/.claude/settings.json` file to list:
- Marketplaces registered under `extraKnownMarketplaces`
- Active plugins enabled in the CLI settings

```bash
./scripts/marketplace list-plugins
```

### 3. `install-skills`
Triggers the setup script to synchronize and re-create symlinks between agent configurations and the workspace repository.
```bash
./scripts/marketplace install-skills
```

### 4. `info <skill-name>`
Prints the full implementation file (`SKILL.md`) of the specified skill directly to your terminal.
```bash
./scripts/marketplace info senior-prompt-engineer
```

### 5. Install one skill with `npx skills`
The helper installs only the selected plugin directory through the open skills CLI:

```bash
./scripts/add-skill.sh logo-creator-expert --global --yes --agent claude-code
```

The equivalent direct command is:

```bash
npx skills add https://github.com/Andersonlimahw/lemon-ai-hub/tree/main/plugins/logo-creator-expert --global --yes
```
