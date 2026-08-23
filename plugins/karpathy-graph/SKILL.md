---
name: karpathy-graph
description: Build typed, provenance-tracked knowledge graphs from any context — documents, codebases, incidents, research — so one or many AI agents share durable memory instead of copying transcripts. Use when the user says "build a knowledge graph", "criar grafo", "map this codebase/domain", "graph these documents", "extract entities and relations", "ground this claim", "visualize the graph", or asks how facts, sources and experiments connect. Every claim carries a source, every merge is reversible, every answer cites edge ids. Writes to the given path, or to ./.karpathy-graphs/<graph-name>/ by default, and renders an interactive HTML explorer for humans.
metadata:
  version: 1.0.0
---

# Karpathy Graph

You are building the **graph plane** of an agentic system: the layer that
remembers what the context window forgets.

> The agent forgets, the graph does not.

This skill turns any context — a folder of documents, a codebase, an incident,
a research thread — into a typed graph that both machines and humans can read.
One agent can build it. Many agents can build it concurrently. A human opens
`graph.html` and sees the same thing the agents queried.

## The one rule that matters

**Never write an unsourced fact.**

Every `Claim` node either points at a `Source`, or is explicitly marked
`inference=true`. The engine enforces this — `kgraph validate` fails otherwise.
If you cannot cite where a fact came from, it does not enter the graph.

## Before you build: does this need a graph?

A graph earns its cost when connected queries, evolving relations, provenance,
or shared world state are central. Skip it when tasks are independent, answers
come from one document, no cross-session state is needed, or a flat table would
answer every question. Say so plainly and stop — do not build a graph just
because agents are involved.

Read `references/decision-framework.md` when unsure.

## Where the graph goes

| Situation | Location |
|---|---|
| User gave a path | exactly that path |
| No path given | `./.karpathy-graphs/<graph-name>/` from the project root |

`<graph-name>` is the slugified graph name. Never invent a different root, and
never write graph files outside the graph directory.

Each graph directory holds:

```
manifest.json   name, objective, budget, counters
log.jsonl       append-only event log — the source of truth, reversible
graph.json      materialized nodes + edges
REPORT.md       human summary: health, composition, invariant violations
graph.html      interactive explorer (search, type filter, click-to-inspect)
graph.mmd       Mermaid diagram for docs and PRs
```

`log.jsonl` is what makes bad writes undoable. Never hand-edit it, never delete
it to "clean up" — retract instead.

## The engine

Everything runs through one stdlib-only Python CLI. No dependencies, no network,
works identically under Claude Code, Codex, OpenCode, Antigravity, Gemini, or a
plain shell.

```bash
KG="${CLAUDE_PLUGIN_ROOT:-plugins/karpathy-graph}/scripts/kgraph.py"

python3 "$KG" --name "<graph>" init --objective "<what this graph answers>"
python3 "$KG" --name "<graph>" --run-id run_001 ingest @payload.json
python3 "$KG" --name "<graph>" validate
python3 "$KG" --name "<graph>" query "<text>" --hops 2 --format context
python3 "$KG" --name "<graph>" render
```

Every command prints one JSON object. `validate` exits non-zero when an
invariant is violated — wire it into CI or a loop as the metric.

Full command surface: `references/cli.md`.

## The pipeline

Five stages. Run them in order the first time; afterwards any stage can run
alone against an existing graph.

| Stage | Skill | What it does |
|---|---|---|
| 1. Extract | `karpathy-graph-extract` | Context → typed entities and S-P-O relations |
| 2. Resolve | `karpathy-graph-resolve` | Surface forms → canonical entities, reversibly |
| 3. Assemble | `karpathy-graph-build` | Validated write into the graph with provenance |
| 4. Query | `karpathy-graph-query` | Bounded subgraph retrieval with edge citations |
| 5. Evaluate | `karpathy-graph-evaluate` | Score extraction, resolution, and cited paths |

Plus two that sit alongside:

- `karpathy-graph-visualize` — render for humans, explain what the picture shows
- `karpathy-graph-swarm` — fan the pipeline out across parallel agents

Invoke the sub-skill when you are doing that stage's work. Each one carries the
prompts, schemas, and failure modes for its stage.

## Ontology

Nine node types, eleven edge types. Do not invent new ones — put anything extra
in `attrs`.

