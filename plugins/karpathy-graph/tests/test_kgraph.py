#!/usr/bin/env python3
"""Test suite for the karpathy-graph plugin.

Runs without pytest so any harness can execute it:

    python3 plugins/karpathy-graph/tests/test_kgraph.py

Covers the engine (via CLI subprocesses, the way agents actually use it) and
the plugin's own structural contract: manifest, skills, agents, references,
and marketplace registration.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
KG = PLUGIN / "scripts" / "kgraph.py"
REPO = PLUGIN.parents[1]

RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    RESULTS.append((label, bool(condition), detail))


def run(*args: str, cwd: Path, expect_rc: int | None = 0) -> dict:
    """Invoke the CLI and parse its JSON envelope."""
    proc = subprocess.run(
        [sys.executable, str(KG), *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )
    if expect_rc is not None and proc.returncode != expect_rc:
        raise AssertionError(
            f"{' '.join(args)} -> rc={proc.returncode} (want {expect_rc})\n"
            f"stdout: {proc.stdout[:800]}\nstderr: {proc.stderr[:800]}"
        )
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"_raw": proc.stdout, "_rc": proc.returncode}


def run_text(*args: str, cwd: Path) -> str:
    proc = subprocess.run(
        [sys.executable, str(KG), *args], cwd=str(cwd), capture_output=True, text=True
    )
    return proc.stdout


def load_engine():
    """Import kgraph.py as a module so store-level guards can be tested directly.

    The CLI wraps these guards in argparse `choices`, which would mask a missing
    check in the store itself.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location("kgraph_mod", KG)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check_store_guards(tmp: Path) -> None:
    """The ontology must be enforced by the store, not only by the CLI parser."""
    mod = load_engine()
    store = mod.GraphStore.create("guards", tmp / "guards")

    try:
        store.add_node("Nonsense", "x")
        check("store rejects an unknown node type", False, "no error raised")
    except mod.KGraphError:
        check("store rejects an unknown node type", True)
    except Exception as exc:  # noqa: BLE001
        check("store rejects an unknown node type", False, f"wrong error: {exc!r}")

    a = store.add_node("Entity", "A")
    b = store.add_node("Entity", "B")

    try:
        store.add_edge("FROBS", a["id"], b["id"])
        check("store rejects an unknown edge type", False, "no error raised")
    except mod.KGraphError:
        check("store rejects an unknown edge type", True)
    except Exception as exc:  # noqa: BLE001
        check("store rejects an unknown edge type", False, f"wrong error: {exc!r}")

    try:
        store.add_edge("MENTIONS", a["id"], "ghost_id")
        check("store rejects an unresolvable edge endpoint", False, "no error raised")
    except mod.KGraphError:
        check("store rejects an unresolvable edge endpoint", True)

    check(
        "a rejected write leaves the store untouched",
        len(store.edges) == 0 and len(store.nodes) == 2,
    )

    # a destructive merge would break reversibility, so the alias must survive
    alias = store.add_node("Entity", "A-alias")
    store.resolve_entities(a["id"], [alias["id"]], run_id="r", rationale="test")
    check("merge keeps the alias node addressable", alias["id"] in store.nodes)
    check(
        "merge records exactly one RESOLVED_TO edge",
        len([e for e in store.edges.values() if e["predicate"] == "RESOLVED_TO"]) == 1,
    )

    # Each invariant is checked in isolation, so that weakening any single one
    # is caught by its own assertion rather than by a neighbouring check.
    probe = mod.GraphStore.create("invariants", tmp / "invariants")

    probe.add_node("Claim", "unsourced")
    v = probe.validate()
    check(
        "I1 fires for a claim with no source",
        any(x["invariant"] == "I1" for x in v["violations"]),
    )
    probe.append({"event": "retract_node", "node_id": probe.find_nodes("unsourced")[0]["id"]})

    probe.add_node("Artifact", "unauthored", attrs={"version": 1})
    v = probe.validate()
    check(
        "I2 fires for an artifact with no authoring run",
        any(x["invariant"] == "I2" for x in v["violations"]),
    )
    probe.append({"event": "retract_node", "node_id": probe.find_nodes("unauthored")[0]["id"]})

    probe.add_node("Evaluation", "no-rubric")
    v = probe.validate()
    check(
        "I3 fires for an evaluation with no rubric",
        any(x["invariant"] == "I3" for x in v["violations"]),
        json.dumps(v["violations"])[:200],
    )
    probe.append({"event": "retract_node", "node_id": probe.find_nodes("no-rubric")[0]["id"]})

    probe.add_node("Evaluation", "with-rubric", attrs={"rubric": "criteria stated"})
    v = probe.validate()
    check("I3 accepts an evaluation that states a rubric", v["ok"], json.dumps(v["violations"])[:200])

    check("all four invariants are documented", len(mod.INVARIANTS) == 4)


