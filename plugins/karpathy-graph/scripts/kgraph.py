#!/usr/bin/env python3
"""kgraph — Karpathy Graph Engineering store.

Stdlib-only CLI that any AI harness (Claude Code, Codex, OpenCode, Antigravity,
Gemini, ...) can drive as a subprocess. It implements the graph plane described
in "Karpathy: Graph Engineering Systems":

  - typed nodes  (Entity, Claim, Source, Artifact, AgentRun, Evaluation,
                  Task, Commit, Metric)
  - typed edges  (MENTIONS, SUPPORTS, CONTRADICTS, DERIVED_FROM, PRODUCED,
                  EVALUATES, REVISES, SUPERSEDES, DEPENDS_ON, PARENT_OF,
                  RESOLVED_TO)
  - four write invariants (see INVARIANTS)
  - bounded subgraph retrieval instead of whole-graph context dumping
  - append-only, reversible history so a bad merge can be undone

Storage layout (default root: ./.karpathy-graphs/<graph_name>/):

    graph.json      materialized graph (nodes + edges), rebuilt from log
    log.jsonl       append-only event log — the source of truth
    manifest.json   graph metadata, budget, counters
    REPORT.md       human-readable summary            (written by `render`)
    graph.html      interactive visual explorer       (written by `render`)
    graph.mmd       Mermaid diagram                   (written by `render`)

Every command prints a single JSON object to stdout so agents can parse it.
"""

from __future__ import annotations

import argparse
import hashlib
from html import escape as html_escape
import json
import os
import re
import sys
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = "1.0.0"
DEFAULT_ROOT = ".karpathy-graphs"

NODE_TYPES = (
    "Entity",
    "Claim",
    "Source",
    "Artifact",
    "AgentRun",
    "Evaluation",
    "Task",
    "Commit",
    "Metric",
)

EDGE_TYPES = (
    "MENTIONS",
    "SUPPORTS",
    "CONTRADICTS",
    "DERIVED_FROM",
    "PRODUCED",
    "EVALUATES",
    "REVISES",
    "SUPERSEDES",
    "DEPENDS_ON",
    "PARENT_OF",
    "RESOLVED_TO",
)

INVARIANTS = (
    "I1: every Claim has a source edge (SUPPORTS/DERIVED_FROM from a Source) "
    "or is explicitly marked inference=true",
    "I2: every Artifact has an authoring run (AgentRun -PRODUCED-> Artifact) "
    "and a version",
    "I3: every Evaluation identifies a rubric",
    "I4: every superseded object remains addressable "
    "(SUPERSEDES targets must still exist)",
)

SLUG_RE = re.compile(r"[^a-z0-9]+")


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


class KGraphError(Exception):
    """User-facing error; reported as JSON with ok=false."""


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slugify(value: str) -> str:
    slug = SLUG_RE.sub("-", value.strip().lower()).strip("-")
    return slug or "graph"


def stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha1(" ".join(parts).encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


def parse_kv(pairs: Iterable[str]) -> dict[str, Any]:
    """Parse --attr key=value pairs. JSON values are decoded when possible."""
    out: dict[str, Any] = {}
    for pair in pairs:
        if "=" not in pair:
            raise KGraphError(f"invalid attribute {pair!r}, expected key=value")
        key, raw = pair.split("=", 1)
        try:
            out[key] = json.loads(raw)
        except json.JSONDecodeError:
            out[key] = raw
    return out


def read_json_arg(value: str | None) -> Any:
    """Accept inline JSON, @file.json, or @- for stdin."""
    if value is None:
        return None
    if value == "@-":
        return json.loads(sys.stdin.read())
    if value.startswith("@"):
        path = Path(value[1:]).expanduser()
        if not path.is_file():
            raise KGraphError(f"file not found: {path}")
        return json.loads(path.read_text(encoding="utf-8"))
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise KGraphError(f"invalid JSON payload: {exc}") from exc


# --------------------------------------------------------------------------
# store
# --------------------------------------------------------------------------


class GraphStore:
    def __init__(self, path: Path):
        self.path = path
        self.log_path = path / "log.jsonl"
        self.graph_path = path / "graph.json"
        self.manifest_path = path / "manifest.json"
        self.nodes: dict[str, dict[str, Any]] = {}
        self.edges: dict[str, dict[str, Any]] = {}
        self.manifest: dict[str, Any] = {}

    # -- resolution ------------------------------------------------------

    @staticmethod
    def resolve_dir(name: str | None, path: str | None) -> Path:
        """Where the graph lives.

        --path wins. Otherwise ./<DEFAULT_ROOT>/<slug(name)>/ from cwd.
        """
        if path:
            return Path(path).expanduser().resolve()
        return (Path.cwd() / DEFAULT_ROOT / slugify(name or "graph")).resolve()

    # -- lifecycle -------------------------------------------------------

    @classmethod
    def create(
        cls,
        name: str,
        directory: Path,
        objective: str = "",
        budget: dict[str, Any] | None = None,
    ) -> "GraphStore":
        if (directory / "manifest.json").exists():
            raise KGraphError(
                f"graph already exists at {directory} — use `add` or pass a new --name"
            )
        directory.mkdir(parents=True, exist_ok=True)
        store = cls(directory)
        store.manifest = {
            "schema_version": SCHEMA_VERSION,
            "name": name,
            "slug": slugify(name),
            "objective": objective,
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "budget": budget or {},
            "counters": {"nodes": 0, "edges": 0, "events": 0},
            "node_types": list(NODE_TYPES),
            "edge_types": list(EDGE_TYPES),
        }
        store.log_path.write_text("", encoding="utf-8")
        store.save()
        return store

    @classmethod
    def load(cls, directory: Path) -> "GraphStore":
        if not (directory / "manifest.json").exists():
            raise KGraphError(
                f"no graph at {directory} — run `kgraph init --name <name>` first"
            )
        store = cls(directory)
        store.manifest = json.loads(
            store.manifest_path.read_text(encoding="utf-8")
        )
        store.replay()
        return store

    def replay(self) -> None:
        """Rebuild nodes/edges from the append-only log (source of truth)."""
        self.nodes = {}
        self.edges = {}
        if not self.log_path.exists():
            return
        for line in self.log_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            event = json.loads(line)
            self._apply(event)

    def _apply(self, event: dict[str, Any]) -> None:
        kind = event.get("event")
        if kind == "upsert_node":
            node = event["node"]
            existing = self.nodes.get(node["id"])
            if existing:
                version = existing.get("version", 1) + 1
                merged = {**existing, **node, "version": version}
                merged["aliases"] = sorted(
                    set(existing.get("aliases", [])) | set(node.get("aliases", []))
                )
                merged["source_docs"] = sorted(
                    set(existing.get("source_docs", []))
                    | set(node.get("source_docs", []))
                )
                self.nodes[node["id"]] = merged
            else:
                node.setdefault("version", 1)
                self.nodes[node["id"]] = node
        elif kind == "add_edge":
            edge = event["edge"]
            self.edges[edge["id"]] = edge
        elif kind == "retract_edge":
            self.edges.pop(event["edge_id"], None)
        elif kind == "retract_node":
            node_id = event["node_id"]
            self.nodes.pop(node_id, None)
            for edge_id in [
                eid
                for eid, e in self.edges.items()
                if e["source"] == node_id or e["target"] == node_id
            ]:
                self.edges.pop(edge_id, None)
        # unknown events are ignored on purpose: forward compatibility

    def append(self, event: dict[str, Any]) -> None:
        event.setdefault("ts", now_iso())
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        self._apply(event)
        self.manifest["counters"]["events"] = (
            self.manifest["counters"].get("events", 0) + 1
        )

    def save(self) -> None:
        self.manifest["updated_at"] = now_iso()
        self.manifest["counters"]["nodes"] = len(self.nodes)
        self.manifest["counters"]["edges"] = len(self.edges)
        self.manifest_path.write_text(
            json.dumps(self.manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        self.graph_path.write_text(
            json.dumps(
                {
                    "schema_version": SCHEMA_VERSION,
                    "name": self.manifest.get("name"),
                    "generated_at": now_iso(),
                    "nodes": list(self.nodes.values()),
                    "edges": list(self.edges.values()),
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

    # -- mutation --------------------------------------------------------

    def add_node(
        self,
        node_type: str,
        name: str,
        node_id: str | None = None,
        description: str = "",
        run_id: str = "",
        attrs: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if node_type not in NODE_TYPES:
            raise KGraphError(
                f"unknown node type {node_type!r}; allowed: {', '.join(NODE_TYPES)}"
            )
        attrs = dict(attrs or {})
        aliases = attrs.pop("aliases", []) or []
        if isinstance(aliases, str):
            aliases = [aliases]
        source_docs = attrs.pop("source_docs", []) or []
        if isinstance(source_docs, str):
            source_docs = [source_docs]
        nid = node_id or stable_id(node_type[:3].lower(), node_type, name.lower())
        node = {
            "id": nid,
            "type": node_type,
            "name": name,
            "description": description,
            "aliases": sorted(set(aliases)),
            "source_docs": sorted(set(source_docs)),
            "run_id": run_id,
            "created_at": now_iso(),
            "attrs": attrs,
        }
        self.append({"event": "upsert_node", "node": node, "run_id": run_id})
        return self.nodes[nid]

    def add_edge(
        self,
        predicate: str,
        source: str,
        target: str,
        run_id: str = "",
        source_doc: str = "",
        confidence: float | None = None,
        attrs: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if predicate not in EDGE_TYPES:
            raise KGraphError(
                f"unknown edge type {predicate!r}; allowed: {', '.join(EDGE_TYPES)}"
            )
        for endpoint in (source, target):
            if endpoint not in self.nodes:
                raise KGraphError(
                    f"edge endpoint {endpoint!r} does not resolve to a node"
                )
        eid = stable_id("e", predicate, source, target, source_doc)
        edge = {
            "id": eid,
            "predicate": predicate,
            "source": source,
            "target": target,
            "source_doc": source_doc,
            "confidence": confidence,
            "run_id": run_id,
            "created_at": now_iso(),
            "attrs": dict(attrs or {}),
        }
        self.append({"event": "add_edge", "edge": edge, "run_id": run_id})
        return self.edges[eid]

    def resolve_entities(
        self, canonical_id: str, alias_ids: list[str], run_id: str, rationale: str
    ) -> dict[str, Any]:
        """Reversible merge: aliases keep their node and gain RESOLVED_TO."""
        if canonical_id not in self.nodes:
            raise KGraphError(f"canonical node {canonical_id!r} not found")
        merged = []
        for alias_id in alias_ids:
            if alias_id == canonical_id:
                continue
            if alias_id not in self.nodes:
                raise KGraphError(f"alias node {alias_id!r} not found")
            alias_node = self.nodes[alias_id]
            self.add_edge(
                "RESOLVED_TO",
                alias_id,
                canonical_id,
                run_id=run_id,
                attrs={"rationale": rationale, "reversible": True},
            )
            canonical = self.nodes[canonical_id]
            self.append(
                {
                    "event": "upsert_node",
                    "run_id": run_id,
                    "node": {
                        "id": canonical_id,
                        "type": canonical["type"],
                        "name": canonical["name"],
                        "aliases": sorted(
                            set(canonical.get("aliases", []))
                            | {alias_node["name"]}
                            | set(alias_node.get("aliases", []))
                        ),
                        "source_docs": sorted(
                            set(canonical.get("source_docs", []))
                            | set(alias_node.get("source_docs", []))
                        ),
                    },
                }
            )
            merged.append(alias_id)
        return {"canonical": canonical_id, "merged": merged, "rationale": rationale}

    # -- retrieval -------------------------------------------------------

    def find_nodes(
        self, query: str = "", node_type: str = "", limit: int = 50
    ) -> list[dict[str, Any]]:
        needle = query.lower().strip()
        hits = []
        for node in self.nodes.values():
            if node_type and node["type"] != node_type:
                continue
            if needle:
                haystack = " ".join(
                    [
                        node.get("name", ""),
                        node.get("description", ""),
                        " ".join(node.get("aliases", [])),
                    ]
                ).lower()
                if needle not in haystack:
                    continue
            hits.append(node)
        hits.sort(key=lambda n: (n["type"], n["name"]))
        return hits[:limit]

    def neighborhood(
        self,
        seeds: list[str],
        hops: int = 2,
        edge_types: list[str] | None = None,
        max_nodes: int = 60,
    ) -> dict[str, Any]:
        """Bounded traversal — never dump the whole graph into a model."""
        allowed = set(edge_types or EDGE_TYPES)
        adjacency: dict[str, list[dict[str, Any]]] = {}
        for edge in self.edges.values():
            if edge["predicate"] not in allowed:
                continue
            adjacency.setdefault(edge["source"], []).append(edge)
            adjacency.setdefault(edge["target"], []).append(edge)

        seen = {s for s in seeds if s in self.nodes}
        frontier = deque((s, 0) for s in seen)
        picked_edges: dict[str, dict[str, Any]] = {}
        truncated = False

        while frontier:
            node_id, depth = frontier.popleft()
            if depth >= hops:
                continue
            for edge in adjacency.get(node_id, []):
                other = edge["target"] if edge["source"] == node_id else edge["source"]
                picked_edges[edge["id"]] = edge
                if other not in seen:
                    if len(seen) >= max_nodes:
                        truncated = True
                        continue
                    seen.add(other)
                    frontier.append((other, depth + 1))

        return {
            "nodes": [self.nodes[n] for n in seen if n in self.nodes],
            "edges": list(picked_edges.values()),
            "truncated": truncated,
            "hops": hops,
        }

    def find_path(
        self, source: str, target: str, max_depth: int = 6
    ) -> list[dict[str, Any]]:
        """Shortest provenance path, returned as an ordered edge list."""
        if source not in self.nodes or target not in self.nodes:
            raise KGraphError("path endpoints must both exist in the graph")
        adjacency: dict[str, list[dict[str, Any]]] = {}
        for edge in self.edges.values():
            adjacency.setdefault(edge["source"], []).append(edge)
            adjacency.setdefault(edge["target"], []).append(edge)

        queue: deque[tuple[str, list[dict[str, Any]]]] = deque([(source, [])])
        visited = {source}
        while queue:
            node_id, trail = queue.popleft()
            if node_id == target:
                return trail
            if len(trail) >= max_depth:
                continue
            for edge in adjacency.get(node_id, []):
                other = edge["target"] if edge["source"] == node_id else edge["source"]
                if other in visited:
                    continue
                visited.add(other)
                queue.append((other, trail + [edge]))
        return []

    # -- quality ---------------------------------------------------------

    def validate(self) -> dict[str, Any]:
        """Check the four write invariants plus structural health."""
        violations: list[dict[str, str]] = []

        out_edges: dict[str, list[dict[str, Any]]] = {}
        in_edges: dict[str, list[dict[str, Any]]] = {}
        for edge in self.edges.values():
            out_edges.setdefault(edge["source"], []).append(edge)
            in_edges.setdefault(edge["target"], []).append(edge)

        for node in self.nodes.values():
            nid, ntype = node["id"], node["type"]

            if ntype == "Claim":
                inference = bool(node.get("attrs", {}).get("inference"))
                sourced = any(
                    e["predicate"] in ("SUPPORTS", "DERIVED_FROM")
                    and self.nodes.get(e["source"], {}).get("type") == "Source"
                    for e in in_edges.get(nid, [])
                ) or any(
                    e["predicate"] in ("SUPPORTS", "DERIVED_FROM")
                    and self.nodes.get(e["target"], {}).get("type") == "Source"
                    for e in out_edges.get(nid, [])
                )
                if not (inference or sourced):
                    violations.append(
                        {
                            "invariant": "I1",
                            "node": nid,
                            "detail": f"Claim {node['name']!r} has no Source edge "
                            "and is not marked inference=true",
                        }
                    )

            if ntype == "Artifact":
                authored = any(
                    e["predicate"] == "PRODUCED"
                    and self.nodes.get(e["source"], {}).get("type") == "AgentRun"
                    for e in in_edges.get(nid, [])
                )
                if not authored:
                    violations.append(
                        {
                            "invariant": "I2",
                            "node": nid,
                            "detail": f"Artifact {node['name']!r} has no "
                            "AgentRun -PRODUCED-> edge",
                        }
                    )
                if not node.get("attrs", {}).get("version") and not node.get("version"):
                    violations.append(
                        {
                            "invariant": "I2",
                            "node": nid,
                            "detail": f"Artifact {node['name']!r} has no version",
                        }
                    )

            if ntype == "Evaluation" and not node.get("attrs", {}).get("rubric"):
                violations.append(
                    {
                        "invariant": "I3",
                        "node": nid,
                        "detail": f"Evaluation {node['name']!r} has no rubric attribute",
                    }
                )

        for edge in self.edges.values():
            if edge["predicate"] == "SUPERSEDES" and edge["target"] not in self.nodes:
                violations.append(
                    {
                        "invariant": "I4",
                        "node": edge["target"],
                        "detail": "superseded object is no longer addressable",
                    }
                )

        isolated = [
            n["id"]
            for n in self.nodes.values()
            if not out_edges.get(n["id"]) and not in_edges.get(n["id"])
        ]

        return {
            "ok": not violations,
            "violations": violations,
            "invariants": list(INVARIANTS),
            "stats": self.stats(isolated=isolated),
        }

    def stats(self, isolated: list[str] | None = None) -> dict[str, Any]:
        by_node_type: dict[str, int] = {}
        for node in self.nodes.values():
            by_node_type[node["type"]] = by_node_type.get(node["type"], 0) + 1
        by_edge_type: dict[str, int] = {}
        for edge in self.edges.values():
            by_edge_type[edge["predicate"]] = by_edge_type.get(edge["predicate"], 0) + 1

        node_count = len(self.nodes)
        edge_count = len(self.edges)
        density = round(edge_count / node_count, 3) if node_count else 0.0

        if isolated is None:
            touched = {e["source"] for e in self.edges.values()} | {
                e["target"] for e in self.edges.values()
            }
            isolated = [n for n in self.nodes if n not in touched]

        return {
            "nodes": node_count,
            "edges": edge_count,
            "density": density,
            "components": self.component_count(),
            "isolated_nodes": len(isolated),
            "by_node_type": by_node_type,
            "by_edge_type": by_edge_type,
        }

    def component_count(self) -> int:
        adjacency: dict[str, set[str]] = {n: set() for n in self.nodes}
        for edge in self.edges.values():
            if edge["source"] in adjacency and edge["target"] in adjacency:
                adjacency[edge["source"]].add(edge["target"])
                adjacency[edge["target"]].add(edge["source"])
        seen: set[str] = set()
        count = 0
        for node_id in adjacency:
            if node_id in seen:
                continue
            count += 1
            stack = [node_id]
            while stack:
                current = stack.pop()
                if current in seen:
                    continue
                seen.add(current)
                stack.extend(adjacency[current] - seen)
        return count


# --------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------

NODE_COLORS = {
    "Entity": "#4f9df7",
    "Claim": "#f7b955",
    "Source": "#7ed491",
    "Artifact": "#c792ea",
    "AgentRun": "#ff6b6b",
    "Evaluation": "#4ecdc4",
    "Task": "#ffd166",
    "Commit": "#a0a8b3",
    "Metric": "#ef6ea8",
}


def render_mermaid(store: GraphStore, max_nodes: int = 120) -> str:
    lines = ["graph LR"]
    nodes = list(store.nodes.values())[:max_nodes]
    keep = {n["id"] for n in nodes}
    for node in nodes:
        label = node["name"].replace('"', "'")[:40]
        lines.append(f'  {node["id"]}["{node["type"]}: {label}"]')
    for edge in store.edges.values():
        if edge["source"] in keep and edge["target"] in keep:
            lines.append(
                f'  {edge["source"]} -->|{edge["predicate"]}| {edge["target"]}'
            )
    if len(store.nodes) > max_nodes:
        lines.append(f'  %% truncated: showing {max_nodes}/{len(store.nodes)} nodes')
    return "\n".join(lines) + "\n"


def render_report(store: GraphStore, validation: dict[str, Any]) -> str:
    stats = validation["stats"]
    name = store.manifest.get("name", "graph")
    lines = [
        f"# Knowledge Graph — {name}",
        "",
        f"- **Objective:** {store.manifest.get('objective') or '_not set_'}",
        f"- **Updated:** {now_iso()}",
        f"- **Schema:** {SCHEMA_VERSION}",
        "",
        "## Health",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| Nodes | {stats['nodes']} |",
        f"| Edges | {stats['edges']} |",
        f"| Density (edges/node) | {stats['density']} |",
        f"| Connected components | {stats['components']} |",
        f"| Isolated nodes | {stats['isolated_nodes']} |",
        f"| Invariant violations | {len(validation['violations'])} |",
        "",
        "## Composition",
        "",
        "| Node type | Count |",
        "|---|---|",
    ]
    for key in NODE_TYPES:
        if stats["by_node_type"].get(key):
            lines.append(f"| {key} | {stats['by_node_type'][key]} |")
    lines += ["", "| Edge type | Count |", "|---|---|"]
    for key in EDGE_TYPES:
        if stats["by_edge_type"].get(key):
            lines.append(f"| {key} | {stats['by_edge_type'][key]} |")

    lines += ["", "## Invariants", ""]
    for text in INVARIANTS:
        lines.append(f"- {text}")

    lines += ["", "## Violations", ""]
    if validation["violations"]:
        lines += ["| Invariant | Node | Detail |", "|---|---|---|"]
        for violation in validation["violations"]:
            lines.append(
                f"| {violation['invariant']} | `{violation['node']}` | "
                f"{violation['detail']} |"
            )
    else:
        lines.append("None. Every write satisfies I1–I4.")

    lines += [
        "",
        "## Visual",
        "",
        "- `graph.html` — interactive explorer (open in a browser)",
        "- `graph.mmd` — Mermaid source",
        "- `graph.json` — machine-readable graph",
        "- `log.jsonl` — append-only event log (reversible history)",
        "",
    ]
    return "\n".join(lines)


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Karpathy Graph — __NAME__</title>
<style>
  :root { color-scheme: dark; }
  * { box-sizing: border-box; }
  body { margin:0; background:#0d1117; color:#e6edf3;
         font:14px/1.5 ui-sans-serif,-apple-system,"Segoe UI",Roboto,sans-serif; }
  header { padding:14px 18px; border-bottom:1px solid #21262d;
           display:flex; gap:16px; align-items:center; flex-wrap:wrap; }
  h1 { font-size:16px; margin:0; font-weight:600; }
  .pill { background:#161b22; border:1px solid #30363d; border-radius:999px;
          padding:3px 10px; font-size:12px; color:#8b949e; }
  .bad { border-color:#f85149; color:#f85149; }
  .good { border-color:#3fb950; color:#3fb950; }
  main { display:grid; grid-template-columns: 1fr 340px; height:calc(100vh - 57px); }
  #canvas { position:relative; overflow:hidden; background:
            radial-gradient(circle at 50% 40%, #12181f 0%, #0d1117 70%); }
  aside { border-left:1px solid #21262d; overflow-y:auto; padding:14px; }
  aside h2 { font-size:12px; text-transform:uppercase; letter-spacing:.08em;
             color:#8b949e; margin:18px 0 8px; }
  aside h2:first-child { margin-top:0; }
  input, select { width:100%; background:#0d1117; border:1px solid #30363d;
                  color:#e6edf3; border-radius:6px; padding:7px 9px; font-size:13px; }
  .legend { display:flex; flex-wrap:wrap; gap:6px; }
  .legend span { font-size:11px; padding:3px 8px; border-radius:999px;
                 background:#161b22; border:1px solid #30363d; cursor:pointer; }
  .legend span.off { opacity:.32; }
  .dot { display:inline-block; width:8px; height:8px; border-radius:50%;
         margin-right:5px; vertical-align:middle; }
  #detail { font-size:13px; }
  #detail dt { color:#8b949e; font-size:11px; text-transform:uppercase;
               letter-spacing:.05em; margin-top:10px; }
  #detail dd { margin:2px 0 0; word-break:break-word; }
  code { background:#161b22; padding:1px 5px; border-radius:4px; font-size:12px; }
  .hint { color:#8b949e; font-size:12px; }
  svg { width:100%; height:100%; display:block; cursor:grab; }
  svg:active { cursor:grabbing; }
  .node circle { stroke:#0d1117; stroke-width:1.5; cursor:pointer; }
  .node.sel circle { stroke:#e6edf3; stroke-width:2.5; }
  .node.dim { opacity:.12; }
  .node text { font-size:10px; fill:#c9d1d9; pointer-events:none; }
  .link { stroke:#30363d; stroke-width:1.2; }
  .link.dim { opacity:.06; }
  .link.hot { stroke:#58a6ff; stroke-width:2; }
  footer { position:absolute; bottom:8px; left:12px; color:#484f58; font-size:11px; }
</style>
</head>
<body>
<header>
  <h1>__NAME__</h1>
  <span class="pill">__NODE_COUNT__ nodes</span>
  <span class="pill">__EDGE_COUNT__ edges</span>
  <span class="pill">__COMPONENTS__ components</span>
  <span class="pill __VCLASS__">__VIOLATIONS__ invariant violations</span>
</header>
<main>
  <div id="canvas"><svg id="svg"></svg><footer>drag to pan · scroll to zoom · click a node</footer></div>
  <aside>
    <h2>Search</h2>
    <input id="search" placeholder="filter by name or type…" />
    <h2>Node types</h2>
    <div class="legend" id="legend"></div>
    <h2>Selection</h2>
    <dl id="detail"><dd class="hint">Click any node to inspect it and highlight its edges.</dd></dl>
  </aside>
</main>
<script id="graph-data" type="application/json">__DATA__</script>
<script>
(function () {
  const DATA = JSON.parse(document.getElementById('graph-data').textContent);
  const COLORS = __COLORS__;
  const svg = document.getElementById('svg');
  const NS = 'http://www.w3.org/2000/svg';
  const W = svg.clientWidth || 900, H = svg.clientHeight || 600;

  const N = DATA.nodes.length;
  // deterministic pseudo-random start: a golden-angle spiral avoids the
  // symmetric-ring degeneracy that leaves every node at the same radius
  const GOLDEN = Math.PI * (3 - Math.sqrt(5));
  const SPREAD = Math.min(W, H) * 0.42;
  const nodes = DATA.nodes.map((n, i) => {
    const a = i * GOLDEN;
    const r = SPREAD * Math.sqrt((i + 0.5) / Math.max(N, 1));
    return Object.assign({}, n, {
      x: W / 2 + r * Math.cos(a), y: H / 2 + r * Math.sin(a), vx: 0, vy: 0
    });
  });
  const index = new Map(nodes.map(n => [n.id, n]));
  const links = DATA.edges
    .filter(e => index.has(e.source) && index.has(e.target))
    .map(e => Object.assign({}, e, { s: index.get(e.source), t: index.get(e.target) }));

  // Fruchterman-Reingold layout: repulsion k²/d, attraction d²/k, linear cooling.
  // Displacement is capped by the current temperature, not by an arbitrary
  // constant, so the graph actually expands to fill the canvas before it settles.
  const AREA = W * H;
  const k = Math.sqrt(AREA / Math.max(N, 1)) * 0.62;
  const ITER = 420;
  let temp = Math.min(W, H) * 0.12;
  for (let step = 0; step < ITER; step++) {
    for (const n of nodes) { n.vx = 0; n.vy = 0; }
    for (let i = 0; i < N; i++) {
      for (let j = i + 1; j < N; j++) {
        const a = nodes[i], b = nodes[j];
        let dx = a.x - b.x, dy = a.y - b.y;
        let d = Math.sqrt(dx * dx + dy * dy);
        if (d < 0.01) { dx = (i % 7) - 3 + 0.5; dy = (j % 5) - 2 + 0.5; d = Math.sqrt(dx * dx + dy * dy); }
        const rep = (k * k) / d;
        const ux = dx / d, uy = dy / d;
        a.vx += ux * rep; a.vy += uy * rep;
        b.vx -= ux * rep; b.vy -= uy * rep;
      }
    }
    for (const l of links) {
      let dx = l.t.x - l.s.x, dy = l.t.y - l.s.y;
      const d = Math.sqrt(dx * dx + dy * dy) || 0.01;
      const att = (d * d) / k;
      const ux = dx / d, uy = dy / d;
      l.s.vx += ux * att; l.s.vy += uy * att;
      l.t.vx -= ux * att; l.t.vy -= uy * att;
    }
    for (const n of nodes) {
      const disp = Math.sqrt(n.vx * n.vx + n.vy * n.vy) || 0.01;
      const limit = Math.min(disp, temp);
      n.x += (n.vx / disp) * limit;
      n.y += (n.vy / disp) * limit;
      // weak centering keeps disconnected components on screen
      n.x += (W / 2 - n.x) * 0.004;
      n.y += (H / 2 - n.y) * 0.004;
    }
    temp *= 0.985;
  }

  // Disconnected components drift far apart, so a single bounding box would be
  // mostly empty space. Pack each component tightly, lay them out left to right
  // by size, then fit the packed result to the viewport.
  (function packComponents() {
    const adj = new Map(nodes.map(n => [n.id, []]));
    for (const l of links) { adj.get(l.source).push(l.target); adj.get(l.target).push(l.source); }
    const seen = new Set(), comps = [];
    for (const n of nodes) {
      if (seen.has(n.id)) continue;
      const group = [], stack = [n.id];
      while (stack.length) {
        const id = stack.pop();
        if (seen.has(id)) continue;
        seen.add(id); group.push(index.get(id));
        for (const nb of adj.get(id)) if (!seen.has(nb)) stack.push(nb);
      }
      comps.push(group);
    }
    comps.sort((a, b) => b.length - a.length);

    const boxes = comps.map(group => {
      let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
      for (const n of group) {
        if (n.x < minX) minX = n.x; if (n.x > maxX) maxX = n.x;
        if (n.y < minY) minY = n.y; if (n.y > maxY) maxY = n.y;
      }
      return { group, w: Math.max(maxX - minX, 1), h: Math.max(maxY - minY, 1), minX, minY };
    });

    const GAP = 46;
    let cursorX = 0, rowY = 0, rowH = 0;
    const maxRowW = Math.max(...boxes.map(b => b.w), 1) * 1.9;
    for (const b of boxes) {
      if (cursorX > 0 && cursorX + b.w > maxRowW) { cursorX = 0; rowY += rowH + GAP; rowH = 0; }
      for (const n of b.group) { n.x += cursorX - b.minX; n.y += rowY - b.minY; }
      cursorX += b.w + GAP;
      rowH = Math.max(rowH, b.h);
    }

    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    for (const n of nodes) {
      if (n.x < minX) minX = n.x; if (n.x > maxX) maxX = n.x;
      if (n.y < minY) minY = n.y; if (n.y > maxY) maxY = n.y;
    }
    const spanX = Math.max(maxX - minX, 1), spanY = Math.max(maxY - minY, 1);
    const M = 80;
    const s = Math.min((W - 2 * M) / spanX, (H - 2 * M) / spanY, 2.2);
    for (const n of nodes) {
      n.x = (n.x - (minX + maxX) / 2) * s + W / 2;
      n.y = (n.y - (minY + maxY) / 2) * s + H / 2;
    }
  })();

  const defs = document.createElementNS(NS, 'defs');
  defs.innerHTML =
    '<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" ' +
    'markerHeight="6" orient="auto-start-reverse">' +
    '<path d="M0,0 L10,5 L0,10 z" fill="#484f58"/></marker>' +
    '<marker id="arrowhot" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" ' +
    'markerHeight="6" orient="auto-start-reverse">' +
    '<path d="M0,0 L10,5 L0,10 z" fill="#58a6ff"/></marker>';
  svg.appendChild(defs);
  const root = document.createElementNS(NS, 'g');
  svg.appendChild(root);
  const linkLayer = document.createElementNS(NS, 'g');
  const nodeLayer = document.createElementNS(NS, 'g');
  root.appendChild(linkLayer); root.appendChild(nodeLayer);

  const degree = new Map();
  for (const l of links) {
    degree.set(l.source, (degree.get(l.source) || 0) + 1);
    degree.set(l.target, (degree.get(l.target) || 0) + 1);
  }
  const radiusOf = id => 5 + Math.min(9, (degree.get(id) || 0) * 1.4);

  const linkEls = links.map(l => {
    const line = document.createElementNS(NS, 'line');
    line.setAttribute('class', 'link');
    line.setAttribute('marker-end', 'url(#arrow)');
    // stop the segment at the node border so the arrowhead stays visible
    const dx = l.t.x - l.s.x, dy = l.t.y - l.s.y;
    const d = Math.sqrt(dx * dx + dy * dy) || 1;
    const ux = dx / d, uy = dy / d;
    const r1 = radiusOf(l.source) + 1, r2 = radiusOf(l.target) + 5;
    line.setAttribute('x1', l.s.x + ux * r1); line.setAttribute('y1', l.s.y + uy * r1);
    line.setAttribute('x2', l.t.x - ux * r2); line.setAttribute('y2', l.t.y - uy * r2);
    const title = document.createElementNS(NS, 'title');
    title.textContent = l.s.name + ' —' + l.predicate + '→ ' + l.t.name;
    line.appendChild(title);
    linkLayer.appendChild(line);
    return { el: line, data: l };
  });

  // Label only the nodes that carry the most structure. Labelling all of them
  // turns a mid-size graph into unreadable overlapping text.
  const LABEL_BUDGET = nodes.length <= 24 ? nodes.length
    : Math.max(18, Math.round(nodes.length * 0.45));
  const labelled = new Set(
    nodes.slice().sort((a, b) => (degree.get(b.id) || 0) - (degree.get(a.id) || 0))
      .slice(0, LABEL_BUDGET).map(n => n.id)
  );

  const nodeEls = nodes.map(n => {
    const g = document.createElementNS(NS, 'g');
    g.setAttribute('class', 'node');
    g.setAttribute('transform', 'translate(' + n.x + ',' + n.y + ')');
    const c = document.createElementNS(NS, 'circle');
    const r = 5 + Math.min(9, (degree.get(n.id) || 0) * 1.4);
    c.setAttribute('r', r);
    c.setAttribute('fill', COLORS[n.type] || '#8b949e');
    const title = document.createElementNS(NS, 'title');
    title.textContent = n.type + ': ' + n.name;
    c.appendChild(title);
    g.appendChild(c);
    if (labelled.has(n.id)) {
      const label = document.createElementNS(NS, 'text');
      label.setAttribute('x', r + 4); label.setAttribute('y', 3);
      label.textContent = n.name.length > 24 ? n.name.slice(0, 23) + '…' : n.name;
      g.appendChild(label);
    }
    nodeLayer.appendChild(g);
    g.addEventListener('click', ev => { ev.stopPropagation(); select(n.id); });
    return { el: g, data: n };
  });

  const detail = document.getElementById('detail');
  const escapeHtml = value => String(value).replace(/[&<>"']/g, char => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[char]));
  function select(id) {
    const node = index.get(id);
    const incident = links.filter(l => l.source === id || l.target === id);
    const hot = new Set([id]);
    incident.forEach(l => { hot.add(l.source); hot.add(l.target); });
    nodeEls.forEach(n => {
      n.el.classList.toggle('dim', !hot.has(n.data.id));
      n.el.classList.toggle('sel', n.data.id === id);
    });
    linkEls.forEach(l => {
      const on = l.data.source === id || l.data.target === id;
      l.el.classList.toggle('hot', on);
      l.el.classList.toggle('dim', !on);
      l.el.setAttribute('marker-end', on ? 'url(#arrowhot)' : 'url(#arrow)');
    });
    const rows = [
      ['Type', escapeHtml(node.type)],
      ['ID', '<code>' + escapeHtml(node.id) + '</code>'],
      ['Description', escapeHtml(node.description || '—')],
      ['Aliases', escapeHtml((node.aliases || []).join(', ') || '—')],
      ['Sources', escapeHtml((node.source_docs || []).join(', ') || '—')],
      ['Run', escapeHtml(node.run_id || '—')],
      ['Degree', String(incident.length)]
    ];
    const edgeList = incident.slice(0, 40).map(l => {
      const dir = l.source === id
        ? '→ ' + escapeHtml(index.get(l.target).name)
        : '← ' + escapeHtml(index.get(l.source).name);
      return '<div><code>' + escapeHtml(l.predicate) + '</code> ' + dir + '</div>';
    }).join('');
    detail.innerHTML = '<dt>Name</dt><dd>' + escapeHtml(node.name) + '</dd>' +
      rows.map(r => '<dt>' + r[0] + '</dt><dd>' + r[1] + '</dd>').join('') +
      '<dt>Edges</dt><dd>' + (edgeList || '—') + '</dd>';
  }
  svg.addEventListener('click', () => {
    nodeEls.forEach(n => { n.el.classList.remove('dim', 'sel'); });
    linkEls.forEach(l => {
      l.el.classList.remove('dim', 'hot');
      l.el.setAttribute('marker-end', 'url(#arrow)');
    });
    detail.innerHTML = '<dd class="hint">Click any node to inspect it and highlight its edges.</dd>';
  });

  const hidden = new Set();
  const legend = document.getElementById('legend');
  Object.keys(COLORS).forEach(type => {
    if (!nodes.some(n => n.type === type)) return;
    const span = document.createElement('span');
    span.innerHTML = '<i class="dot" style="background:' + COLORS[type] + '"></i>' + type;
    span.addEventListener('click', () => {
      hidden.has(type) ? hidden.delete(type) : hidden.add(type);
      span.classList.toggle('off', hidden.has(type));
      applyFilter();
    });
    legend.appendChild(span);
  });

  const search = document.getElementById('search');
  search.addEventListener('input', applyFilter);
  function applyFilter() {
    const q = search.value.trim().toLowerCase();
    const visible = new Set();
    nodeEls.forEach(n => {
      const d = n.data;
      const match = (!q || (d.name + ' ' + d.type + ' ' + (d.description || '')).toLowerCase().includes(q))
        && !hidden.has(d.type);
      n.el.style.display = match ? '' : 'none';
      if (match) visible.add(d.id);
    });
    linkEls.forEach(l => {
      l.el.style.display = visible.has(l.data.source) && visible.has(l.data.target) ? '' : 'none';
    });
  }

  let scale = 1, tx = 0, ty = 0, dragging = false, lastX = 0, lastY = 0;
  function apply() { root.setAttribute('transform', 'translate(' + tx + ',' + ty + ') scale(' + scale + ')'); }
  svg.addEventListener('wheel', e => {
    e.preventDefault();
    const factor = e.deltaY < 0 ? 1.1 : 0.9;
    scale = Math.max(0.15, Math.min(6, scale * factor));
    apply();
  }, { passive: false });
  svg.addEventListener('mousedown', e => { dragging = true; lastX = e.clientX; lastY = e.clientY; });
  window.addEventListener('mouseup', () => { dragging = false; });
  window.addEventListener('mousemove', e => {
    if (!dragging) return;
    tx += e.clientX - lastX; ty += e.clientY - lastY;
    lastX = e.clientX; lastY = e.clientY;
    apply();
  });
})();
</script>
</body>
</html>
"""


def render_html(store: GraphStore, validation: dict[str, Any]) -> str:
    stats = validation["stats"]
    payload = {
        "nodes": [
            {
                "id": n["id"],
                "type": n["type"],
                "name": n["name"],
                "description": n.get("description", ""),
                "aliases": n.get("aliases", []),
                "source_docs": n.get("source_docs", []),
                "run_id": n.get("run_id", ""),
            }
            for n in store.nodes.values()
        ],
        "edges": [
            {
                "id": e["id"],
                "predicate": e["predicate"],
                "source": e["source"],
                "target": e["target"],
            }
            for e in store.edges.values()
        ],
    }
    violations = len(validation["violations"])
    html = HTML_TEMPLATE
    html = html.replace(
        "__NAME__", html_escape(str(store.manifest.get("name", "graph")), quote=True)
    )
    html = html.replace("__NODE_COUNT__", str(stats["nodes"]))
    html = html.replace("__EDGE_COUNT__", str(stats["edges"]))
    html = html.replace("__COMPONENTS__", str(stats["components"]))
    html = html.replace("__VIOLATIONS__", str(violations))
    html = html.replace("__VCLASS__", "bad" if violations else "good")
    html = html.replace("__COLORS__", json.dumps(NODE_COLORS))
    # Keep the payload inert inside the <script type=application/json> block.
    # Escaping angle brackets also prevents a graph value from closing the
    # script element before the browser parses the JSON.
    safe_payload = (
        json.dumps(payload, ensure_ascii=False)
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )
    html = html.replace(
        "__DATA__",
        safe_payload,
    )
    return html


def render_all(store: GraphStore) -> dict[str, Any]:
    validation = store.validate()
    (store.path / "graph.mmd").write_text(render_mermaid(store), encoding="utf-8")
    (store.path / "REPORT.md").write_text(
        render_report(store, validation), encoding="utf-8"
    )
    (store.path / "graph.html").write_text(
        render_html(store, validation), encoding="utf-8"
    )
    store.save()
    return {
        "files": {
            "graph": str(store.graph_path),
            "html": str(store.path / "graph.html"),
            "mermaid": str(store.path / "graph.mmd"),
            "report": str(store.path / "REPORT.md"),
            "log": str(store.log_path),
        },
        "stats": validation["stats"],
        "violations": len(validation["violations"]),
    }


# --------------------------------------------------------------------------
# ingest
# --------------------------------------------------------------------------


def ingest_payload(
    store: GraphStore, payload: dict[str, Any], run_id: str
) -> dict[str, Any]:
    """Apply an ExtractedGraph-shaped payload: {nodes:[...], edges:[...]}.

    Edges may reference nodes by id or by name; names are resolved against the
    nodes created in this same payload first, then against the whole graph.
    """
    if not isinstance(payload, dict):
        raise KGraphError("payload must be a JSON object with nodes/edges")

    name_to_id: dict[str, str] = {}
    created_nodes = []
    for raw in payload.get("nodes", []):
        node = store.add_node(
            node_type=raw.get("type", "Entity"),
            name=raw["name"],
            node_id=raw.get("id"),
            description=raw.get("description", ""),
            run_id=raw.get("run_id", run_id),
            attrs={
                k: v
                for k, v in raw.items()
                if k not in ("type", "name", "id", "description", "run_id")
            },
        )
        name_to_id[raw["name"].lower()] = node["id"]
        for alias in node.get("aliases", []):
            name_to_id.setdefault(alias.lower(), node["id"])
        created_nodes.append(node["id"])

    for node in store.nodes.values():
        name_to_id.setdefault(node["name"].lower(), node["id"])

    def resolve(ref: str) -> str:
        if ref in store.nodes:
            return ref
        found = name_to_id.get(str(ref).lower())
        if not found:
            raise KGraphError(
                f"edge endpoint {ref!r} does not match any node id or name"
            )
        return found

    created_edges = []
    for raw in payload.get("edges", []):
        edge = store.add_edge(
            predicate=raw.get("predicate", raw.get("type", "MENTIONS")),
            source=resolve(raw.get("source", raw.get("from"))),
            target=resolve(raw.get("target", raw.get("to"))),
            run_id=raw.get("run_id", run_id),
            source_doc=raw.get("source_doc", ""),
            confidence=raw.get("confidence"),
            attrs={
                k: v
                for k, v in raw.items()
                if k
                not in (
                    "predicate",
                    "type",
                    "source",
                    "target",
                    "from",
                    "to",
                    "run_id",
                    "source_doc",
                    "confidence",
                )
            },
        )
        created_edges.append(edge["id"])

    return {"nodes_added": created_nodes, "edges_added": created_edges}


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def emit(payload: dict[str, Any], ok: bool = True) -> None:
    out = {"ok": ok, **payload}
    print(json.dumps(out, indent=2, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kgraph",
        description="Karpathy graph engineering store (typed nodes, provenance, "
        "bounded retrieval, human-visual rendering).",
    )
    parser.add_argument("--name", help="graph name (slugified into the default path)")
    parser.add_argument(
        "--path", help="explicit graph directory; overrides ./.karpathy-graphs/<name>"
    )
    parser.add_argument("--run-id", default="", help="AgentRun id for provenance")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="create a new graph")
    p_init.add_argument("--objective", default="")
    p_init.add_argument("--budget", help="JSON budget object, @file.json or @-")

    p_node = sub.add_parser("add-node", help="add or update one typed node")
    p_node.add_argument("--type", required=True, choices=NODE_TYPES)
    p_node.add_argument("--name", dest="node_name", required=True)
    p_node.add_argument("--id")
    p_node.add_argument("--description", default="")
    p_node.add_argument("--attr", action="append", default=[], metavar="KEY=VALUE")

    p_edge = sub.add_parser("add-edge", help="add one typed edge with provenance")
    p_edge.add_argument("--predicate", required=True, choices=EDGE_TYPES)
    p_edge.add_argument("--source", required=True)
    p_edge.add_argument("--target", required=True)
    p_edge.add_argument("--source-doc", default="")
    p_edge.add_argument("--confidence", type=float)
    p_edge.add_argument("--attr", action="append", default=[], metavar="KEY=VALUE")

    p_ingest = sub.add_parser(
        "ingest", help="apply an ExtractedGraph payload (nodes + edges) in one write"
    )
    p_ingest.add_argument("payload", help="inline JSON, @file.json or @- for stdin")

    p_resolve = sub.add_parser(
        "resolve", help="reversibly merge alias nodes into a canonical entity"
    )
    p_resolve.add_argument("--canonical", required=True)
    p_resolve.add_argument("--alias", action="append", default=[], required=True)
    p_resolve.add_argument("--rationale", default="")

    p_query = sub.add_parser(
        "query", help="retrieve a bounded subgraph instead of the whole graph"
    )
    p_query.add_argument("text", nargs="?", default="")
    p_query.add_argument("--type", default="", choices=("",) + NODE_TYPES)
    p_query.add_argument("--hops", type=int, default=2)
    p_query.add_argument("--max-nodes", type=int, default=60)
    p_query.add_argument("--edge-type", action="append", default=[])
    p_query.add_argument(
        "--format", default="json", choices=("json", "triples", "context")
    )

    p_path = sub.add_parser("path", help="shortest provenance path between two nodes")
    p_path.add_argument("source")
    p_path.add_argument("target")
    p_path.add_argument("--max-depth", type=int, default=6)

    sub.add_parser("validate", help="check the four write invariants")
    sub.add_parser("stats", help="graph health metrics")
    sub.add_parser("render", help="write REPORT.md, graph.html and graph.mmd")
    sub.add_parser("list", help="list every graph under ./.karpathy-graphs")

    p_retract = sub.add_parser("retract", help="reverse a node or edge (append-only)")
    p_retract.add_argument("--node")
    p_retract.add_argument("--edge")

    sub.add_parser("selftest", help="run an end-to-end self test in a temp dir")

    return parser


def cmd_list() -> dict[str, Any]:
    root = Path.cwd() / DEFAULT_ROOT
    graphs = []
    if root.is_dir():
        for child in sorted(root.iterdir()):
            manifest = child / "manifest.json"
            if manifest.is_file():
                data = json.loads(manifest.read_text(encoding="utf-8"))
                graphs.append(
                    {
                        "name": data.get("name"),
                        "path": str(child),
                        "nodes": data.get("counters", {}).get("nodes", 0),
                        "edges": data.get("counters", {}).get("edges", 0),
                        "updated_at": data.get("updated_at"),
                    }
                )
    return {"root": str(root), "graphs": graphs}


def serialize_triples(sub: dict[str, Any], store: GraphStore) -> str:
    lookup = {n["id"]: n for n in sub["nodes"]}
    lines = []
    for edge in sub["edges"]:
        s = lookup.get(edge["source"], store.nodes.get(edge["source"], {}))
        t = lookup.get(edge["target"], store.nodes.get(edge["target"], {}))
        cite = f"  [edge:{edge['id']}]"
        doc = f" (src: {edge['source_doc']})" if edge.get("source_doc") else ""
        lines.append(
            f"({s.get('name', edge['source'])}) -{edge['predicate']}-> "
            f"({t.get('name', edge['target'])}){doc}{cite}"
        )
    return "\n".join(lines)


def serialize_context(sub: dict[str, Any], store: GraphStore) -> str:
    lines = ["## Entities", ""]
    for node in sorted(sub["nodes"], key=lambda n: (n["type"], n["name"])):
        alias = (
            f" (aliases: {', '.join(node['aliases'])})" if node.get("aliases") else ""
        )
        desc = f" — {node['description']}" if node.get("description") else ""
        lines.append(f"- [{node['type']}] {node['name']}{alias}{desc} `{node['id']}`")
    lines += ["", "## Relations", "", serialize_triples(sub, store)]
    if sub.get("truncated"):
        lines += ["", "> Subgraph truncated by max_nodes — widen the budget to see more."]
    return "\n".join(lines)


def selftest() -> dict[str, Any]:
    """End-to-end check: build, validate, render, query, retract."""
    import shutil
    import tempfile

    tmp = Path(tempfile.mkdtemp(prefix="kgraph-selftest-"))
    checks: list[dict[str, Any]] = []

    def check(label: str, condition: bool, detail: str = "") -> None:
        checks.append({"check": label, "pass": bool(condition), "detail": detail})

    try:
        store = GraphStore.create("Self Test", tmp / "g", objective="verify engine")
        run = store.add_node("AgentRun", "run-1", run_id="run-1")
        src = store.add_node("Source", "readme.md", attrs={"uri": "./readme.md"})
        ent = store.add_node("Entity", "Autoresearch")
        claim = store.add_node("Claim", "Autoresearch keeps only improvements")
        art = store.add_node("Artifact", "report.md", attrs={"version": 1})
        ev = store.add_node("Evaluation", "eval-1", attrs={"rubric": "graph-quality"})

        store.add_edge("SUPPORTS", src["id"], claim["id"], source_doc="readme.md")
        store.add_edge("MENTIONS", claim["id"], ent["id"])
        store.add_edge("PRODUCED", run["id"], art["id"])
        store.add_edge("EVALUATES", ev["id"], art["id"])
        store.save()

        v = store.validate()
        check("invariants clean on a well-formed graph", v["ok"], json.dumps(v["violations"]))

        bad = store.add_node("Claim", "unsourced claim")
        v2 = store.validate()
        check(
            "I1 catches an unsourced claim",
            any(x["invariant"] == "I1" for x in v2["violations"]),
        )
        store.append({"event": "retract_node", "node_id": bad["id"]})
        check("retract restores a clean graph", store.validate()["ok"])

        alias = store.add_node("Entity", "auto-research")
        merged = store.resolve_entities(
            ent["id"], [alias["id"]], run_id="run-1", rationale="same project"
        )
        check("resolve records a reversible merge", merged["merged"] == [alias["id"]])
        check(
            "canonical entity keeps the alias",
            "auto-research" in store.nodes[ent["id"]]["aliases"],
        )

        sub = store.neighborhood([claim["id"]], hops=2)
        check("bounded traversal returns a subgraph", 0 < len(sub["nodes"]) <= len(store.nodes))

        trail = store.find_path(src["id"], ent["id"])
        check("path finds provenance route", len(trail) >= 2)

        rendered = render_all(store)
        html = Path(rendered["files"]["html"]).read_text(encoding="utf-8")
        check("html renders", "<svg" in html and "Karpathy Graph" in html)
        check("html embeds every node", html.count('"type"') >= len(store.nodes))
        check("mermaid renders", Path(rendered["files"]["mermaid"]).read_text().startswith("graph LR"))
        check("report renders", "Invariants" in Path(rendered["files"]["report"]).read_text())

        reloaded = GraphStore.load(store.path)
        check(
            "log replay reproduces the graph",
            len(reloaded.nodes) == len(store.nodes)
            and len(reloaded.edges) == len(store.edges),
            f"{len(reloaded.nodes)}/{len(store.nodes)} nodes",
        )

        ingested = ingest_payload(
            reloaded,
            {
                "nodes": [{"type": "Metric", "name": "val_bpb"}],
                "edges": [
                    {
                        "predicate": "MENTIONS",
                        "source": "Autoresearch",
                        "target": "val_bpb",
                    }
                ],
            },
            run_id="run-2",
        )
        check(
            "ingest resolves edges by name",
            len(ingested["nodes_added"]) == 1 and len(ingested["edges_added"]) == 1,
        )

        default_dir = GraphStore.resolve_dir("My Graph", None)
        check(
            "default path is ./.karpathy-graphs/<slug>",
            default_dir.parent.name == DEFAULT_ROOT and default_dir.name == "my-graph",
            str(default_dir),
        )
        explicit = GraphStore.resolve_dir("My Graph", str(tmp / "custom"))
        check("explicit --path wins", explicit == (tmp / "custom").resolve())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    failed = [c for c in checks if not c["pass"]]
    return {
        "passed": len(checks) - len(failed),
        "total": len(checks),
        "failed": failed,
        "checks": checks,
    }


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "selftest":
            result = selftest()
            emit(result, ok=not result["failed"])
            return 0 if not result["failed"] else 1

        if args.command == "list":
            emit(cmd_list())
            return 0

        directory = GraphStore.resolve_dir(args.name, args.path)

        if args.command == "init":
            store = GraphStore.create(
                name=args.name or directory.name,
                directory=directory,
                objective=args.objective,
                budget=read_json_arg(args.budget) or {},
            )
            render_all(store)
            emit(
                {
                    "graph": store.manifest["name"],
                    "path": str(store.path),
                    "node_types": list(NODE_TYPES),
                    "edge_types": list(EDGE_TYPES),
                    "invariants": list(INVARIANTS),
                }
            )
            return 0

        store = GraphStore.load(directory)

        if args.command == "add-node":
            node = store.add_node(
                node_type=args.type,
                name=args.node_name,
                node_id=args.id,
                description=args.description,
                run_id=args.run_id,
                attrs=parse_kv(args.attr),
            )
            store.save()
            emit({"node": node})

        elif args.command == "add-edge":
            edge = store.add_edge(
                predicate=args.predicate,
                source=args.source,
                target=args.target,
                run_id=args.run_id,
                source_doc=args.source_doc,
                confidence=args.confidence,
                attrs=parse_kv(args.attr),
            )
            store.save()
            emit({"edge": edge})

        elif args.command == "ingest":
            result = ingest_payload(
                store, read_json_arg(args.payload), run_id=args.run_id
            )
            store.save()
            validation = store.validate()
            emit(
                {
                    **result,
                    "invariant_violations": validation["violations"],
                    "stats": validation["stats"],
                }
            )

        elif args.command == "resolve":
            result = store.resolve_entities(
                args.canonical, args.alias, args.run_id, args.rationale
            )
            store.save()
            emit(result)

        elif args.command == "query":
            seeds = [
                n["id"]
                for n in store.find_nodes(args.text, args.type, limit=args.max_nodes)
            ]
            if not seeds:
                emit(
                    {
                        "seeds": [],
                        "nodes": [],
                        "edges": [],
                        "note": "no node matched the query",
                    }
                )
                return 0
            sub = store.neighborhood(
                seeds,
                hops=args.hops,
                edge_types=args.edge_type or None,
                max_nodes=args.max_nodes,
            )
            if args.format == "triples":
                print(serialize_triples(sub, store))
            elif args.format == "context":
                print(serialize_context(sub, store))
            else:
                emit({"seeds": seeds, **sub})

        elif args.command == "path":
            trail = store.find_path(args.source, args.target, args.max_depth)
            emit(
                {
                    "found": bool(trail),
                    "hops": len(trail),
                    "path": trail,
                    "citations": [e["id"] for e in trail],
                }
            )

        elif args.command == "validate":
            result = store.validate()
            emit(result, ok=result["ok"])
            return 0 if result["ok"] else 1

        elif args.command == "stats":
            emit({"graph": store.manifest.get("name"), "stats": store.stats()})

        elif args.command == "render":
            emit(render_all(store))

        elif args.command == "retract":
            if args.node:
                store.append({"event": "retract_node", "node_id": args.node})
            elif args.edge:
                store.append({"event": "retract_edge", "edge_id": args.edge})
            else:
                raise KGraphError("retract requires --node or --edge")
            store.save()
            emit({"retracted": args.node or args.edge, "stats": store.stats()})

        return 0

    except KGraphError as exc:
        emit({"error": str(exc)}, ok=False)
        return 2
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        emit({"error": f"{type(exc).__name__}: {exc}"}, ok=False)
        return 3


if __name__ == "__main__":
    sys.exit(main())
