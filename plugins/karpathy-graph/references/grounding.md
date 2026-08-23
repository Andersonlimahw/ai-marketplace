# Grounding

Grounding is checking a claim against graph edges instead of against a model's
confidence. The difference matters: a model asked "is this true?" produces an
opinion; the graph produces a path or the absence of one.

## The check

```bash
KG="${CLAUDE_PLUGIN_ROOT:-plugins/karpathy-graph}/scripts/kgraph.py"
python3 "$KG" --name "<graph>" path <source_entity_id> <target_entity_id>
```

**Found** → supported. Cite the returned edge ids.

**Not found** → unsupported. Return structured feedback, not a critique.

## Structured feedback

```json
{
  "decision": "revise",
  "claim": "Vendor X supplied the component involved in Incident Y",
  "reason": "No supported path from Vendor X to Incident Y",
  "required_evidence": [
    "A source-backed supplied relation from Vendor X to a component",
    "A source-backed involved_in relation from that component to Incident Y"
  ]
}
```

This is actionable — it names the two edges that would settle the question. A
free-form "I could not verify this claim" is not, because the next agent has to
re-derive what was missing.

`decision` is one of `approve`, `revise`, or `reject`:

| Decision | When |
|---|---|
| `approve` | a supported path exists and the cited edges are relevant |
| `revise` | evidence is missing but obtainable — name it |
| `reject` | the graph contains a `CONTRADICTS` edge against the claim |

## Fact versus inference

Every grounded answer must separate the two.

- **Fact** — supported by edges you cite
- **Inference** — reasoned across the gap between edges

State which is which in the answer. An inference presented as a fact with a
nearby citation is the exact failure this system exists to prevent.

Claims stored as inference carry `inference=true` and no `Source` edge. That
satisfies invariant I1 honestly rather than by inventing a source.

## Evaluating the answer, not just the verdict

A valid grounded answer must:

1. resolve the question's entities correctly
2. retrieve a relevant subgraph
3. use only supported edges
4. respect time and source constraints in the question
5. distinguish fact from inference
6. cite the edge ids used
7. identify what evidence is missing

Both the answer **and the path** are evaluated. A fluent answer citing
irrelevant edges scores worse than an honest "not supported, here is what's
missing" — it is wrong in a way that is harder to detect.

## Recording the gate

Make the evaluation auditable by putting it in the graph:

```bash
python3 "$KG" --name "<graph>" --run-id "$RUN" add-node \
  --type Evaluation --name "grounding gate $RUN" \
  --attr rubric="every claim in the artifact cites a supported edge" \
  --attr result="revise"

python3 "$KG" --name "<graph>" --run-id "$RUN" add-edge \
  --predicate EVALUATES --source <eval_id> --target <artifact_id>
```

Invariant I3 requires the rubric. An evaluation that does not state its criteria
is an opinion wearing a node type.

## Contradictions

When two sources disagree, do not silently pick one. Record both and link the
conflict:

```bash
python3 "$KG" --name "<graph>" --run-id "$RUN" add-edge \
  --predicate CONTRADICTS --source <claim_b_id> --target <claim_a_id> \
  --source-doc "audit-2026-04.md"
```

The graph preserves claims, sources, and relationships so they can be
inspected. **It does not convert claims into truth.** Surfacing a live
contradiction to a human is a correct outcome, not an unfinished one.
