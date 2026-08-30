#!/usr/bin/env bash
# harness-doctor.sh — Health check for the multi-harness ecosystem (Claude = source of truth).
# Verifies symlinks, hooks (rtk/caveman/context-mode), configs and drift across harnesses.
#
# Usage:  bash scripts/harness-doctor.sh          # local checks (no network)
#         bash scripts/harness-doctor.sh --net    # + zai smoke-test (calls API)
set -uo pipefail

HUB="$HOME/Projects/IA/lemon-ai-hub/plugins"
PASS=0; FAIL=0; WARN=0

ok()   { printf '  \033[32mOK\033[0m    %s\n' "$1"; PASS=$((PASS+1)); }
bad()  { printf '  \033[31mFAIL\033[0m  %s\n' "$1"; FAIL=$((FAIL+1)); }
warn() { printf '  \033[33mWARN\033[0m  %s\n' "$1"; WARN=$((WARN+1)); }

link_is() { # $1=link $2=expected_target
  [ -L "$1" ] && [ "$(readlink "$1")" = "$2" ]
}

curated_overlay_is_ready() {
  [ -d "$1" ] && [ -d "$HOME/.agents/skills" ] && [ -r "$HOME/.agents/skills/design-expert/SKILL.md" ]
}

echo "=== harness-doctor — $(date +%F) ==="

echo "[hub]"
[ -d "$HUB" ] && ok "hub plugins/ exists ($(ls "$HUB" | wc -l | tr -d ' ') plugins)" || bad "hub missing: $HUB"

echo "[rtk]"
if command -v rtk >/dev/null 2>&1; then
  ok "binary: $(rtk --version 2>/dev/null | head -1)"
  R=$(echo '{"tool_name":"Bash","tool_input":{"command":"git status"}}' | rtk hook claude 2>/dev/null)
  case "$R" in *'rtk git status'*) ok "'rtk hook claude' processor rewrites commands" ;; *) bad "'rtk hook claude' did not rewrite" ;; esac
  grep -q '"rtk hook claude"' "$HOME/.claude/settings.json" && ok "hook installed in settings.json (PreToolUse Bash)" || bad "rtk hook missing in ~/.claude/settings.json"
else
  bad "rtk not found in PATH"
fi

echo "[claude ~/.claude]"
for f in CLAUDE.md RTK.md kaparthy.md settings.json; do
  [ -r "$HOME/.claude/$f" ] && ok "$f" || bad "$f missing"
done
if [ -e "$HOME/.claude/skills" ]; then
  CLAUDE_DRIFT=0
  for entry in "$HOME/.claude/skills"/*/; do
    [ -d "$entry" ] || continue
    n="$(basename "$entry")"
    if [ -d "$HUB/$n" ]; then
      warn "~/.claude/skills/$n duplicates marketplace skill"
      CLAUDE_DRIFT=1
    fi
  done
  [ "$CLAUDE_DRIFT" = "0" ] && ok "~/.claude/skills contains local-only skills"
else
  ok "~/.claude/skills absent (correct: marketplace covers the hub)"
fi
grep -q '"caveman@caveman": true' "$HOME/.claude/settings.json" && ok "caveman plugin enabled" || bad "caveman plugin disabled"
grep -q '"context-mode@context-mode": true' "$HOME/.claude/settings.json" && ok "context-mode plugin enabled" || bad "context-mode disabled"
grep -q 'ctx-recall.sh' "$HOME/.claude/settings.json" && ok "ctx-recall (memory recall) on SessionStart" || warn "ctx-recall not wired"
grep -q 'auto-model-selector.sh' "$HOME/.claude/settings.json" && ok "auto-model-selector on UserPromptSubmit" || warn "auto-model-selector not wired"

echo "[codex ~/.codex]"
if link_is "$HOME/.codex/skills" "$HUB"; then
  ok "skills → hub"
elif curated_overlay_is_ready "$HOME/.codex/skills"; then
  ok "curated skills + shared design-expert overlay"
else
  bad "skills topology wrong: $(readlink "$HOME/.codex/skills" 2>/dev/null || echo absent)"
fi
[ -r "$HOME/.codex/AGENTS.md" ] && ok "AGENTS.md" || bad "AGENTS.md missing"
[ -r "$HOME/.codex/RTK.md" ] && ok "RTK.md" || warn "RTK.md missing (referenced by AGENTS.md)"

echo "[agy ~/.agy]"
if link_is "$HOME/.agy/skills" "$HUB"; then
  ok "skills → hub"
elif curated_overlay_is_ready "$HOME/.agy/skills"; then
  ok "curated skills + shared design-expert overlay"
else
  bad "skills topology wrong: $(readlink "$HOME/.agy/skills" 2>/dev/null || echo absent)"
fi
[ -r "$HOME/.agy/AGENTS.md" ] && ok "AGENTS.md" || bad "AGENTS.md missing"

echo "[opencode ~/.config/opencode]"
OC="$HOME/.config/opencode"
[ -r "$OC/AGENTS.md" ] && ok "AGENTS.md" || bad "AGENTS.md missing"
ls "$OC"/opencode.json* >/dev/null 2>&1 && ok "opencode.json" || bad "opencode.json missing"
for p in rtk.ts ctx-recall.ts; do
  [ -r "$OC/plugins/$p" ] && ok "plugin $p" || warn "plugin $p missing"
done
DRIFT=0
if [ -d "$OC/skills" ]; then
  for entry in "$OC/skills"/*/; do
    [ -d "$entry" ] || continue
    n="$(basename "$entry")"
    if [ ! -L "${entry%/}" ] && [ -d "$HUB/$n" ]; then
      bad "skill '$n' is a physical copy of the hub (drift) — run setup-symlinks.sh"
      DRIFT=1
    fi
  done
  [ "$DRIFT" = 0 ] && ok "skills without drift (hub-backed = symlinks)"
else
  warn "skills/ missing"
fi

echo "[gemini ~/.gemini]"
[ -r "$HOME/.gemini/GEMINI.md" ] && ok "GEMINI.md" || warn "GEMINI.md missing"
[ -d "$HOME/.gemini/skills" ] && ok "skills/ ($(ls "$HOME/.gemini/skills" | wc -l | tr -d ' ') curated)" || warn "skills/ missing"

echo "[agents git-master]"
for d in "$HOME/.claude/agents" "$HOME/.codex/agents" "$HOME/.agy/agents" "$OC/agents" "$HOME/.gemini/config/agents"; do
  [ -e "$d/git-master.md" ] && ok "$(echo "$d" | sed "s|$HOME|~|")/git-master.md" || warn "git-master missing in $(echo "$d" | sed "s|$HOME|~|")"
done

echo "[zai]"
[ -r "$HOME/.claude/env-zai.json" ] && ok "env-zai.json (provider profile)" || warn "env-zai.json missing"
if [ "${1:-}" = "--net" ]; then
  bash "$HOME/.claude/hooks/zai-health.sh" glm-4.5-air || warn "zai-health failed"
fi

echo
echo "=== summary: $PASS OK / $WARN WARN / $FAIL FAIL ==="
[ "$FAIL" -eq 0 ]
