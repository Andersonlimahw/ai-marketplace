# Decision framework

Answer these before building anything. Most of the cost of a graph system is
paid by teams that needed a table.

## Six selection questions

1. **Can success be verified?** If not, do not begin with autonomy. Define a
   test, a rubric, a source requirement, or a human decision point first.
2. **Are the steps stable?** Yes → a chain. No → planning or an orchestrator.
3. **Are subtasks independent?** Yes → parallelize. No → model the dependencies
   and limit concurrent writes.
4. **Must alternative lineages stay available?** Yes → a DAG. Do not force every
   result into one branch.
5. **Must facts survive the run?** Yes → persist artifacts and graph state. Do
   not rely on transcript summaries.
6. **Can you afford the cost and latency?** Set budgets before adding workers.

## When a graph is the wrong tool

Skip it when:

- tasks are independent and share no state
- no cross-session state is required
- every answer comes from a single document
- relations are fixed and simple
- a relational table answers every query
- provenance is not needed
- extraction errors would outweigh the value of traversal

That last one decides more cases than people expect. If your corpus is noisy
enough that extraction will be wrong 30% of the time, a graph industrializes
those errors and makes them look authoritative.

**Say so and stop.** Recommending against a graph is a valid outcome.

## When a graph earns its cost

- questions span several facts and sources (multi-hop)
- relations evolve and contradictions need tracking
- provenance is required — every claim must trace to a source
- multiple agents need shared world state
- work continues across sessions
- the same entities recur across many documents

## Choosing the architecture level

| Situation | Start with | Why |
|---|---|---|
| Simple low-risk question | zero-shot | lowest latency |
| Output can be checked | loop | repeated feedback improves the artifact |
| Stable sequence | chain | predictable, testable stages |
| Clear categories | router | separates policies and models |
| Independent units | parallel | reduces wall-clock time |
| Variable decomposition | orchestrator-workers | dynamic specialization |
| Alternatives must stay alive | commit DAG | preserves experiment branches |
| Facts must survive sessions | knowledge graph | persistent shared memory |
| Very large parallel work | dynamic workflow | automates fan-out and fan-in |

Each level addresses a specific limitation of the previous one: the loop
addresses single-pass errors, tools address knowledge gaps, planning addresses
complexity, multi-agent addresses perspective limits, the DAG addresses lineage,
and the knowledge graph addresses persistent shared memory.

The progression is directional, not mandatory. Do not skip to the end.

## Commit DAG and knowledge graph are complementary

Do not collapse them.

| | Answers |
|---|---|
| **Commit DAG** | what changed, which experiment is the parent, which agent produced it, which lineages are active |
| **Knowledge graph** | which entities exist, how they relate, which sources support them, which claims conflict |

A production system connects the two:

```
(agent_run_183) -PRODUCED-> (claim_441)
(claim_441) -DERIVED_FROM-> (commit_a81f)
(claim_441) -MENTIONS-> (entity_autoresearch)
(claim_441) -SUPPORTS-> (source_readme)
(claim_441) -SUPERSEDES-> (claim_238)
(evaluation_92) -EVALUATES-> (claim_441)
```

## Complexity budget

Every run declares: maximum model calls, sub-agents, concurrent workers, tool
calls, wall-clock time, tokens, financial cost, retries, graph writes, and the
minimum evidence required to finalize.

When the budget is exhausted, return the best current artifact, the completed
work, the unresolved issues, and the reason for stopping.

**Do not hide partial failure behind a fluent final answer.**

## Five planes

Keep them separate. The point is that no single chat transcript becomes the
database, the workflow engine, and the audit log at once.

| Plane | Holds |
|---|---|
| Control | objectives, plans, budgets, stop decisions |
| Execution | tools, tests, sub-agents in isolated environments |
| Artifact | plans, drafts, changes, reports as immutable versions |
| Graph | entities, claims, relations, provenance, lineage |
| Evaluation | deterministic checks, model evaluators, human review |

This plugin implements the **graph plane**. It does not replace the other four.

## The test that matters

A reliable system makes this statement true:

> Every important output can be traced to an objective, a plan, an artifact, a
> source, a graph path, an evaluator decision, and a bounded execution record.

When it is false, adding more agents increases opacity. When it is true, loops,
swarms, DAGs, and graphs become composable mechanisms rather than opaque
behaviour.
