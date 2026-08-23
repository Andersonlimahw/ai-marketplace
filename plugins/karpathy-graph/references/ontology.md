# Ontology

Nine node types, eleven edge types. Fixed. Anything domain-specific goes in
`attrs`, never in a new type — a graph whose ontology drifts per project cannot
be queried by a shared skill.

## Node types

| Type | Is | Is not |
|---|---|---|
| `Entity` | a thing: person, org, service, module, concept | a statement about a thing |
| `Claim` | a statement that can be true or false | a thing |
| `Source` | a document, file, URL, transcript | the content of that document |
| `Artifact` | something a run produced: report, patch, dataset | a source it read |
| `AgentRun` | one bounded execution by one agent | the agent itself |
| `Evaluation` | a scored judgement against a rubric | an opinion |
| `Task` | a unit of planned work | work that already happened |
| `Commit` | a point in an experiment lineage | a code file |
| `Metric` | a named measurable quantity | a measured value |

Two distinctions worth stating explicitly, because they are the ones that get
collapsed:

**Entity vs Claim.** `Vendor X` is an entity. `Vendor X supplied Component Z` is
a claim. If the name contains a verb asserting something, it is a claim.

**Metric vs value.** `val_bpb` is a `Metric` node. `1.1023` is an `attrs` value
on an `Evaluation` or `Commit`. Do not create a node per measurement — you will
generate thousands of leaf nodes that connect to nothing.

## Edge types

| Predicate | Direction | Means |
|---|---|---|
| `MENTIONS` | Claim/Source → Entity | the subject refers to the entity |
| `SUPPORTS` | Source → Claim | the source is evidence for the claim |
| `CONTRADICTS` | Source/Claim → Claim | evidence against the claim |
| `DERIVED_FROM` | any → any | the subject was built from the object |
| `PRODUCED` | AgentRun → Artifact | the run authored the artifact |
| `EVALUATES` | Evaluation → any | the evaluation judged the object |
| `REVISES` | any → any | a newer version of the object |
| `SUPERSEDES` | any → any | replaces the object, which stays addressable |
| `DEPENDS_ON` | any → any | the subject requires the object |
| `PARENT_OF` | any → any | lineage: commits, tasks, decomposition |
| `RESOLVED_TO` | Entity → Entity | alias points at its canonical entity |

Direction is part of the meaning. `SUPPORTS` runs from evidence to claim, never
the reverse — invariant I1 checks for that direction.

## `REVISES` vs `SUPERSEDES`

- `REVISES` — same object, new version. The old version is history.
- `SUPERSEDES` — different object replacing this one. Both stay live.

Invariant I4 requires superseded objects to remain addressable. Never delete
one to "clean up" — retract the `SUPERSEDES` edge instead.

## Attributes

Common `attrs` keys the engine and skills understand:

| Key | On | Purpose |
|---|---|---|
| `inference` | Claim | `true` when reasoned, not read — satisfies I1 without a source |
| `rubric` | Evaluation | the criteria — required by I3 |
| `version` | Artifact | required by I2 |
| `result` | Evaluation | pass / fail / score |
| `uri` | Source | where the source lives |
| `rationale` | RESOLVED_TO | why the merge was made |
| `confidence` | any edge | 0.0–1.0, honest |

Everything else is free-form. Keep keys stable across a graph so queries can
rely on them.

## Two worked examples

### Incident investigation

```
(run_001:AgentRun) -PRODUCED-> (rca.md:Artifact)
(incident-report.md:Source) -SUPPORTS-> (Vendor X supplied Component Z:Claim)
(Vendor X supplied Component Z:Claim) -MENTIONS-> (Vendor X:Entity)
(Vendor X supplied Component Z:Claim) -MENTIONS-> (Component Z:Entity)
(Component Z involved in Incident Y:Claim) -MENTIONS-> (Incident Y:Entity)
(grounding gate:Evaluation) -EVALUATES-> (rca.md:Artifact)
```

The grounding question "did Vendor X's component cause Incident Y" is now a
path query, not a judgement call.

### Codebase map

```
(src/auth.ts:Source) -SUPPORTS-> (auth runs before routing:Claim)
(auth runs before routing:Claim) -MENTIONS-> (AuthMiddleware:Entity)
(AuthMiddleware:Entity) -DEPENDS_ON-> (TokenStore:Entity)
(api-latency:Metric) <-DEPENDS_ON- (perf gate:Evaluation)
```

## Rules

- Never invent node or edge types
- Never encode a statement as an entity name
- Never create a node per measurement
- Never point `SUPPORTS` backwards
- Never delete a superseded object
