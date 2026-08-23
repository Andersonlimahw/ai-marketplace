# karpathy-graph

Build typed, provenance-tracked knowledge graphs from any context so one or many
AI agents share durable memory instead of copying transcripts.

> The agent forgets, the graph does not.

Implements the **graph plane** described in *Karpathy: Graph Engineering
Systems* — extract, resolve, assemble, query, evaluate. Every claim carries a
source, every merge is reversible, every answer cites edge ids.

## Quick start

```bash
KG="plugins/karpathy-graph/scripts/kgraph.py"

python3 "$KG" --name "Payments Incident" init --objective "trace vendors to incidents"
python3 "$KG" --name "Payments Incident" --run-id run_1 ingest @extraction.json
python3 "$KG" --name "Payments Incident" validate
python3 "$KG" --name "Payments Incident" render
open ./.karpathy-graphs/payments-incident/graph.html
```

No dependencies. Stdlib-only Python 3.9+, no network, no install step.

## Where graphs go

| Situation | Location |
|---|---|
| A path was given | exactly that path (`--path`) |
| No path given | `./.karpathy-graphs/<graph-name>/` (`--name`) |

```
.karpathy-graphs/payments-incident/
├── manifest.json   name, objective, budget, counters
├── log.jsonl       append-only event log — the source of truth
├── graph.json      materialized nodes + edges
├── REPORT.md       health, composition, invariant violations
├── graph.html      interactive explorer
└── graph.mmd       Mermaid diagram
```

## What agents get

A single CLI that any harness drives as a subprocess — Claude Code, Codex,
OpenCode, Antigravity, Gemini, or a plain shell.

| Command | Purpose |
|---|---|
| `init` | create a graph with an objective and budget |
| `ingest` | apply an extracted `{nodes, edges}` payload in one validated write |
| `add-node` / `add-edge` | precise single writes |
| `resolve` | reversibly merge alias entities, with a recorded rationale |
| `query` | bounded subgraph retrieval (`json` / `triples` / `context`) |
| `path` | shortest provenance route — the grounding primitive |
| `validate` | check the four write invariants; exits 1 on violation |
| `stats` | nodes, edges, density, components, isolated nodes |
| `render` | write `REPORT.md`, `graph.html`, `graph.mmd` |
| `retract` | reverse a node or edge without rewriting history |
| `list` | every graph under the default root |
| `selftest` | 15-check end-to-end verification |

Full reference: [`references/cli.md`](references/cli.md).

## What humans get

`graph.html` is a self-contained explorer — no network, no build step. Open it
from a browser or attach it to an issue.

- force-directed layout, deterministic across runs
- node size by degree, colour by type
- click to inspect: type, id, description, aliases, sources, run id, every
  incident edge with direction
- search by name, type, or description
- toggle node types on and off
- pan and zoom

`graph.mmd` drops straight into markdown and renders on GitHub.

## Skills

| Skill | Stage |
|---|---|
| `karpathy-graph` | entry point, rules, retrieval discipline |
| `karpathy-graph-extract` | 1 — context → typed entities and relations |
| `karpathy-graph-resolve` | 2 — surface forms → canonical entities |
| `karpathy-graph-build` | 3 — validated assembly with provenance |
| `karpathy-graph-query` | 4 — bounded retrieval and claim grounding |
| `karpathy-graph-evaluate` | 5 — quality metrics and the ratchet loop |
| `karpathy-graph-visualize` | render for humans, explain the picture |
| `karpathy-graph-swarm` | fan the pipeline across parallel agents |

## Agents

| Agent | Role |
|---|---|
| `graph-builder` | end-to-end build: extract → resolve → assemble → validate → render |
| `graph-querier` | multi-hop answers and claim grounding with edge citations |
| `graph-orchestrator` | coordinate parallel workers writing one graph |

## Ontology

**Nodes:** `Entity` `Claim` `Source` `Artifact` `AgentRun` `Evaluation` `Task`
`Commit` `Metric`

**Edges:** `MENTIONS` `SUPPORTS` `CONTRADICTS` `DERIVED_FROM` `PRODUCED`
`EVALUATES` `REVISES` `SUPERSEDES` `DEPENDS_ON` `PARENT_OF` `RESOLVED_TO`

Fixed by design. Domain specifics go in `attrs`, never in new types — a graph
whose ontology drifts per project cannot be queried by a shared skill.

See [`references/ontology.md`](references/ontology.md).

## The four write invariants

| | Rule |
|---|---|
| **I1** | every `Claim` has a `Source` edge, or is marked `inference=true` |
| **I2** | every `Artifact` has an authoring `AgentRun` and a version |
| **I3** | every `Evaluation` identifies a rubric |
| **I4** | every superseded object stays addressable |

`validate` enforces them and exits non-zero on any violation — wire it into CI
or a ratchet loop as the gate.

## Grounding

Verify a claim by asking the graph for a path, not a model for an opinion:

```bash
python3 "$KG" --name "<graph>" path <vendor_x_id> <incident_y_id>
```

Found → cite the returned edge ids. Not found → return structured feedback
naming the missing evidence:

```json
{
  "decision": "revise",
  "claim": "Vendor X supplied the component involved in Incident Y",
  "reason": "No supported path from Vendor X to Incident Y",
  "required_evidence": [
    "A source-backed supplied relation",
    "A source-backed involved_in relation"
  ]
}
```

## Multi-agent

Workers return `GraphUpdate` payloads; the orchestrator writes. The store is
append-only and single-writer: **extract in parallel, ingest serially**, one
`--run-id` per worker so any batch stays traceable and reversible.

See [`references/multi-agent.md`](references/multi-agent.md).

## When not to use this

A graph earns its cost when connected queries, evolving relations, provenance,
or shared world state are central. Skip it when tasks are independent, answers
come from a single document, no cross-session state is needed, or a flat table
would answer every question.

Recommending against a graph is a valid outcome.

See [`references/decision-framework.md`](references/decision-framework.md).

## Tests

```bash
python3 plugins/karpathy-graph/scripts/kgraph.py selftest   # 15 engine checks
python3 plugins/karpathy-graph/tests/test_kgraph.py         # full suite
```

The suite covers the CLI the way agents use it — as subprocesses — plus the
plugin's structural contract: manifest, skills, agents, references, and
marketplace registration.

## Cross-harness

| Harness | Plugin root |
|---|---|
| Claude Code | `$CLAUDE_PLUGIN_ROOT` |
| Codex | `~/.codex/skills/karpathy-graph` |
| Agy / Antigravity | `~/.agy/skills/karpathy-graph` |
| OpenCode | `~/.config/opencode/skills/karpathy-graph` |
| Gemini | `~/.gemini/skills/karpathy-graph` |

Operating rules for every runtime: [`AGENTS.md`](AGENTS.md).

## License

MIT
