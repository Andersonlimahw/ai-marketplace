---
name: graph-feature-architect
description: "Plan new feature implementations grounded in the project's existing knowledge graph (graphify-out/ or a karpathy-graph output) instead of ad-hoc grepping. Use when a graph already exists for the target codebase and the user wants to plan, scope, or architect a feature that plausibly touches more than one module — surfaces god nodes, community boundaries, and cross-file relationships before any code is written. If no graph exists yet, this skill says so and defers to building one (graphify update . or the karpathy-graph plugin) rather than guessing relationships."
---

# Graph Feature Architect

Minimal skeleton, recreated after the original plugin was removed from the hub while consumer repos still symlinked to it. See `agents/graph-feature-architect.md` for the operating flow: locate the graph, scope the feature into 1-3 graph queries, rank blast radius, sequence the plan leaf-to-god-node, and report honestly when the graph is missing or stale.

Use `karpathy-graph` first if no graph exists yet — this plugin only plans against a graph that is already built.
