#!/usr/bin/env bash

# add-skill.sh - Install one Lemon AI Hub skill with the skills CLI.
# Usage: ./scripts/add-skill.sh <skill-name> [skills add options]

set -euo pipefail

REPO_URL="${LEMON_AI_HUB_REPO_URL:-https://github.com/Andersonlimahw/lemon-ai-hub}"
REPO_REF="${LEMON_AI_HUB_REF:-main}"

usage() {
  echo "Usage: $0 <skill-name> [skills add options]"
  echo ""
  echo "Install one skill from Lemon AI Hub via npx skills add."
  echo "Example: $0 logo-creator-expert --global --yes --agent claude-code"
}

if [ "$#" -lt 1 ] || [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  usage
  [ "$#" -lt 1 ] && exit 1
  exit 0
fi

skill_name="$1"
shift

if [[ ! "$skill_name" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  echo "Error: skill name must be lowercase kebab-case: $skill_name" >&2
  exit 2
fi

if ! command -v npx >/dev/null 2>&1; then
  echo "Error: npx is required to install a skill." >&2
  exit 127
fi

skill_source="${REPO_URL%/}/tree/${REPO_REF}/plugins/${skill_name}"
exec npx skills add "$skill_source" "$@"
