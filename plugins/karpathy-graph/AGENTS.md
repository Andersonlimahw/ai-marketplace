# karpathy-graph — agent contract

Runtime-agnostic operating rules. Claude Code, Codex, OpenCode, Antigravity
(Agy), Gemini CLI, and a plain shell all drive this plugin the same way: one
stdlib-only Python CLI, invoked as a subprocess.

## Engine

```bash
KG="${CLAUDE_PLUGIN_ROOT:-plugins/karpathy-graph}/scripts/kgraph.py"
python3 "$KG" --help
```

No dependencies, no install step, no network. If `CLAUDE_PLUGIN_ROOT` is not
set — every harness except Claude Code — point at the plugin directory directly:

| Harness | Typical root |
|---|---|
| Claude Code | `$CLAUDE_PLUGIN_ROOT` |
| Codex | `~/.codex/skills/karpathy-graph` |
| Agy / Antigravity | `~/.agy/skills/karpathy-graph` |
| OpenCode | `~/.config/opencode/skills/karpathy-graph` |
| Gemini | `~/.gemini/skills/karpathy-graph` |
| Anything else | the checked-out `plugins/karpathy-graph` |

Requires Python 3.9+. Verify with `python3 "$KG" selftest` — 15 checks, exit 0.

## Where graphs go

| Situation | Location |
|---|---|
| User gave a path | that path, via `--path` |
| No path given | `./.karpathy-graphs/<slug>/`, via `--name` |

Never create a second root. Never write graph files outside the graph directory.

## Non-negotiable rules

1. **No unsourced claims.** Every `Claim` cites a `Source` or carries
   `inference=true`. `validate` enforces it.
2. **No fabrication.** Never invent a source, URI, or confidence score.
3. **No similarity-only merges.** Entity resolution uses context as evidence and
   records a rationale. When uncertain, do not merge.
4. **No new types.** Nine node types, eleven edge types. Extras go in `attrs`.
5. **No context dumping.** Retrieve bounded subgraphs; never paste `graph.json`
   into a prompt.
6. **No history deletion.** `log.jsonl` is the source of truth. Retract, never
   delete.
7. **No clean report without `validate`.** Zero violations or it is not done.

## Write path

```bash
python3 "$KG" --name "<graph>" init --objective "<what this answers>"
python3 "$KG" --name "<graph>" --run-id "$RUN" ingest @payload.json
python3 "$KG" --name "<graph>" validate    # exit 1 blocks
python3 "$KG" --name "<graph>" render
```

Always pass `--run-id`. It stamps every node and edge, and it is the only way to
trace and retract a bad batch.

## Read path

```bash
python3 "$KG" --name "<graph>" query "<entities>" --hops 2 --format context
python3 "$KG" --name "<graph>" path <a_id> <b_id>
```

`query --format context` is what you paste into a worker's prompt. `path` is the
grounding primitive — use it instead of asking a model whether a claim holds.

## Multi-agent

Workers return `GraphUpdate` payloads; the orchestrator writes. The store is
append-only and **single-writer**: extract in parallel, ingest serially, one
`--run-id` per worker.

See `references/multi-agent.md`.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | success |
| 1 | `validate` / `selftest` failed |
| 2 | user error |
| 3 | unexpected error |

Wire `validate` into CI or a ratchet loop as the gate.

## Invariants

- **I1** every `Claim` has a `Source` edge or `inference=true`
- **I2** every `Artifact` has an authoring `AgentRun` and a version
- **I3** every `Evaluation` identifies a rubric
- **I4** every superseded object stays addressable

A violation is a malformed write, not a warning to note and move past.

## Reporting

Always close with: path, counts, violations, `graph.html`, and **what the graph
does not know**. A graph is only as good as its corpus.
