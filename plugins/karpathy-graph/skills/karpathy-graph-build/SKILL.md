---
name: karpathy-graph-build
description: Stage 3 of the karpathy-graph pipeline, and the end-to-end entry point. Create a graph, assemble validated writes with provenance, and produce the machine and human artifacts. Use when the user asks to build or create a knowledge graph from a context, to add facts to an existing graph, or when running the whole extract-resolve-assemble-query pipeline in one go.
metadata:
  version: 1.0.0
---

# Build

The assembly stage, and the front door for the whole pipeline. This is where a
payload becomes a graph that satisfies the invariants.

## Decide the location first

| Situation | Location |
|---|---|
| User gave a path | exactly that path, via `--path` |
| No path given | `./.karpathy-graphs/<slug>/`, via `--name` |

```bash
KG="${CLAUDE_PLUGIN_ROOT:-plugins/karpathy-graph}/scripts/kgraph.py"

# default location
python3 "$KG" --name "Payments Incident" init --objective "trace vendor to incident"

# explicit location
python3 "$KG" --path ./docs/graphs/payments init --objective "trace vendor to incident"
```

Never write graph files anywhere else, and never create a second root.

## Set the objective and budget

```bash
python3 "$KG" --name "<graph>" init \
  --objective "which vendors and components connect to the March incidents" \
  --budget '{"max_documents":200,"max_agents":16,"max_tokens":500000}'
```

The objective is not decoration — it decides what belongs in the graph. If a
fact does not serve the objective, leave it out. An unfocused graph is a slow,
expensive way to store noise.

## Assemble

Writes go in as payloads, not as hand-edited files.

```bash
python3 "$KG" --name "<graph>" --run-id run_001 ingest @extraction.json
```

Inline JSON and stdin (`@-`) also work. Single nodes and edges when you need
precision:

```bash
python3 "$KG" --name "<graph>" --run-id run_001 add-node \
  --type Entity --name "AuthMiddleware" --description "request auth gate" \
  --attr 'aliases=["auth-mw"]'

python3 "$KG" --name "<graph>" --run-id run_001 add-edge \
  --predicate DEPENDS_ON --source <a_id> --target <b_id> \
  --source-doc "src/server.ts:41" --confidence 0.95
```

Always pass `--run-id`. It lands on every node and edge, and it is how a bad
batch gets traced back and retracted.

## Validate before you render

```bash
python3 "$KG" --name "<graph>" validate
```

Exit code 0 and `violations: []` or the graph is not ready. Each violation
names the invariant and the node.

| Violation | Fix |
|---|---|
| I1 — claim has no source | add the `SUPPORTS`/`DERIVED_FROM` edge from its `Source`, or mark `inference=true` |
| I2 — artifact has no run | add `AgentRun -PRODUCED-> Artifact`, and set a version |
| I3 — evaluation has no rubric | add `--attr rubric="<criteria>"` |
| I4 — superseded object missing | do not delete superseded objects; retract the `SUPERSEDES` edge instead |

Fix the write. Do not suppress the check.

## Render

```bash
python3 "$KG" --name "<graph>" render
```

Writes `REPORT.md`, `graph.html`, and `graph.mmd`. Run it after every build —
a stale `graph.html` is worse than none, because a human will trust it.

## Full pipeline

```bash
KG="${CLAUDE_PLUGIN_ROOT:-plugins/karpathy-graph}/scripts/kgraph.py"
G="Payments Incident"
RUN="run_$(date +%s)"

python3 "$KG" --name "$G" init --objective "…"        # 1. create
python3 "$KG" --name "$G" --run-id "$RUN" ingest @extraction.json  # 2. extract → assemble
# 3. resolve duplicates (karpathy-graph-resolve)
python3 "$KG" --name "$G" validate                     # 4. gate
python3 "$KG" --name "$G" render                       # 5. artifacts
python3 "$KG" --name "$G" query "vendor" --format context  # 6. use it
```

## Incremental builds

Graphs are additive. Re-running `ingest` on an existing graph appends; nodes
with the same type and name upsert and bump their version rather than
duplicating. New documents can arrive at any time.

```bash
python3 "$KG" --name "<graph>" --run-id run_002 ingest @more-documents.json
python3 "$KG" --name "<graph>" validate && python3 "$KG" --name "<graph>" render
```

`init` on an existing graph fails on purpose. Nothing overwrites a graph
silently.

## Report honestly

When you finish, tell the user:

1. Where the graph is
2. Node and edge counts, components, isolated nodes
3. Invariant violations — should be zero
4. What to open: `graph.html`
5. **What the graph does not know**

Point five is not optional. Name the documents you did not read, the relations
you could not source, and the entities you declined to merge. A graph is only as
good as its corpus, and a confident report over a thin corpus misleads.

Next stage: `karpathy-graph-query`.
