---
name: karpathy-loop
description: Executes autonomous Loop Engineering cycles for continuous software engineering optimization — performance, build time, bundle size, test coverage, correctness — against any measurable metric.
version: 2.1.0
---

# Karpathy Loop (Loop Engineering)

Implements **Loop Engineering** — the practice of delegating experimentation loops to an AI agent that iteratively modifies code, runs a timed experiment, evaluates a metric, and decides to keep or revert the change. Generalized from Andrej Karpathy's Autoresearch method to general-purpose software engineering: performance tuning, build/CI optimization, bundle-size reduction, test-coverage loops, flaky-test fixes, refactors — anything with a measurable metric and a revert path. No ML/GPU/dataset assumptions required.

## Core Architecture

Three-part contract:

| Part | Role | Agent Editable? | Required? |
|------|------|----------------|-----------|
| Setup script (wired via the `evaluation_script` field; e.g. `prepare.sh`, fixtures, seed data) | Deterministic baseline for the experiment | No (immutable baseline) | Optional — see `evaluation_script` under `/runLoop` below |
| Target file(s) | The code under optimization — any language, any layer | Yes (agent's playground) | Required |
| `program.md` | Human-written instructions, constraints, metric definition, and acceptance criteria | No (human edits only) | Required |

Each iteration: agent reads `program.md` → forms hypothesis → edits target code → runs timed experiment (default 5 min) → evaluates metric → commits if improved, reverts if regressed.

## Memory Caching Strategy

Two-layer cache for iterative agent loops:

**Layer 1 — Cold Cache (stable context)**
Stable, rarely-changing context reused across every iteration without recomputation:
- `program.md` instructions
- Baseline metrics and experiment contract
- Permission policies and constraints
- Shared system prompts

**Layer 2 — Hot Cache (Prompt Cache)**
Dynamic per-iteration state via OpenAI/Anthropic prompt caching:
- Agent hypotheses generated this session
- Runtime logs and partial results
- Frequently changing context

Cold + hot separation keeps cache size bounded while maximizing reuse. See `/getCacheStatus` endpoint for current cache utilization.

## Endpoints

### `POST /runLoop`
Start an autonomous optimization loop.

```json
{
  "program_file": "./program.md",
  "target_file": "./src/parser.ts",
  "evaluation_script": "./scripts/prepare.sh",
  "metric_name": "p95_latency_ms",
  "max_iterations": 100,
  "timeout_seconds": 300,
  "cache_strategy": "prompt_cache"
}
```

`evaluation_script` is optional — omit it when the target's own existing test/build/bench command already emits `metric_name` directly (e.g. `npm test -- --coverage`, `go test -bench=.`). In that case `program.md` must name the exact command to run; a setup script is only needed when the experiment requires a fixed baseline state the target's own command doesn't already provide.

Response:
```json
{
  "status": "success",
  "data": {
    "loop_id": "loop_a1b2c3d4",
    "status": "running",
    "started_at": "2026-07-09T20:00:00Z"
  }
}
```

### `GET /getResults`
Retrieve loop progress and history.

```json
{
  "loop_id": "loop_a1b2c3d4"
}
```

Response:
```json
{
  "loop_id": "loop_a1b2c3d4",
  "status": "running",
  "current_iteration": 42,
  "best_metric": {
    "name": "p95_latency_ms",
    "value": 142,
    "improvement_pct": 13.9
  },
  "total_improvements": 5,
  "iterations": [
    {
      "number": 38,
      "hypothesis": "Add index on orders.user_id to cut lookup latency",
      "metric_value": 142,
      "accepted": true,
      "duration_seconds": 298
    }
  ],
  "cache_hits": 38,
  "cache_savings_ms": 15200
}
```

### `POST /runExperiment`
Run a single isolated experiment without commit.

```json
{
  "target_file": "./src/parser.ts",
  "dry_run": false,
  "use_cache": true
}
```

Response:
```json
{
  "execution_time_seconds": 298,
  "metric": { "name": "p95_latency_ms", "value": 142 },
  "logs": "test suite: 214 passed, 0 failed... p95_latency_ms final: 142",
  "cached": true
}
```

### `GET /getCacheStatus`
Inspect cache state across layers.

Response:
```json
{
  "prompt_cache": { "active_entries": 3, "hits": 38, "misses": 4, "savings_ms": 15200 },
  "cold_storage": { "cached_files": ["program.md", "baseline.json"], "size_bytes": 24576 }
}
```

### `POST /revertLast`
Revert the last accepted change.

```json
{ "loop_id": "loop_a1b2c3d4" }
```

Response:
```json
{
  "status": "success",
  "reverted_iteration": 38,
  "previous_metric": { "name": "p95_latency_ms", "value": 165 }
}
```

## Permissions

| Permission | Purpose |
|-----------|---------|
| `llm_api_access` | Agent generates hypotheses and code edits via LLM APIs |
| `file_storage_read_write` | Read/write target files, logs, and progress artifacts |
| `network_access` | Fetch dependencies, sync results, call LLM APIs |
| `git_operations` | Commit accepted changes, revert regressions, track history |

## Testing

1. `lemon-cli plugin audit karpathy-loop` — verify all 4 permissions requested
2. Create a mock eval script that prints `p95_latency_ms: 150` → `/runExperiment` → verify metric extraction
3. Write `program.md` targeting metric reduction (e.g. cut `p95_latency_ms`) → `/runLoop` with `max_iterations: 3` → verify autonomous cycle
4. `/getCacheStatus` pre/post loop — verify prompt cache hits increase with shared prefixes
5. `/getResults` during loop + `/revertLast` — verify iteration tracking and git revert
