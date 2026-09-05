---
title: plugin.json Component Declarations (MANDATORY)
status: active
updated: 2026-09-05
related: [docs/rules/marketplace-sync.md, scripts/validate_plugins.py, AGENTS.md]
---

# Rule: never declare a component path `plugin.json` cannot deliver

**Why:** PRs #32 and #33. Six plugins declared `"agents": "./agents/"`. Claude
Code's manifest schema rejects a bare directory string there, and it validates
the manifest **before** registering anything — so the install aborted and every
skill and agent the plugin shipped vanished silently:

```
✘ Failed to install plugin "code-review-expert@lemon-ai-hub":
  Validation errors: agents: Invalid input
```

The failure is invisible until someone tries to use the skill. `code-review-expert`
was unreachable in Claude Code and Codex for months while working fine in
Antigravity, which reads `SKILL.md` off disk and never parses `plugin.json`.
`smart-sub-agents` — the worker-matrix plugin the routing contract depends on —
was dead the same way.

## The invariant

Every component path a manifest declares MUST exist on disk, and `agents` MUST
be an array.

| Field      | Valid shape                                  | Invalid                     |
|------------|----------------------------------------------|-----------------------------|
| `agents`   | array of file paths                          | `"./agents/"` — install fails |
| `skills`   | path to an existing, non-empty directory      | path that does not exist    |
| `commands` | path to an existing, non-empty directory      | path that does not exist    |
| `hooks`    | path to an existing file                      | path that does not exist    |

```jsonc
// correct
"agents": [
  "./agents/thermo-nuclear-review-subagent.md",
  "./agents/thermo-nuclear-code-quality-review-subagent.md"
]
```

## Prefer omitting the field

Components are discovered by convention from `agents/`, `skills/` and the root
`SKILL.md`. 158 of the 166 plugins in this repo declare no component fields at
all and load correctly. **Declare a field only when you need to override the
convention.** An omitted field cannot break; a wrong one takes the whole plugin
down.

Never declare a directory that is empty or holds only `.gitkeep` — that
announces components the plugin does not ship.

## How to verify before committing

```bash
# Repo guard — catches every shape above (MANIFEST_* codes):
python3 scripts/validate_plugins.py

# Claude Code's own schema, the authoritative oracle:
for f in plugins/*/plugin.json; do claude plugin validate "$f"; done
```

`scripts/validate_plugins.py` reported `0 errors` while five plugins were
uninstallable, which is why it now enforces this rule directly. Do not weaken
the `MANIFEST_AGENTS_NOT_ARRAY`, `MANIFEST_PATH_NOT_FOUND` or
`MANIFEST_PATH_EMPTY` checks — re-run `claude plugin validate` first and fix
the manifest instead.
