---
name: karpathy-graph-extract
description: Stage 1 of the karpathy-graph pipeline. Turn unstructured context — documents, source files, incident timelines, chat logs, research notes — into typed entities and subject-predicate-object relations that fit the graph ontology. Use when the user asks to extract entities, pull relations out of documents, map a codebase into a graph, or when building a knowledge graph and no nodes exist yet.
metadata:
  version: 1.0.0
---

# Extract

Replace the classical NLP pipeline with one schema-constrained pass per
document. There is no trained NER model here — **the schema is the training
data**, and the ontology is the contract.

## Input contract

One unit of context at a time. A "unit" is whatever fits comfortably in one
pass with room for reasoning:

| Context | Unit |
|---|---|
| Documents | one document, or one section of a long one |
| Codebase | one module or package, not one file |
| Incident | one timeline, one postmortem |
| Research | one paper, one thread |

Never batch unrelated documents into one extraction call. Provenance gets
blurred and you cannot tell which source supported which claim.

## Output contract

Emit exactly this shape. Nothing else — no prose, no markdown fence commentary.

```json
{
  "nodes": [
    {
      "type": "Source",
      "name": "incident-2026-03-11.md",
      "uri": "./docs/incidents/incident-2026-03-11.md"
    },
    {
      "type": "Entity",
      "name": "Vendor X",
      "description": "component supplier named in the incident report",
      "aliases": ["VendorX Ltd", "Vendor-X"]
    },
    {
      "type": "Claim",
      "name": "Vendor X supplied Component Z",
      "description": "stated in the parts inventory section"
    }
  ],
  "edges": [
    {
      "predicate": "SUPPORTS",
      "source": "incident-2026-03-11.md",
      "target": "Vendor X supplied Component Z",
      "source_doc": "incident-2026-03-11.md#parts-inventory",
      "confidence": 0.92
    },
    {
      "predicate": "MENTIONS",
      "source": "Vendor X supplied Component Z",
      "target": "Vendor X"
    }
  ]
}
```

Edges may reference nodes by `name` or by `id`. Names resolve against the nodes
in the same payload first, then against the existing graph — so you can extract
without knowing what ids the engine will assign.

## Rules

**Always emit a `Source` node first.** Every document you read becomes one.
Every claim you extract must connect back to it. A payload with claims and no
source will fail `validate`.

**Separate entities from claims.** An entity is a thing (`Vendor X`,
`AuthMiddleware`, `val_bpb`). A claim is a statement about things
(`Vendor X supplied Component Z`). Do not encode a statement as an entity name.

**Capture aliases as you see them.** Abbreviations, former names, spelling
variants, casing differences. Resolution (stage 2) depends on this — an alias
you drop here is a merge that cannot happen later.

**Write descriptions that disambiguate.** Resolution uses descriptions as
contextual evidence. "Vendor X" is useless. "Component supplier named in the
2026-03-11 incident report" lets a later stage tell it apart from a different
Vendor X.

**Set honest confidence.** Explicitly stated in the text → 0.9–1.0. Strongly
implied → 0.7–0.9. Inferred across sentences → 0.5–0.7. Below 0.5, do not emit
it. Never round everything to 0.95 to look decisive.

**Mark inference explicitly.** A claim you reasoned to rather than read gets
`"inference": true` and no `Source` edge. Anything else is fabrication.

## What not to extract

- Boilerplate: licence headers, nav chrome, changelog scaffolding
- Restatements of something already extracted from the same source
- Entities that appear once with no relation — they become isolated nodes
- Anything you cannot point at a line or section for

Precision beats recall here. A missed entity is a gap; a fabricated one
contaminates every traversal that touches it.

## Codebase extraction

When the context is source code, map it like this:

| Code concept | Node |
|---|---|
| Module, service, package | `Entity` |
| The file itself | `Source` |
| Architectural fact ("auth runs before routing") | `Claim` |
| Build output, generated report | `Artifact` |
| Test suite, benchmark | `Evaluation` |
| Latency, coverage, bundle size | `Metric` |

Imports and calls become `DEPENDS_ON`. Derivation and forks become
`DERIVED_FROM`. Do not create an edge type for every code relationship — the
ontology is fixed.

## Handing off

Write the payload to a file and pass it to the engine:

```bash
KG="${CLAUDE_PLUGIN_ROOT:-plugins/karpathy-graph}/scripts/kgraph.py"
python3 "$KG" --name "<graph>" --run-id "$RUN_ID" ingest @extraction.json
```

The response reports `nodes_added`, `edges_added`, and any
`invariant_violations`. **A non-empty violations list means your payload was
malformed** — fix the extraction, do not proceed to resolution.

Next stage: `karpathy-graph-resolve`.
