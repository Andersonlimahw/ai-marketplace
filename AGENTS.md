
# Andrej Kaparthy's coding style

<!-- Lemon AI Hub: Karpathy Standards -->

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## Project Rules

Mandatory project rules live in `docs/rules/`. Read and apply them before touching
the affected areas:

- [`docs/rules/marketplace-sync.md`](docs/rules/marketplace-sync.md) — every plugin
  in `plugins/` MUST be registered in `.claude-plugin/marketplace.json` in the same
  change. Never add/rename/remove a plugin without syncing the marketplace.
- [`docs/rules/plugin-manifest.md`](docs/rules/plugin-manifest.md) — never declare a
  component path `plugin.json` cannot deliver. `agents` MUST be an array of file
  paths (`"./agents/"` makes the whole install fail), and every declared `skills`
  / `commands` / `hooks` path MUST exist. Prefer omitting the field: components
  are discovered by convention. Verify with `python3 scripts/validate_plugins.py`.
- [`docs/rules/worktree-hygiene.md`](docs/rules/worktree-hygiene.md) — `.claude/`
  is local machine state and MUST be in `.gitignore`. Before any `git commit` /
  `git push` / PR creation, run `rtk git worktree list` and remove every stale
  worktree. When an agent session ends, its worktree MUST be removed in the
  same turn.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).

## 🔌 CLI Wrapper — cross-harness policy

When ANY AI harness (Claude Code, Codex, Gemini, Agy, OpenCode) needs to invoke another CLI:

1. **PREFER** `/cli-wrapper:<cli>-cli invoke <args>` over raw `<cli> <args>`
2. Wrapper validates flags via pre-built digest, post-processes output
3. Token savings: 60-95% per invocation vs raw CLI output
4. **Setup**: run `/cli-wrapper:cli-wrapper-setup` once per machine
5. **New CLI?** `/cli-wrapper wrap <new-cli>` to add to ecosystem

Wrapper agents handle cross-harness delegation (e.g., Claude spawns `codex-cli` agent to delegate to Codex). Never run raw `<cli> exec` — always through the wrapper.

- **Git & GitHub Operations**: Use the `git-expert` plugin (`/git-commit`, `git-bisect-ai`) for version control automation. For GitHub CLI interactions, use the `gh-expert` plugin.

## 🤝 Smart Handoff — cross-session continuity

When a session's context, token budget, or usage limit is nearly exhausted (~90-95%+):

1. **Save a handoff** — invoke `smart-handoff` skill or spawn `handoff-writer` agent to write a self-contained handoff file under `docs/ai/handoff/<runtime>/<date>/`, commit, push, and stop.
2. **Resume later** — invoke `handoff-resumer` agent or say "implement the handoff" / "continue where you stopped". The agent finds the latest handoff across all runtimes, verifies repo state matches, and resumes from the recorded next action.
3. **Runtime-agnostic** — handoff files are plain markdown with zero runtime assumptions. Any harness (Claude Code, Codex, Gemini, Agy, OpenCode) can read and resume.
4. **Chaining** — when you approach your own budget limit while resuming, write a new handoff pointing back to the previous one.

**Never** skip the commit/push step. Broken-but-committed beats uncommitted-and-lost. Do not fabricate session IDs — write `unknown` if the runtime doesn't expose one.
