---
name: heygen-expert
description: |
  Canonical HeyGen orchestrator. Routes any request touching HeyGen — AI avatars, presenter
  videos, video translation/dubbing, lipsync, or HyperFrames HTML-based video composition
  (motion graphics, captions, slideshows, Remotion ports, faceless explainers, product launch
  videos, PR-to-video, music-to-video, talking-head recuts) — to the correct skill and CLI
  (`heygen`, `npx hyperframes`) instead of guessing or reimplementing what those skills already
  do. Use when the user says "create an avatar", "make a HeyGen video", "translate/dub this
  video", "lipsync", "clone my voice into another language", "generate a talking head video",
  "make a promo/explainer/motion graphic", "hyperframes", "render a composition", or names any
  heygen-* / hyperframes-* skill directly. Decides HeyGen API vs HyperFrames vs CLI-only, and
  how to bridge a HeyGen-generated clip into a HyperFrames composition.
metadata:
  short-description: Canonical HeyGen + HyperFrames orchestrator
---

# HeyGen Expert

Act as the dispatcher for the whole HeyGen skill family installed on this machine. Never
reimplement what a leaf skill or the CLI already does — pick the right one, hand off with the
right inputs, and stop. This skill carries no video-generation logic of its own.

## Two engines, one vendor

HeyGen ships two independent capability sets. Tell them apart before routing:

1. **HeyGen API skills** (`heygen-avatar`, `heygen-video`, `heygen-translate`) — thin wrappers
   over the hosted HeyGen API. Fast, single-clip, presenter-led. Output is a rendered MP4 / share
   URL from HeyGen's servers. Backed by the `heygen` CLI (`~/.local/bin/heygen`, repo
   `heygen-com/skills`).
2. **HyperFrames** (`hyperframes` + ~19 companion skills) — an HTML-based, locally-rendered video
   composition framework (DOM timing via `data-*`, seekable GSAP/Lottie/Three.js runtimes,
   multi-scene, captions, keyframes, Figma import, Remotion ports). Repo `heygen-com/hyperframes`,
   backed by the `hyperframes` / `npx hyperframes` CLI (see `hyperframes-cli`).

They compose: a HeyGen-rendered talking-head clip is a valid **input asset** into a HyperFrames
composition (title cards, lower-thirds, captions, keyframed camera moves wrapped around it). Route
identity/clip generation to the API skills first, then hand the resulting file to HyperFrames for
anything compositional.

## Routing table

Match the requested deliverable, first row wins.

| Request | Route |
|---|---|
| No avatar identity exists yet, and one is needed (agent, user, or a named character) | `heygen-avatar` first — always before `heygen-video` if identity isn't established |
| "Make a HeyGen video / talking head / send a video message" with an avatar_id already known or a stock presenter is fine | `heygen-video` (v3 Video Agent pipeline) |
| Localize / dub / subtitle an **existing** video into another language, same presenter | `heygen-translate` |
| Create identity AND generate a video in the same request ("create an avatar called X and make a video") | `heygen-avatar` → then `heygen-video`, in that order |
| Anything HyperFrames-shaped: promo, explainer, motion graphic, title card, captioned clip, slideshow/deck, overlay, Remotion port, music video, PR-to-video, changelog video, talking-head recut with graphics, Figma import | `hyperframes` (the gateway skill) — do not pre-pick its sub-skill; `hyperframes` owns intent capture, project-state resume, and routing to `hyperframes-core` / `hyperframes-animation` / `hyperframes-creative` / `hyperframes-keyframes` / `hyperframes-registry` / `media-use` / the workflow skills (`faceless-explainer`, `general-video`, `motion-graphics`, `music-to-video`, `pr-to-video`, `product-launch-video`, `remotion-to-hyperframes`, `slideshow`, `talking-head-recut`, `embedded-captions`, `changelog-video`, `figma`) and the doctrine skills (`motion-doctrine`, `cut-the-curve`, `captions-overlay`, `oversized-cursor`, `seam-craft`) |
| A HeyGen clip needs to become part of a bigger composition (title card intro, captions, lower-thirds, camera moves around a talking head) | Generate the clip via `heygen-video`/`heygen-translate` first, then hand the output file to `hyperframes` (`media-use` ingests it as a footage asset; `talking-head-recut` or `general-video` wrap it) |
| Only raw API calls needed — batch jobs, scripting, CI, status polling, asset/voice/brand management, webhooks | `heygen` CLI directly, no skill needed |
| Only HyperFrames CLI operations needed — init, render, preview, publish, doctor, batch-render on an existing project | `hyperframes-cli` / `npx hyperframes <cmd>` directly, skip the gateway's intent interview (its own state table already does this — see "Specific operation on an existing HyperFrames project") |
| Ambiguous ("make a video") | Ask one routing question: presenter-led single clip (→ HeyGen API) or a fuller composition with graphics/captions/multi-scene (→ HyperFrames)? Default to `hyperframes` if the user mentions motion graphics, captions, multi-scene, or a URL/PR/Figma input — those are HyperFrames-shaped by definition |

