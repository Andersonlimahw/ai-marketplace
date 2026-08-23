---
name: karpathy-graph-query
description: Stage 4 of the karpathy-graph pipeline. Answer multi-hop questions from a knowledge graph by retrieving a bounded subgraph with edge citations, and ground or refute claims against actual graph paths. Use when the user asks a question that spans several facts, asks how two things connect, asks to verify or ground a claim, or when an agent needs task-specific context from an existing graph.
metadata:
  version: 1.0.0
---

# Query

The graph exists so agents stop replaying transcripts. That only works if
retrieval stays **bounded**.

## The rule

**Never dump the graph into a prompt.**

Not `graph.json`, not the full node list, not "just this once because it's
small". Retrieve the connected state needed for the current decision, and
nothing else. A graph used as a context dump is worse than no graph — it costs
the same tokens plus the build.

## Retrieval procedure

1. Resolve the entities the question mentions
2. Expand one or two hops over the edge types that matter
3. Filter by type, source, or date when the question implies it
4. Serialize within a token budget
5. Keep the edge ids so the answer can cite them

```bash
KG="${CLAUDE_PLUGIN_ROOT:-plugins/karpathy-graph}/scripts/kgraph.py"

python3 "$KG" --name "<graph>" query "vendor X" \
  --hops 2 \
  --edge-type SUPPORTS --edge-type MENTIONS \
  --max-nodes 40 \
  --format context
```

## Choosing hops

| Hops | Use for |
|---|---|
| 1 | "what is directly attached to X" |
| 2 | most questions — the default |
| 3 | explicit multi-hop chains (X → Y → Z) |
| 4+ | almost never; you are retrieving the whole graph with extra steps |

If two hops returns nothing useful, the problem is usually missing edges, not
an insufficient radius. Widening the radius to compensate for a thin graph
retrieves noise.

## Output formats

**`--format context`** — entities plus relations with `[edge:...]` citations.
This is what you paste into a worker's prompt.

```
## Entities

- [Entity] Vendor X (aliases: VendorX Ltd) — component supplier `ent_0269238d2ffa`
- [Claim] Vendor X supplied Component Z `cla_f9ab59811007`

## Relations

(incident-report.md) -SUPPORTS-> (Vendor X supplied Component Z) (src: incident-report.md)  [edge:e_22a78d1f9eeb]
(Vendor X supplied Component Z) -MENTIONS-> (Vendor X)  [edge:e_401a5179c882]
```

**`--format triples`** — relations only, when entity descriptions are noise.

**`--format json`** — full node and edge objects, for programmatic use.

Watch for `"truncated": true`. It means `--max-nodes` cut the neighbourhood —
either raise the budget deliberately or narrow the question. **Never present a
truncated result as complete.**

## Grounding a claim

To verify "Vendor X supplied the component involved in Incident Y", ask the
graph for a path, not a model for an opinion.

```bash
python3 "$KG" --name "<graph>" path <vendor_x_id> <incident_y_id>
```

**Path found** — the claim is supported. Cite the returned edge ids.

**No path** — return structured feedback naming the missing evidence:

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

This is actionable. "I could not verify this" is not.

## Answering discipline

A valid multi-hop answer must:

- resolve the question's entities correctly
- use only edges that exist in the retrieved subgraph
- respect source and time constraints in the question
- **distinguish fact from inference** — say which is which
- cite the edge ids it used
- name what evidence is missing

Both the answer and the path are being evaluated. A fluent answer citing
irrelevant edges is a failure, not a partial success.

## When the graph cannot answer

Say so. Then say precisely what is missing: which entity is absent, which
relation has no source, which document was never ingested.

Do not fall back to model priors and present the result as graph-grounded. The
whole point of the graph plane is that answers are traceable — an untraceable
answer wearing a citation is the failure mode this system exists to prevent.

Next stage: `karpathy-graph-evaluate`.
