---
name: karpathy-graph-resolve
description: Stage 2 of the karpathy-graph pipeline. Collapse duplicate surface forms into canonical entities using context as evidence, reversibly and with a recorded rationale. Use after extraction when the graph contains aliases, abbreviations, or spelling variants of the same thing, when isolated-node count is high, or when the user asks to deduplicate or merge entities.
metadata:
  version: 1.0.0
---

# Resolve

Extraction creates **surface forms**, not a clean graph. The same thing appears
as an abbreviation, an alias, a former name, a spelling variant, or a partial
name. Resolution decides which of those are the same entity.

This is a reasoning task, not a string-matching task.

## Why string similarity is not enough

It fails in both directions:

- **Misses:** "Edwin Aldrin" and "Buzz Aldrin" share zero character overlap and
  are the same person.
- **False merges:** two different people named "J. Silva" have perfect overlap
  and are not the same person.

A false merge is the more expensive error. Collapse two entities into one node
and every downstream traversal silently combines their relations, dates, and
sources. Nothing errors. The graph just becomes confidently wrong.

**When uncertain, do not merge.** An unmerged duplicate is visible and fixable.
A false merge is invisible.

## Procedure

### 1. Block by type

Only ever compare entities of the same `type`. An `Entity` never resolves to a
`Source`, a `Metric` never resolves to a `Claim`.

```bash
KG="${CLAUDE_PLUGIN_ROOT:-plugins/karpathy-graph}/scripts/kgraph.py"
python3 "$KG" --name "<graph>" query "" --type Entity --max-nodes 200
```

### 2. Narrow with cheap signals

Before spending reasoning on candidates, group by anything cheap: shared token,
shared acronym, edit distance, one name being a substring of another, shared
`source_docs`. This is blocking, not deciding — it builds the candidate set.

### 3. Decide with context

For each candidate cluster, weigh the evidence that actually discriminates:

| Evidence | Weight |
|---|---|
| Descriptions describe the same thing | strong |
| Same `source_docs`, same section | strong |
| Alias lists overlap | strong |
| Neighbours in the graph overlap | moderate |
| Names look similar | weak on its own |

Ask: *would a careful human reading both descriptions conclude these are the
same thing?* If the honest answer is "probably", that is a no.

### 4. Merge reversibly

```bash
python3 "$KG" --name "<graph>" --run-id "$RUN_ID" resolve \
  --canonical <canonical_id> \
  --alias <alias_id> --alias <other_alias_id> \
  --rationale "both describe the component supplier in the 2026-03-11 incident; shared source section"
```

The engine keeps every alias node addressable and adds a `RESOLVED_TO` edge
carrying the rationale. Nothing is destroyed. The canonical entity absorbs the
aliases' names and `source_docs`.

**The rationale is mandatory.** "duplicate" is not a rationale. Write the
evidence that convinced you, so a human — or a later agent — can audit or
reverse the decision.

### 5. Undo a bad merge

```bash
python3 "$KG" --name "<graph>" retract --edge <resolved_to_edge_id>
```

One edge. That is the whole cost of reversing a merge, which is exactly why the
merge must never destroy the alias node.

## Reading the metrics

After resolving, check `REPORT.md`:

**Compression ratio** = surface forms ÷ canonical entities.

A high ratio is **not** automatically good. Over-merging produces a connected
graph that is false. Watch the direction of travel:

| Change | Likely cause |
|---|---|
| Isolated nodes jump up | resolution regressed, or extraction produced orphans |
| Isolated nodes drop sharply | possible over-merging |
| Components collapse toward 1 | check for false merges before celebrating |
| Compression ratio > 3 | inspect a sample of merges by hand |

Sample and verify. Do not trust an aggregate that only rewards merging.

## Do not resolve

- Entities whose descriptions are empty on both sides — extract better first
- Anything where the only evidence is name similarity
- Across types, ever
- In bulk without recording per-cluster rationales

Next stage: `karpathy-graph-build`.