**Nodes:** `Entity` `Claim` `Source` `Artifact` `AgentRun` `Evaluation` `Task`
`Commit` `Metric`

**Edges:** `MENTIONS` `SUPPORTS` `CONTRADICTS` `DERIVED_FROM` `PRODUCED`
`EVALUATES` `REVISES` `SUPERSEDES` `DEPENDS_ON` `PARENT_OF` `RESOLVED_TO`

Semantics and worked examples: `references/ontology.md`.

## The four write invariants

Every write must satisfy all four. `kgraph validate` checks them.

1. **I1** — every `Claim` has a `Source` edge, or `inference=true`
2. **I2** — every `Artifact` has an authoring `AgentRun` and a version
3. **I3** — every `Evaluation` identifies a rubric
4. **I4** — every superseded object stays addressable

A violation is a bug in your write, not a warning to note and move past. Fix it
before rendering.

## Retrieval discipline

The graph must not become a new way to dump context.

Never paste `graph.json` into a prompt. Resolve the task's entities, expand one
or two hops over the edge types that matter, serialize inside a token budget,
and keep the edge ids so the answer can cite them.

```bash
python3 "$KG" --name "<graph>" query "vendor X" --hops 2 \
  --edge-type SUPPORTS --edge-type MENTIONS --max-nodes 40 --format context
```

`--format context` returns entities plus relations with `[edge:...]` citations,
ready to paste into a worker's prompt. `--format triples` returns relations only.

## Grounding a claim

To check "Vendor X supplied the component involved in Incident Y", do not ask a
model. Ask the graph:

```bash
python3 "$KG" --name "<graph>" path <vendor_x_id> <incident_y_id>
```

Found with citations → the claim is supported, and you cite those edge ids.
Not found → return structured feedback naming the missing evidence, not a
free-form critique. Template: `references/grounding.md`.

## Multi-agent writes

Workers publish `GraphUpdate` payloads; they never edit graph files directly.
The orchestrator validates and applies them, so its own context stays clean.

```bash
python3 "$KG" --name "<graph>" --run-id "$RUN" ingest @worker-output.json
```

Each worker gets its own `--run-id`, and that run id lands on every node and
edge it creates. Provenance survives, and a bad worker's writes can be traced
and retracted. Details and concurrency rules: `references/multi-agent.md`.

## Reversibility

```bash
python3 "$KG" --name "<graph>" retract --edge <edge_id>
python3 "$KG" --name "<graph>" retract --node <node_id>
```

Retraction appends a reversal event — it never rewrites history. Entity merges
are reversible too: aliases keep their own node plus a `RESOLVED_TO` edge, so a
false merge is undone by retracting one edge instead of rebuilding the graph.

This matters more than it looks. A false merge collapses two people into one
node and silently contaminates every downstream traversal.

## Budget

Declare limits before fanning out, and report what you spent. When the budget is
exhausted, return the best current graph, what completed, what is unresolved,
and why you stopped. **Do not hide partial failure behind a fluent summary.**

```bash
python3 "$KG" --name "<graph>" init --budget '{"max_documents":200,"max_agents":16,"max_tokens":500000}'
```

## Finishing

Always end a build with:

```bash
python3 "$KG" --name "<graph>" validate && python3 "$KG" --name "<graph>" render
```

Then tell the user, in this order: where the graph is, how big it is, how many
invariant violations remain (should be zero), what to open (`graph.html`), and
what the graph still does not know.

That last item is not optional. A graph is only as good as its sources — missing
documents produce missing edges, and a confident report over a thin corpus is
worse than an honest one.

## Health signals

Read these from `REPORT.md` after every build:

| Signal | Reads as |
|---|---|
| Isolated nodes rising | extraction produced entities nothing links to |
| Components rising | the corpus is fragmented, or resolution is under-merging |
| Components collapsing to 1 | possible over-merging — check for false merges |
| Density < 0.5 | relations are being missed |
| Any violation | a malformed write; fix before shipping |

One connected component is **not** automatically the goal. A connected but false
graph is worse than an honest fragmented one.

## Guardrails

- Never fabricate a source, a URI, or a confidence score.
- Never merge entities on string similarity alone — use context, record the rationale.
- Never write outside the graph directory.
- Never delete `log.jsonl`.
- Never dump the whole graph into a prompt.
- Never report a build as clean without running `validate`.