# ---------------------------------------------------------------------------
# engine
# ---------------------------------------------------------------------------


def test_engine(tmp: Path) -> None:
    # Store-level guards run first: they are in-process and cannot abort the
    # rest of the suite, so a weakened invariant reports its own assertion
    # rather than surfacing as a downstream CLI exit-code mismatch.
    check_store_guards(tmp)

    # the engine's own end-to-end check
    out = run("selftest", cwd=tmp)
    check(
        "selftest passes every internal check",
        out.get("ok") and not out.get("failed"),
        json.dumps(out.get("failed", []))[:300],
    )

    # default path convention: ./.karpathy-graphs/<slug>/
    out = run("--name", "My Test Graph", "init", "--objective", "unit test", cwd=tmp)
    expected = tmp / ".karpathy-graphs" / "my-test-graph"
    check(
        "init writes to ./.karpathy-graphs/<slug> when no path is given",
        Path(out["path"]).resolve() == expected.resolve(),
        out.get("path", ""),
    )
    check(
        "init creates manifest, log and graph files",
        (expected / "manifest.json").is_file()
        and (expected / "log.jsonl").is_file()
        and (expected / "graph.json").is_file(),
    )

    # explicit --path overrides the default root
    custom = tmp / "custom" / "place"
    out = run("--path", str(custom), "init", "--objective", "explicit", cwd=tmp)
    check(
        "explicit --path overrides the default root",
        Path(out["path"]).resolve() == custom.resolve(),
    )

    # init never silently overwrites
    out = run("--name", "My Test Graph", "init", cwd=tmp, expect_rc=2)
    check("init refuses to overwrite an existing graph", out.get("ok") is False)

    G = ("--name", "My Test Graph")

    # ingest resolves edge endpoints by name
    payload = {
        "nodes": [
            {"type": "AgentRun", "name": "run_a"},
            {"type": "Source", "name": "doc.md", "uri": "./doc.md"},
            {"type": "Entity", "name": "Widget", "aliases": ["widgets"]},
            {"type": "Claim", "name": "Widget ships weekly"},
            {"type": "Artifact", "name": "out.md", "version": 1},
            {"type": "Evaluation", "name": "gate", "rubric": "cited"},
        ],
        "edges": [
            {
                "predicate": "SUPPORTS",
                "source": "doc.md",
                "target": "Widget ships weekly",
                "source_doc": "doc.md#1",
                "confidence": 0.9,
            },
            {"predicate": "MENTIONS", "source": "Widget ships weekly", "target": "Widget"},
            {"predicate": "PRODUCED", "source": "run_a", "target": "out.md"},
            {"predicate": "EVALUATES", "source": "gate", "target": "out.md"},
        ],
    }
    out = run(*G, "--run-id", "run_a", "ingest", json.dumps(payload), cwd=tmp)
    check(
        "ingest applies a payload and resolves endpoints by name",
        out["ok"] and len(out["nodes_added"]) == 6 and len(out["edges_added"]) == 4,
    )
    check("well-formed payload violates no invariant", not out["invariant_violations"])

    # run_id provenance lands on written nodes
    graph = json.loads((expected / "graph.json").read_text())
    check(
        "run id is stamped on every written node",
        all(n.get("run_id") == "run_a" for n in graph["nodes"]),
    )

    # validate gates on invariants
    out = run(*G, "validate", cwd=tmp)
    check("validate passes on a well-formed graph", out["ok"])

    # I1: unsourced claim is rejected
    run(*G, "--run-id", "run_a", "add-node", "--type", "Claim", "--name", "floating", cwd=tmp)
    out = run(*G, "validate", cwd=tmp, expect_rc=1)
    check(
        "I1 rejects a claim with no source",
        any(v["invariant"] == "I1" for v in out["violations"]),
    )
    check("validate exits non-zero on violation", out["ok"] is False)

    floating = next(
        n["id"]
        for n in json.loads((expected / "graph.json").read_text())["nodes"]
        if n["name"] == "floating"
    )
    run(*G, "retract", "--node", floating, cwd=tmp)
    out = run(*G, "validate", cwd=tmp)
    check("retract restores a clean graph", out["ok"])

    # I1 escape hatch: explicit inference
    run(
        *G, "--run-id", "run_a", "add-node", "--type", "Claim",
        "--name", "inferred thing", "--attr", "inference=true", cwd=tmp,
    )
    out = run(*G, "validate", cwd=tmp)
    check("I1 accepts a claim marked inference=true", out["ok"])

    # I3: evaluation without a rubric
    run(*G, "--run-id", "run_a", "add-node", "--type", "Evaluation", "--name", "no rubric", cwd=tmp)
    out = run(*G, "validate", cwd=tmp, expect_rc=1)
    check(
        "I3 rejects an evaluation with no rubric",
        any(v["invariant"] == "I3" for v in out["violations"]),
    )
    norubric = next(
        n["id"]
        for n in json.loads((expected / "graph.json").read_text())["nodes"]
        if n["name"] == "no rubric"
    )
    run(*G, "retract", "--node", norubric, cwd=tmp)

    # I2: artifact with no authoring run
    run(
        *G, "--run-id", "run_a", "add-node", "--type", "Artifact",
        "--name", "orphan.md", "--attr", "version=1", cwd=tmp,
    )
    out = run(*G, "validate", cwd=tmp, expect_rc=1)
    check(
        "I2 rejects an artifact with no authoring run",
        any(v["invariant"] == "I2" for v in out["violations"]),
    )
    orphan = next(
        n["id"]
        for n in json.loads((expected / "graph.json").read_text())["nodes"]
        if n["name"] == "orphan.md"
    )
    run(*G, "retract", "--node", orphan, cwd=tmp)
    check("graph is clean again after retraction", run(*G, "validate", cwd=tmp)["ok"])

    # unknown types are rejected, not silently accepted.
    # argparse rejects the choice itself, so this one exits 2 without a JSON
    # envelope — assert on the exit code and the message instead.
    proc = subprocess.run(
        [sys.executable, str(KG), *G, "add-node", "--type", "Nonsense", "--name", "x"],
        cwd=str(tmp), capture_output=True, text=True,
    )
    check(
        "unknown node type is rejected",
        proc.returncode == 2 and "invalid choice" in proc.stderr,
    )
    out = run(
        *G, "ingest",
        json.dumps({"nodes": [], "edges": [{"predicate": "FROBS", "source": "a", "target": "b"}]}),
        cwd=tmp, expect_rc=2,
    )
    check("unknown edge type is rejected via ingest", out.get("ok") is False)

    # The ontology is fixed by design. add-edge must reject unknown predicates
    # even when both endpoints resolve — otherwise the type system is advisory.
    ids = {n["name"]: n["id"] for n in json.loads((expected / "graph.json").read_text())["nodes"]}
    proc = subprocess.run(
        [sys.executable, str(KG), *G, "add-edge", "--predicate", "FROBS",
         "--source", ids["Widget"], "--target", ids["doc.md"]],
        cwd=str(tmp), capture_output=True, text=True,
    )
    check(
        "unknown edge type is rejected via add-edge",
        proc.returncode == 2 and "invalid choice" in proc.stderr,
    )

    # argparse's `choices` guards the CLI surface; check_store_guards (run at
    # the top of this suite) covers the in-process path that bypasses argparse.
    edges = json.loads((expected / "graph.json").read_text())["edges"]
    check(
        "a rejected edge type is never written",
        not [e for e in edges if e["predicate"] == "FROBS"],
    )
    check(
        "every stored edge uses a known predicate",
        all(e["predicate"] in (
            "MENTIONS", "SUPPORTS", "CONTRADICTS", "DERIVED_FROM", "PRODUCED",
            "EVALUATES", "REVISES", "SUPERSEDES", "DEPENDS_ON", "PARENT_OF",
            "RESOLVED_TO",
        ) for e in edges),
    )
    check(
        "every stored node uses a known type",
        all(n["type"] in (
            "Entity", "Claim", "Source", "Artifact", "AgentRun",
            "Evaluation", "Task", "Commit", "Metric",
        ) for n in json.loads((expected / "graph.json").read_text())["nodes"]),
    )

    # entity resolution is reversible and keeps aliases
    ids = {n["name"]: n["id"] for n in json.loads((expected / "graph.json").read_text())["nodes"]}
    run(*G, "--run-id", "run_a", "add-node", "--type", "Entity", "--name", "widget-alias", cwd=tmp)
    ids = {n["name"]: n["id"] for n in json.loads((expected / "graph.json").read_text())["nodes"]}
    out = run(
        *G, "--run-id", "run_a", "resolve",
        "--canonical", ids["Widget"], "--alias", ids["widget-alias"],
        "--rationale", "same widget, different casing", cwd=tmp,
    )
    check("resolve merges the alias", out["merged"] == [ids["widget-alias"]])

    nodes = {n["id"]: n for n in json.loads((expected / "graph.json").read_text())["nodes"]}
    check(
        "alias node stays addressable after the merge",
        ids["widget-alias"] in nodes,
    )
    check(
        "canonical entity absorbs the alias name",
        "widget-alias" in nodes[ids["Widget"]]["aliases"],
    )
    edges = json.loads((expected / "graph.json").read_text())["edges"]
    resolved = [e for e in edges if e["predicate"] == "RESOLVED_TO"]
    check("merge records a RESOLVED_TO edge", len(resolved) == 1)
    check(
        "merge records its rationale",
        resolved[0]["attrs"].get("rationale") == "same widget, different casing",
    )
    run(*G, "retract", "--edge", resolved[0]["id"], cwd=tmp)
    edges = json.loads((expected / "graph.json").read_text())["edges"]
    check(
        "a false merge is undone by retracting one edge",
        not [e for e in edges if e["predicate"] == "RESOLVED_TO"],
    )

    # bounded retrieval
    out = run(*G, "query", "Widget", "--hops", "2", cwd=tmp)
    check("query returns seeds and a bounded subgraph", out["seeds"] and out["nodes"])
    out = run(*G, "query", "Widget", "--hops", "2", "--max-nodes", "2", cwd=tmp)
    check("max-nodes caps the neighbourhood", len(out["nodes"]) <= 2)
    out = run(*G, "query", "definitely-not-present", cwd=tmp)
    check("query with no match returns empty, not an error", out["ok"] and not out["nodes"])

    # prompt-ready serializations
    text = run_text(*G, "query", "Widget", "--format", "context", cwd=tmp)
    check("context format lists entities and relations", "## Entities" in text and "## Relations" in text)
    check("context format carries edge citations", "[edge:" in text)
    text = run_text(*G, "query", "Widget", "--format", "triples", cwd=tmp)
    check("triples format emits cited triples", "-MENTIONS->" in text and "[edge:" in text)

    # edge-type filtering
    out = run(*G, "query", "Widget", "--hops", "2", "--edge-type", "SUPPORTS", cwd=tmp)
    check(
        "edge-type filter restricts traversal",
        all(e["predicate"] == "SUPPORTS" for e in out["edges"]),
    )

    # grounding
    ids = {n["name"]: n["id"] for n in json.loads((expected / "graph.json").read_text())["nodes"]}
    out = run(*G, "path", ids["doc.md"], ids["Widget"], cwd=tmp)
    check("path finds a provenance route", out["found"] and out["hops"] >= 2)
    check("path returns edge citations", len(out["citations"]) == out["hops"])
    out = run(*G, "path", ids["doc.md"], ids["run_a"], cwd=tmp)
    check("path reports honestly when no route exists", out["found"] is False)

    # render artifacts
    run(
        *G, "--run-id", "run_a", "add-node", "--type", "Entity",
        "--name", "</script><img src=x onerror=alert(1)>", cwd=tmp,
    )
    out = run(*G, "render", cwd=tmp)
    for label, key in (("report", "report"), ("html", "html"), ("mermaid", "mermaid")):
        check(f"render writes {label}", Path(out["files"][key]).is_file())
    html = Path(out["files"]["html"]).read_text()
    # the only allowed URL is the SVG XML namespace, which is an identifier and
    # is never fetched; anything else would make the explorer network-dependent
    stripped = html.replace("http://www.w3.org/2000/svg", "")
    check(
        "html is self-contained (no external requests)",
        "http://" not in stripped and "https://" not in stripped,
    )
    check(
        "html loads no external script or stylesheet",
        "<script src" not in html and "<link" not in html,
    )
    check("html embeds the graph payload", '"nodes"' in html and '"edges"' in html)
    check("html renders an svg canvas", "<svg" in html)
    check(
        "html keeps graph payload terminators inert",
        "\\u003c/script\\u003e" in html and "<img src=x onerror" not in html,
    )
    check(
        "html escapes interactive graph values",
        "const escapeHtml" in html and "escapeHtml(node.name)" in html,
    )
    report = Path(out["files"]["report"]).read_text()
    check("report states the invariants", "I1" in report and "I4" in report)
    check("report shows health metrics", "Connected components" in report)
    mmd = Path(out["files"]["mermaid"]).read_text()
    check("mermaid is valid graph source", mmd.startswith("graph LR"))

    # log replay: graph.json is derived, log.jsonl is the truth
    (expected / "graph.json").unlink()
    out = run(*G, "render", cwd=tmp)
    check(
        "graph.json is rebuilt from the append-only log",
        (expected / "graph.json").is_file() and out["stats"]["nodes"] > 0,
    )

    # list
    out = run("list", cwd=tmp)
    check("list finds graphs under the default root", any(g["name"] == "My Test Graph" for g in out["graphs"]))

    # stats
    out = run(*G, "stats", cwd=tmp)
    for key in ("nodes", "edges", "density", "components", "isolated_nodes"):
        check(f"stats reports {key}", key in out["stats"])


