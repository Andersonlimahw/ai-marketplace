---
name: karpathy-graph-visualize
description: Render a karpathy-graph for humans — an interactive HTML explorer, a Mermaid diagram for docs and PRs, and a health report — then explain what the picture actually shows. Use when the user asks to see, visualize, draw, or open the graph, wants a diagram for documentation, or asks what the graph looks like.
metadata:
  version: 1.0.0
---

# Visualize

The graph is machine memory. This is the part humans read.

Agents query subgraphs; a human needs to see the shape — where the clusters
are, what is disconnected, which nodes carry the structure, where provenance is
thin.

## Render

```bash
KG="${CLAUDE_PLUGIN_ROOT:-plugins/karpathy-graph}/scripts/kgraph.py"
python3 "$KG" --name "<graph>" render
```

Three artifacts, one command:

| File | For | Notes |
|---|---|---|
| `graph.html` | exploring | self-contained, no network, no dependencies |
| `graph.mmd` | docs and PRs | Mermaid; renders on GitHub |
| `REPORT.md` | reviewing | health, composition, violations |

Run this after **every** build. A stale `graph.html` is worse than none — a
human will trust it.

## The HTML explorer

Open it directly in a browser:

```bash
open ./.karpathy-graphs/<slug>/graph.html          # macOS
xdg-open ./.karpathy-graphs/<slug>/graph.html      # Linux
```

It embeds the graph data inline, so it works offline and can be attached to an
issue or emailed.

What it does:

- **Header pills** — nodes, edges, components, invariant violations. The
  violations pill turns red when non-zero.
- **Force-directed layout** — deterministic, so the same graph renders the same
  way twice. Disconnected components are packed rather than flung apart.
- **Node size = degree** — the structural hubs are visually obvious.
- **Node colour = type** — nine types, nine colours.
- **Click a node** — highlights its neighbourhood, dims the rest, and shows
  type, id, description, aliases, sources, run id, degree, and every incident
  edge with direction.
- **Search** — filters by name, type, or description; edges follow.
- **Type legend** — click to toggle a type off, to see structure without noise.
- **Pan and zoom** — drag, scroll.

Labels are shown for the highest-degree nodes only. Labelling all of them turns
a mid-size graph into unreadable overlapping text; hover or click for the rest.

## Mermaid

`graph.mmd` drops straight into markdown:

````markdown
```mermaid
graph LR
  ent_0269238d2ffa["Entity: Vendor X"]
  cla_f9ab59811007["Claim: Vendor X supplied Component Z"]
  cla_f9ab59811007 -->|MENTIONS| ent_0269238d2ffa
```
````

It caps at 120 nodes and says so in a comment when it truncates. Past that,
Mermaid becomes unreadable anyway — use a filtered subgraph:

```bash
python3 "$KG" --name "<graph>" query "<focus>" --hops 2 --format triples
```

## Reading the picture

Teach the user what they are looking at. The visual is diagnostic, not
decorative.

| What you see | What it means |
|---|---|
| A few large hubs | healthy — those are the entities the domain turns on |
| Many small islands | fragmented corpus, or resolution is under-merging |
| One dense blob | possible over-merging — inspect the merges |
| Scattered dots, no edges | extraction produced entities but missed relations |
| Green `Source` nodes barely connected | claims are not being tied to evidence |
| Red violations pill | a malformed write — fix before sharing |

One connected component is **not** the goal. A connected but false graph is
worse than an honest fragmented one.

## Reporting to the user

Give them the path, the shape, and the caveat:

> Graph at `./.karpathy-graphs/payments-incident/`
> 40 nodes, 49 edges, 2 components, 0 invariant violations.
> Open `graph.html` — the hubs are Knowledge Graph and Entity Resolution.
> The second component is the five planes, which nothing links to the incident
> corpus yet: no document mentions both.

That last sentence is the useful one. Say what the picture reveals is
**missing**, not just what it contains.
