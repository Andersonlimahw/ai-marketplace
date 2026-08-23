---
name: karpathy-graph-swarm
description: Fan the karpathy-graph pipeline out across parallel agents that share the graph as memory instead of copying transcripts. Use when the context is too large for one pass — hundreds of documents, a whole codebase, many independent hypotheses — or when the user asks to parallelize graph construction, run a swarm, or use multiple agents to build a graph.
metadata:
  version: 1.0.0
---

# Swarm

Scale out only when the work is genuinely parallel **and the reducer is defined
before fan-out**. More agents without a reducer produces activity, not progress.

The graph is what makes the swarm coherent: workers write findings as structured
updates, and a synthesizer traverses the graph to combine them even though no
single worker saw all the sources.

## Before fanning out

Answer all six. If any answer is missing, do not fan out yet.

1. **Is the work independent?** Overlapping units mean duplicate entities and a
   resolution problem you created yourself.
2. **What is the reducer?** How do N worker payloads become one graph? Decide
   now, not after.
3. **What is the artifact contract?** Every worker returns the same shape.
4. **What are the budgets?** Concurrency, worker cap, tokens, per-worker
   timeout, retries.
5. **What is the dedup policy?** Same entity from two workers — merge how?
6. **What is the final gate?** What must be true for the graph to ship?

## Partition

Give each worker a unit that stands alone: one document, one module, one
incident, one hypothesis. Never split a single document across workers —
provenance blurs and neither worker sees enough context to resolve entities.

Overlap is not free. Two workers on the same source produce two surface forms of
every entity, and stage 2 has to clean it up.

## The write protocol

**Workers never touch graph files.** They return payloads. The orchestrator
validates and applies them. That is what keeps the orchestrator's context clean
— it never reads a worker transcript, only structured updates.

Worker output:

```json
{
  "run_id": "run_007",
  "agent_id": "extractor-07",
  "nodes": [{"type": "Source", "name": "doc-07.md"}, "…"],
  "edges": [{"predicate": "SUPPORTS", "source": "doc-07.md", "target": "…"}]
}
```

Orchestrator applies it:

```bash
KG="${CLAUDE_PLUGIN_ROOT:-plugins/karpathy-graph}/scripts/kgraph.py"
python3 "$KG" --name "<graph>" --run-id run_007 ingest @worker-07.json
```

One `--run-id` per worker. Every node and edge carries it, so a bad worker's
writes can be found and retracted without touching anyone else's.

## Serialize the writes

The store is append-only and single-writer. **Run workers in parallel; apply
their payloads sequentially.** Extraction is the expensive part and it
parallelizes; ingestion is fast and does not need to.

```bash
# workers run concurrently, each writing its own payload file
for i in $(seq 1 16); do
  extract_worker "$i" > "worker-$i.json" &
done
wait

# orchestrator applies them one at a time
for i in $(seq 1 16); do
  python3 "$KG" --name "<graph>" --run-id "run_$i" ingest "@worker-$i.json"
done
```

Do not have sixteen agents call `ingest` simultaneously.

## Roles

Split roles only when specialization adds signal:

| Role | Returns |
|---|---|
| Extractor | typed nodes and edges from one unit |
| Resolver | canonical clusters with rationales |
| Verifier | supported / unsupported per claim, with edge citations |
| Synthesizer | one cited report traversing the assembled graph |

A verification wave only helps if the verifiers have a **different prompt,
evidence set, or role** than the extractors. Running the same prompt twice
produces correlated errors and false confidence.

## Reduce

After all payloads are applied:

```bash
python3 "$KG" --name "<graph>" query "" --type Entity --max-nodes 300  # find duplicates
# resolve clusters — see karpathy-graph-resolve
python3 "$KG" --name "<graph>" validate
python3 "$KG" --name "<graph>" render
```

Parallel extraction always produces duplicate surface forms. That is expected,
not a failure — resolution is the reducer.

## Budget, and what to do when it runs out

Declare limits up front:

```bash
python3 "$KG" --name "<graph>" init \
  --budget '{"max_agents":16,"max_documents":200,"max_tokens":500000,"max_retries":2}'
```

Large fan-out consumes tokens fast. When the budget is exhausted, return:

- the best current graph
- what completed
- what is unresolved
- **why you stopped**

Do not hide partial failure behind a fluent final answer. A report that reads as
complete over half a corpus is the expensive failure mode here.

## When not to swarm

Some work needs one coherent context. Architecture decisions, tightly coupled
reasoning, and narrative synthesis degrade when split into isolated units —
each worker sees a fragment and none sees the argument.

Fan out extraction. Keep synthesis whole.

If the corpus is small enough for one pass, one agent is faster, cheaper, and
produces a cleaner graph. Say so instead of parallelizing for its own sake.
