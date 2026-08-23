---
name: karpathy-graph-evaluate
description: Stage 5 of the karpathy-graph pipeline. Score graph quality across extraction, resolution, structure, query, and operations, and run a ratchet loop that keeps only changes which improve the metric. Use when the user asks how good the graph is, wants to tune extraction prompts or the ontology, asks to measure or improve graph quality, or wants to detect resolution regressions.
metadata:
  version: 1.0.0
---

# Evaluate

The evaluation harness has the same shape as Karpathy's autoresearch loop. The
artifact being optimized is not `train.py` — it is the extraction prompt, the
ontology, the resolution policy, or the query serializer.

```
Read current extraction prompt and score history
  -> Propose ONE motivated change
  -> Run extraction on the gold set
  -> Compute precision, recall, F1, cost, latency
  -> If improved: keep.  If worse: revert.
  -> Record and continue.
```

One change at a time. A batch of five changes that improves the metric teaches
you nothing about which of the five worked.

## Build a gold set first

Without one you are guessing. Take 10–30 representative units of context and
hand-label the entities and relations that should be extracted. Include
adversarial cases deliberately:

- misleading aliases (two different things with near-identical names)
- contradictory dates across sources
- entities that *should not* merge despite high string similarity
- claims with no supporting source
- disconnected paths that look connected

A gold set of only easy cases certifies a system that fails on the hard ones.

## Metrics by layer

Each layer has a metric and a way it misleads you. Track both.

| Layer | Metric | How it misreads |
|---|---|---|
| Extraction | entity/relation precision, recall, F1 | high precision hides missing entities |
| Resolution | pairwise precision/recall, false-merge rate | compression alone rewards over-merging |
| Graph | components, density, isolated nodes | one component is not always desirable |
| Query | answer accuracy, cited-path validity | fluent answers can cite irrelevant edges |
| Workflow | task success, cost, latency | more agents can raise activity without value |
| Operations | recovery rate, corrections | average success hides catastrophic cases |

Also track schema-valid response rate and cost per document. An extraction
prompt that gains two F1 points and triples cost is usually a regression.

## Structural health

```bash
KG="${CLAUDE_PLUGIN_ROOT:-plugins/karpathy-graph}/scripts/kgraph.py"
python3 "$KG" --name "<graph>" stats
python3 "$KG" --name "<graph>" validate
```

Read the trend, not the snapshot:

| Movement | Reads as |
|---|---|
| Isolated nodes jump | resolution regressed, or extraction produced orphans |
| Isolated nodes drop sharply | possible over-merging |
| Components rising | fragmented corpus, or under-merging |
| Components → 1 | check for false merges before calling it success |
| Density falling | relations are being missed |
| Any violation | malformed write — this is a bug, not a metric |

## The ratchet loop

Four conditions make this loop work. Preserve all four:

1. **Verifiable output** — the gold set produces a number
2. **Reversible action** — every change can be undone
3. **Short horizon** — one extraction run, not one full corpus
4. **Bounded environment** — one prompt, one ontology, one policy

```bash
BEST=$(score_against_gold_set)          # baseline
# propose exactly one change
NEW=$(score_against_gold_set)
if better "$NEW" "$BEST"; then
  keep; BEST=$NEW
else
  revert
fi
# record the trial either way — failures are evidence
```

Record reverted trials. A change that failed tells the next iteration where not
to go; discarding it means rediscovering the same dead end.

## Grounding gate

Before an artifact ships, verify that every claim in it traces to a graph path.

```bash
python3 "$KG" --name "<graph>" path <source_entity> <target_entity>
```

Unsupported claim → return structured feedback naming the missing evidence, not
a free-form critique. Template: `references/grounding.md`.

Record the gate itself in the graph, so the evaluation is auditable:

```bash
python3 "$KG" --name "<graph>" --run-id "$RUN" add-node \
  --type Evaluation --name "grounding gate $RUN" \
  --attr rubric="every claim cites a supported edge" \
  --attr result="pass"

python3 "$KG" --name "<graph>" --run-id "$RUN" add-edge \
  --predicate EVALUATES --source <eval_id> --target <artifact_id>
```

Invariant I3 requires the rubric. An evaluation without stated criteria is an
opinion.

## Metrics can be gamed

A ratchet improves the metric it can see. It will happily raise F1 while
tripling cost, or raise compression while corrupting the graph with false
merges.

Hold constraints alongside the objective: cost ceiling, latency ceiling,
false-merge rate ceiling, minimum component count. Optimizing extraction
quality at the price of resolution precision is not an improvement.

## Monitor in production

Track trends over time, not isolated scores: extraction rate by document type,
schema failure rate, resolution compression, connected-component changes, query
latency, subgraph size, cited-edge validity, token cost, stale entity count,
graph write failures, agent retry rates.

A sudden rise in isolated nodes signals a resolution regression. A sudden drop
signals over-merging. Both need a human before the next build.
