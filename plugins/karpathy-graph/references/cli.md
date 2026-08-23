# CLI reference

One stdlib-only Python file. No dependencies, no network. Every command prints
a single JSON object to stdout.

```bash
KG="${CLAUDE_PLUGIN_ROOT:-plugins/karpathy-graph}/scripts/kgraph.py"
python3 "$KG" --help
```

## Global flags

| Flag | Purpose |
|---|---|
| `--name <name>` | graph name; resolves to `./.karpathy-graphs/<slug>/` |
| `--path <dir>` | explicit directory; **overrides** `--name` |
| `--run-id <id>` | provenance stamp on every node and edge written |

Pass `--run-id` on every write. It is the only way to trace a bad batch.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | success |
| 1 | `validate` or `selftest` failed |
| 2 | user error (bad type, missing node, malformed payload) |
| 3 | unexpected error |

`validate` returning 1 is the signal to wire into CI or a loop.

## Commands

### `init`

```bash
python3 "$KG" --name "Payments" init \
  --objective "trace vendors to incidents" \
  --budget '{"max_documents":200,"max_agents":16}'
```

Fails if a graph already exists there. Nothing is overwritten silently.

### `add-node`

```bash
python3 "$KG" --name "Payments" --run-id run_1 add-node \
  --type Entity --name "Vendor X" \
  --description "component supplier" \
  --attr 'aliases=["VendorX Ltd"]' \
  --attr region=EU
```

`--attr` values are parsed as JSON when possible, otherwise kept as strings.
Same type and name upserts and bumps `version` rather than duplicating.

### `add-edge`

```bash
python3 "$KG" --name "Payments" --run-id run_1 add-edge \
  --predicate SUPPORTS --source <src_id> --target <claim_id> \
  --source-doc "report.md#parts" --confidence 0.92
```

Both endpoints must already exist, or it errors.

### `ingest`

The main write path. Accepts inline JSON, `@file.json`, or `@-` for stdin.

```bash
python3 "$KG" --name "Payments" --run-id run_1 ingest @extraction.json
cat extraction.json | python3 "$KG" --name "Payments" --run-id run_1 ingest @-
```

Payload shape:

```json
{
  "nodes": [{"type": "Entity", "name": "Vendor X", "aliases": ["VendorX Ltd"]}],
  "edges": [{"predicate": "MENTIONS", "source": "<claim name or id>", "target": "Vendor X"}]
}
```

Edges resolve endpoints by id or by name — payload nodes first, then the
existing graph. Returns `nodes_added`, `edges_added`, `invariant_violations`,
and `stats`.

### `resolve`

```bash
python3 "$KG" --name "Payments" --run-id run_1 resolve \
  --canonical <canonical_id> --alias <alias_id> --alias <other_id> \
  --rationale "same supplier; shared source section"
```

Reversible: alias nodes stay addressable, each gains a `RESOLVED_TO` edge
carrying the rationale. The canonical entity absorbs aliases and `source_docs`.

### `query`

```bash
python3 "$KG" --name "Payments" query "vendor" \
  --type Entity --hops 2 --max-nodes 40 \
  --edge-type SUPPORTS --edge-type MENTIONS \
  --format context
```

| Flag | Default | Purpose |
|---|---|---|
| `--type` | any | restrict seed nodes to one node type |
| `--hops` | 2 | traversal radius |
| `--max-nodes` | 60 | hard cap; sets `truncated: true` when hit |
| `--edge-type` | all | repeatable; restrict traversal |
| `--format` | json | `json`, `triples`, or `context` |

`context` and `triples` print text, not JSON — they are meant to be pasted into
a prompt. Check `truncated` before treating a result as complete.

### `path`

```bash
python3 "$KG" --name "Payments" path <source_id> <target_id> --max-depth 6
```

Shortest provenance route. Returns `found`, `hops`, the ordered edge list, and
`citations` (edge ids). This is the grounding primitive — use it instead of
asking a model whether a claim holds.

### `validate`

```bash
python3 "$KG" --name "Payments" validate
```

Checks I1–I4. Exit 1 on any violation. Each violation names the invariant, the
node, and what is wrong.

### `stats`

```bash
python3 "$KG" --name "Payments" stats
```

Nodes, edges, density, components, isolated nodes, counts by type.

### `render`

```bash
python3 "$KG" --name "Payments" render
```

Writes `REPORT.md`, `graph.html`, `graph.mmd`. Run after every build.

### `retract`

```bash
python3 "$KG" --name "Payments" retract --edge <edge_id>
python3 "$KG" --name "Payments" retract --node <node_id>
```

Appends a reversal event; never rewrites history. Retracting a node also drops
its edges. Undo a false merge by retracting its `RESOLVED_TO` edge.

### `list`

```bash
python3 "$KG" list
```

Every graph under `./.karpathy-graphs/` with counts and timestamps.

### `selftest`

```bash
python3 "$KG" selftest
```

End-to-end check in a temp directory: invariants, reversibility, resolution,
traversal, paths, rendering, log replay, ingest, path resolution. Exit 1 on any
failure. Run it after touching the engine.

## Files

| File | Role |
|---|---|
| `log.jsonl` | append-only event log — **the source of truth** |
| `graph.json` | materialized graph, rebuilt from the log |
| `manifest.json` | name, objective, budget, counters |
| `REPORT.md` | health and composition |
| `graph.html` | interactive explorer |
| `graph.mmd` | Mermaid diagram |

`graph.json` is derived. Delete it and `render` rebuilds it from the log.
Delete `log.jsonl` and the history is gone — never do that.
