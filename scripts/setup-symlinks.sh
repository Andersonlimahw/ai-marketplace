#!/usr/bin/env bash

# setup-symlinks.sh - Configure sharing of skills across agents
# This script creates symlinks from agent home directories to this repository's plugins/ folder.
# Supported agents: Claude Code, Codex, Codex App, Gemini, Agy, OpenCode.
#
# Phase 3.5: after directory symlinks, sync agent frontmatter per-harness via
# scripts/sync-agents.py. Raw symlinks for `agents/` would feed Claude-format
# frontmatter to OpenCode/Agy/Gemini and break them (e.g. `tools:` is deprecated
# in OpenCode v1.1.1, `name:` is treated as a label, missing `description:` is
# a hard error). The sync emits per-harness materialized files with strict
# schema validation and fail-loud warnings for invalid keys.

set -euo pipefail

# Pull the managed clone safely: fetch first, move any untracked file that the
# incoming changes would overwrite into a timestamped backup dir, then pull.
update_repo() {
  local repo_root="$1"
  git -C "$repo_root" fetch origin main --quiet || {
    echo "WARNING: fetch failed for $repo_root" >&2
    return 1
  }
  local incoming
  incoming=$(git -C "$repo_root" diff --name-only HEAD FETCH_HEAD)
  local backup_dir="$repo_root/.pull-backup-$(date +%s)"
  local moved=0
  local f
  while IFS= read -r f; do
    [ -z "$f" ] && continue
    if [ -e "$repo_root/$f" ] && ! git -C "$repo_root" ls-files --error-unmatch -- "$f" >/dev/null 2>&1; then
      mkdir -p "$backup_dir/$(dirname "$f")"
      mv "$repo_root/$f" "$backup_dir/$f"
      moved=1
    fi
  done <<< "$incoming"
  if [ "$moved" = "1" ]; then
    echo "Moved conflicting untracked files to $backup_dir"
  fi
  git -C "$repo_root" pull origin main
}

# Get the absolute path of the repository's plugins directory
if [ -d "$PWD/plugins" ] && [ -d "$PWD/.git" ]; then
  # Running from within a local clone
  REPO_ROOT="$PWD"
else
  # Running via curl or outside the repo
  REPO_ROOT="$HOME/.lemon-ai-hub"
  echo "Setting up Lemon AI Hub at $REPO_ROOT..."
  if [ ! -d "$REPO_ROOT" ]; then
    git clone https://github.com/Andersonlimahw/lemon-ai-hub.git "$REPO_ROOT"
  else
    update_repo "$REPO_ROOT"
  fi
fi
REPO_PLUGINS_DIR="$REPO_ROOT/plugins"
SYNC_AGENTS="$REPO_ROOT/scripts/sync-agents.py"

install_symlink() {
  local target="$1"
  local link_name="$2"

  echo "Setting up symlink: $link_name -> $target"

  link_name="${link_name/#\~/$HOME}"

  if [ -d "$link_name" ] && [ ! -L "$link_name" ]; then
    local backup="${link_name}_bak_$(date +%s)"
    echo "Warning: Directory $link_name exists. Backing up to $backup"
    mv "$link_name" "$backup"
  elif [ -L "$link_name" ] || [ -e "$link_name" ]; then
    rm -f "$link_name"
  fi

  mkdir -p "$(dirname "$link_name")"
  ln -s "$target" "$link_name"
  echo "Created: $link_name"
}

echo "=== Lemon AI Hub: Headless Symlink Setup ==="
echo "Scope: Global (~/)"
echo "Target: All Supported Agents"

# Claude Code deliberately has NO ~/.claude/skills link: it consumes the hub via
# the lemon-ai-hub plugin marketplace; a skills/ symlink would duplicate every
# skill in the session context.

# Codex, Agy, OpenCode (~/.config/opencode), and Gemini keep CURATED skills
# dirs: hub-backed entries become individual symlinks, non-hub entries remain
# untouched. Whole-dir symlinks would load 150+ descriptions per session and
# would hide shared-overlay companions such as impeccable and revenue-centric-design.
curate_hub_symlinks() {
  local skills_dir="$1"
  skills_dir="${skills_dir/#\~/$HOME}"
  [ -d "$skills_dir" ] || return 0
  local entry name
  for entry in "$skills_dir"/*/; do
    [ -d "$entry" ] || continue
    name="$(basename "$entry")"
    if [ ! -L "${entry%/}" ] && [ -d "$REPO_PLUGINS_DIR/$name" ]; then
      local backup="${skills_dir}/.${name}_bak_$(date +%s)"
      echo "Curating: $name (physical hub copy -> symlink; backup at $backup)"
      mv "${entry%/}" "$backup"
      ln -s "$REPO_PLUGINS_DIR/$name" "${entry%/}"
    fi
  done
}
curate_hub_symlinks "~/.codex/skills"
curate_hub_symlinks "~/.agy/skills"
curate_hub_symlinks "~/.config/opencode/skills"
curate_hub_symlinks "~/.gemini/skills"

# Phase 3.5: per-harness agent frontmatter sync.
# Materializes transformed copies of plugins/cli-wrapper/agents/*.md into each
# harness's agents/ dir with the correct schema (drops `name` for OpenCode,
# drops `tools`, validates permission keys, emits Codex .toml sidecar).
if [ -f "$SYNC_AGENTS" ]; then
  echo ""
  echo "=== Phase 3.5: Agent Frontmatter Sync ==="
  if python3 "$SYNC_AGENTS"; then
    echo "Agent frontmatter synced across all harnesses."
  else
    echo "WARNING: sync-agents.py reported errors. Run 'python3 $SYNC_AGENTS --verify' to inspect." >&2
  fi
else
  echo "WARNING: $SYNC_AGENTS not found. Skipping per-harness agent sync." >&2
fi

echo "=== All symlinks configured successfully! ==="