# ---------------------------------------------------------------------------
# plugin structure
# ---------------------------------------------------------------------------

EXPECTED_SKILLS = [
    "karpathy-graph-build",
    "karpathy-graph-extract",
    "karpathy-graph-resolve",
    "karpathy-graph-query",
    "karpathy-graph-visualize",
    "karpathy-graph-swarm",
    "karpathy-graph-evaluate",
]

EXPECTED_AGENTS = ["graph-builder", "graph-querier", "graph-orchestrator"]

EXPECTED_REFERENCES = [
    "ontology.md",
    "cli.md",
    "decision-framework.md",
    "grounding.md",
    "multi-agent.md",
]


def frontmatter(path: Path) -> dict:
    """Minimal YAML frontmatter reader — top-level scalar keys only."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    block = text.split("---", 2)[1]
    out: dict[str, str] = {}
    for line in block.splitlines():
        if line.startswith((" ", "\t")) or ":" not in line:
            continue
        key, value = line.split(":", 1)
        out[key.strip()] = value.strip()
    return out


def test_structure() -> None:
    manifest = json.loads((PLUGIN / "plugin.json").read_text())
    check("plugin.json declares the plugin name", manifest["name"] == "karpathy-graph")
    check("plugin.json has a version", bool(manifest.get("version")))
    check("plugin.json has a license", manifest.get("license") == "MIT")
    check(
        "plugin.json description carries trigger phrases",
        "knowledge graph" in manifest["description"].lower(),
    )
    check(
        "plugin.json keywords follow hub convention",
        {"skill", "lemon-ai-hub", "karpathy-graph"} <= set(manifest.get("keywords", [])),
    )

    root_skill = frontmatter(PLUGIN / "SKILL.md")
    check("root SKILL.md has valid frontmatter", root_skill.get("name") == "karpathy-graph")
    check("root SKILL.md has a description", len(root_skill.get("description", "")) > 80)
    check(
        "root SKILL.md documents the default path",
        ".karpathy-graphs/" in (PLUGIN / "SKILL.md").read_text(),
    )

    for name in EXPECTED_SKILLS:
        path = PLUGIN / "skills" / name / "SKILL.md"
        check(f"skill {name} exists", path.is_file())
        if path.is_file():
            fm = frontmatter(path)
            check(f"skill {name} frontmatter name matches its directory", fm.get("name") == name)
            check(f"skill {name} has a usable description", len(fm.get("description", "")) > 60)

    for name in EXPECTED_AGENTS:
        path = PLUGIN / "agents" / f"{name}.md"
        check(f"agent {name} exists", path.is_file())
        if path.is_file():
            fm = frontmatter(path)
            check(f"agent {name} frontmatter name matches its file", fm.get("name") == name)
            check(f"agent {name} declares tools", bool(fm.get("tools")))

    for name in EXPECTED_REFERENCES:
        check(f"reference {name} exists", (PLUGIN / "references" / name).is_file())

    check("AGENTS.md exists for cross-harness use", (PLUGIN / "AGENTS.md").is_file())
    check("README.md exists", (PLUGIN / "README.md").is_file())
    check("engine script exists", KG.is_file())
    check("engine script is executable", os.access(KG, os.X_OK))

    # no broken internal references
    missing: list[str] = []
    for doc in list(PLUGIN.rglob("*.md")):
        text = doc.read_text(encoding="utf-8")
        for ref in EXPECTED_REFERENCES:
            token = f"references/{ref}"
            if token in text and not (PLUGIN / "references" / ref).is_file():
                missing.append(f"{doc.name} -> {token}")
    check("no document points at a missing reference", not missing, "; ".join(missing))

    # marketplace registration is mandatory in this repo
    market_path = REPO / ".claude-plugin" / "marketplace.json"
    if market_path.is_file():
        market = json.loads(market_path.read_text())
        entry = next((p for p in market["plugins"] if p["name"] == "karpathy-graph"), None)
        check("plugin is registered in marketplace.json", entry is not None)
        if entry:
            check(
                "marketplace source points at the plugin directory",
                entry["source"] == "./plugins/karpathy-graph",
            )
            check(
                "marketplace version matches plugin.json",
                entry.get("version") == manifest["version"],
            )
            check(
                "marketplace description matches plugin.json",
                entry.get("description") == manifest["description"],
            )


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="kgraph-tests-"))
    try:
        # A crash mid-suite is itself a failure to report, not a reason to lose
        # every check that already ran — record it and keep the results.
        for name, fn in (("engine", lambda: test_engine(tmp)), ("structure", test_structure)):
            try:
                fn()
            except Exception as exc:  # noqa: BLE001
                check(f"{name} suite ran to completion", False, f"{type(exc).__name__}: {exc}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    failed = [r for r in RESULTS if not r[1]]
    for label, ok, detail in RESULTS:
        if not ok:
            print(f"FAIL  {label}" + (f"  — {detail}" if detail else ""))
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} checks passed")
    if failed:
        print(f"{len(failed)} FAILED")
        return 1
    print("all green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
