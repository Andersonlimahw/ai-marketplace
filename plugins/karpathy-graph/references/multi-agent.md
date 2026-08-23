# Multi-agent contract

How several agents share one graph without corrupting it or each other's
context. This is the operational detail behind `karpathy-graph-swarm`.

## The core rule

**Workers return payloads. The orchestrator writes.**

Workers never call `add-node`, `add-edge`, or `ingest` against the shared graph.
They emit a `GraphUpdate` and hand it back. The orchestrator validates and
applies it.

This is what keeps the orchestrator's context clean: it reads structured
updates, never worker transcripts. That property is the entire reason the graph
plane exists.

## GraphUpdate

```json
{
  "run_id": "run_007",
  "agent_id": "extractor-07",
  "nodes": [
    {"type": "Source", "name": "doc-07.md", "uri": "./docs/doc-07.md"},
    {"type": "Entity", "name": "Vendor X", "aliases": ["VendorX Ltd"]}
  ],
  "edges": [
    {"predicate": "MENTIONS", "source": "doc-07.md", "target": "Vendor X",
     "source_doc": "doc-07.md#3", "confidence": 0.9}
  ]
}
```

Every worker returns this shape. No prose, no partial payloads, no "I also
noticed…" commentary outside the schema.

## Applying updates

```bash
KG="${CLAUDE_PLUGIN_ROOT:-plugins/karpathy-graph}/scripts/kgraph.py"
python3 "$KG" --name "<graph>" --run-id run_007 ingest @worker-07.json
```

The engine validates schema, node types, edge types, and endpoint resolution
before anything is written. A malformed payload is rejected whole — there are no
half-applied updates.

## Concurrency

The store is append-only and **single-writer**.

- Extraction runs in parallel — it is the expensive part
- Ingestion runs sequentially — it is fast and does not need parallelism

```bash
for i in $(seq 1 16); do
  extract_worker "$i" > "worker-$i.json" &
done
wait

for i in $(seq 1 16); do
  python3 "$KG" --name "<graph>" --run-id "run_$i" ingest "@worker-$i.json"
done
```

Sixteen concurrent `ingest` calls will interleave writes to `log.jsonl`. Do not
do it.

If agents must genuinely write concurrently, give each its own graph directory
and merge afterwards by ingesting each one's payloads into a target graph.

## Provenance per run

Every node and edge carries the `run_id` that created it. That makes a bad batch
traceable and reversible:

```bash
python3 "$KG" --name "<graph>" query "" --format json \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print([n['id'] for n in d['nodes'] if n.get('run_id')=='run_007'])"

python3 "$KG" --name "<graph>" retract --node <id>
```

Record the run itself as a node so the lineage is queryable:

```bash
python3 "$KG" --name "<graph>" --run-id run_007 add-node \
  --type AgentRun --name run_007 \
  --attr agent=extractor-07 --attr unit=doc-07.md
```

## Handoff contracts

Every handoff is an artifact contract, not a conversation.

| Role | Returns |
|---|---|
| Extractor | `GraphUpdate` for one unit |
| Resolver | canonical clusters with per-cluster rationales |
| Verifier | supported / unsupported per claim, with edge citations |
| Synthesizer | one cited report traversing the assembled graph |

A reviewer returns **criterion-level defects**, never "looks good". A verdict
without criteria cannot be acted on or audited.

Use worktree isolation when multiple coding agents modify the same repository.

## Correlated errors

Parallel workers running the same prompt make the same mistakes, and agreement
between them reads as confidence. It is not.

A verification wave only adds signal when verifiers differ in **prompt, evidence
set, or role** from the workers they check. Three identical verifiers are one
verifier with extra cost.

## Context construction per worker

Each worker gets a task-specific subgraph, never the whole graph:

1. resolve the entities named in its task
2. expand one or two hops over allowed edge types
3. include current artifact versions
4. prioritize recent verified claims
5. include known conflicts and uncertainty
6. serialize within a token budget
7. attach stable edge ids for citation

```bash
python3 "$KG" --name "<graph>" query "<worker task entities>" \
  --hops 2 --max-nodes 40 --format context
```

The graph must not become a new form of context dumping. If a worker's prompt
contains most of the graph, the architecture has failed its purpose.

## Budget and stopping

Set before fan-out: concurrency limit, worker cap, token budget, per-worker
timeout, retry policy, evidence contract, dedup policy, final evaluation gate.

When exhausted, return the best current graph, what completed, what is
unresolved, and why you stopped. Never present a partial run as a complete one.