## `heygen` CLI cheat sheet

Binary: `~/.local/bin/heygen`. JSON output by default; `--human` for tables;
`--request-schema` on any subcommand shows expected JSON input.

```
heygen auth login --api-key|--oauth|--device   # non-interactive shells auto-pick --api-key
heygen avatar   create|list|get|update|delete | looks list|get|update|delete | consent create
heygen video    create|list|get|delete
heygen video-agent create|list|get|send|stop|resources get|styles list|videos list
heygen video-translate create|list|get|update|delete | batches create|get | languages list
                        | proofreads create|generate|get|srt get|srt update | statuses list
heygen lipsync ...            heygen voice ...             heygen asset ...
heygen ai-clipping ...        heygen filler-word-removal ... heygen background-removal ...
heygen brand ...              heygen template ...            heygen webhook ...
heygen user ...                heygen config list             heygen update
```

Env: `HEYGEN_API_KEY` (overrides stored credentials), `HEYGEN_OUTPUT=json|human`. Exit codes:
`0` success, `1` API/network error, `2` usage error, `3` auth error, `4` timeout (resource
created, not yet complete — poll, don't retry the create).

## HyperFrames CLI cheat sheet

Invoke via `npx hyperframes <cmd>` (project pins its own version in `package.json`; `hyperframes-cli`
covers the full loop). Core commands: `init`, `add`, `catalog`, `capture`, `lint`, `check`,
`snapshot`, `compare`, `grade-compare`, `preview`, `play`, `present`, `beats`, `keyframes`,
`render` (single/batch), `publish`, `cloud`, `cloudrun`, `feedback`, `lambda`, `doctor`, `browser`,
`info`, `upgrade`, `skills`, `compositions`, `docs`, `benchmark`, `telemetry`, `transcribe`, `auth`,
`tts`, `remove-background`. `validate`/`inspect`/`layout` are deprecated aliases for `check`.
Rendering targets: local, HeyGen-hosted cloud, AWS Lambda, Google Cloud Run.

## Anti-patterns

- Don't call `heygen-video` before `heygen-avatar` when no identity exists — it will use a stock
  presenter when the user asked for a specific/recurring identity.
- Don't hand-author HyperFrames HTML/JS here — always defer to the `hyperframes` gateway so intent
  capture, project resume, and sub-skill routing stay centralized and don't drift from its own
  state table.
- Don't use `heygen-translate` to create a video that doesn't exist yet — that's `heygen-video`
  with a target-language script.
- Don't skip `hyperframes`'s CLI-pin check on resumed projects (`npx hyperframes@latest upgrade
  --project . --check`) — stale pins silently change render behavior.
- API key management goes through `heygen auth`, never hardcoded or echoed into logs.
