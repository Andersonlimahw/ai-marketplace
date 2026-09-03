---
name: logo-creator-expert
description: Design a minimalist, single-gesture brand mark the way Jony Ive would — one idea, no ornament, tested small before it's called done. Use when the user asks to create/redesign a logo, favicon, or app icon, wants a "minimalist" or "Apple-style" mark, or says a logo feels generic/cluttered/AI-slop.
---

# Logo Creator Expert

A brand mark is one idea, drawn once, that survives 16px. Everything in this
skill exists to force that constraint before any pixel is exported.

## Philosophy (non-negotiable)

1. **One gesture, not a scene.** If the mark needs two metaphors ("it's a pin
   AND a chart AND a handshake"), it is not done — it is three drafts glued
   together. Pick the single idea that carries the whole meaning.
2. **The concept must be nameable in five words.** "Y of Your, staked as a
   pin, seat as the dot." If you can't name it that short, it's decoration,
   not a concept.
3. **Negative space is a design decision, not leftover space.** Prefer a
   knockout, a shared stroke, or a letterform doing double duty over adding
   another shape.
4. **Delete until it breaks, then add back one thing.** Every anchor point,
   gradient, and color must justify its existence. Flat fills over gradients.
   One accent color over a palette.
5. **Design at 1024, judge at 16.** A mark that only works large is not a
   mark, it's an illustration. The kill test is a real (not scaled-up) 16px
   render next to a real 16px competitor favicon.
6. **The mark must earn its story from the product, not from mythology.**
   Don't reach for generic "growth arrows" or "connection nodes" — derive the
   shape from what the product actually does (see Step 1).

## Process

### Step 0 — Read the brand before drawing anything

Never invent a concept from the brand name alone. Pull real constraints first:

- Read `DESIGN.md` / `docs/brand-guidelines.md` / design-tokens files for
  existing color tokens (accent, ink, surface) and product posture language.
- Read `tailwind.config.ts` / `globals.css` / `design-tokens.css` for the
  actual hex values already shipping in the product — the mark must use them,
  not invent a new palette.
- Find the primary UI font already loaded (`next/font/local`, `@font-face`)
  — the wordmark pairs with what's already shipping, not a new typeface.
- Note where the mark is actually consumed (favicon tab, app-icon tile,
  header chip on a light background, dark landing hero, README badge). Each
  context can demand a different background treatment of the *same* mark —
  check call sites (`grep -rn "logo\|favicon\|apple-icon" src`) before
  assuming a transparent PNG is enough.

If invoked with `/brand:brand` or `/design:design` context already loaded in
the conversation, reuse that instead of re-deriving it.

### Step 1 — Extract the single concept from the product, not the name

Ask: what does this product actually *do*, in one sentence? Turn the core
mechanic — not the company name — into a visual pun or reduction:

- A market with one ownable unit → the mark should show *one occupied slot*
  distinct from the rest, not a generic grid/globe/pin.
  A geographic ownership product ("claim a region on a map") became a Y-shaped
  pin (Y = "Your") with the seat as a single filled dot at the vertex — one
  gesture, three meanings (initial, pin, occupancy), same stroke.
- A messaging product → the mark should show the *exchange*, not a generic
  chat bubble.
- A scheduling product → the mark should show the *commitment* (a locked
  slot), not a generic calendar grid.

Generate 4–6 distinct concepts this way, each a different metaphor for the
same mechanic — not 6 variations of the same shape.

### Step 2 — Build a real contact sheet, don't eyeball SVG code

Static SVG markup lies about legibility. Render an actual HTML page with all
candidates at real pixel sizes (128/64/32/16, dark + light background using
the product's real tokens) and view it with `claude-in-chrome` (or
`chrome-devtools` MCP) — never judge from the `<path>` coordinates alone.

```bash
mkdir -p /tmp/<slug>-logo && python3 -m http.server 8899 --directory /tmp/<slug>-logo &
```

Serve over `http://localhost` rather than `file://` — some MCP screenshot
paths behave inconsistently with `file://`. Screenshot the sheet, cut
anything that:
- reads as a stock icon (generic pin, generic globe, generic chat bubble)
- needs color to be understood (fails a grayscale/16px squint test)
- has more than ~4 distinct anchor shapes

Keep 1–2 survivors, then do a second contact-sheet round refining *those*
concepts' proportions (stroke width, corner radius, optical centering) — not
inventing new ones. Two rounds is normal; more than three means Step 1 was
skipped.

### Step 3 — Verify at true small sizes, not scaled-up boxes

A `<div>` with `padding` around a `32px` SVG is not a 32px test — the
surrounding whitespace lies about density. Render each candidate in a bare
`<svg width="16" height="16">` (and 24/32/48) with no padding, on the
product's actual dark and light surface colors, and on the accent color if
the mark ever sits on a colored tile (app icon, social avatar).

### Step 4 — Produce the deliverable set, not just one PNG

A logo task is done when every consumption context is covered, matched to
where Step 0 found the mark is actually used:

- **Transparent mark** (ink-colored, no background) — for light chips, docs,
  anywhere the surrounding surface provides contrast.
- **App-icon tile** (mark on a solid/branded background, correct corner
  radius for the platform) — for favicons, apple-touch-icon, PWA icons,
  social avatars.
- **Full icon size ladder** matching whatever the codebase already references
  (`grep` the exact filenames/sizes before generating — don't guess a generic
  16/32/180/512 set if the project wants 24/72/144/152/384 too).
- **`favicon.ico`** multi-resolution (16/32/48) if the project ships one.
- **Editable source** (`.svg`, flat, one `viewBox`, named layers or at least
  named `<path>` comments) saved back into the repo next to the raster
  exports — the next person must be able to edit it without re-deriving it.

Render pipeline (no paid AI image generation needed for a geometric mark —
draw it directly in SVG for pixel-perfect control):

```bash
rsvg-convert -w <size> -h <size> mark.svg -o icon-<size>.png   # crisp raster
cwebp -q 90 icon-<size>.png -o icon-<size>.webp                 # web format
magick icon-16.png icon-32.png icon-48.png favicon.ico          # multi-res ico
```

### Step 5 — Ship it and verify in the real app, not just the contact sheet

Copy files into place, then start the dev server and load the real page
(header, favicon tab, login screen) — browsers aggressively cache image URLs
that keep the same filename, so hard-reload (`cmd+shift+r`) before judging.
Confirm the mark reads correctly in the actual chip/background it lives in,
not just the isolated contact sheet.

## Revenue-centric framing (when the mark is for a commercial product)

A logo is not decoration — it is the first trust signal a prospect sees.
Two [[revenue-centric-design]] principles apply directly:

- **Your promise is the size of your proof.** A logo that overclaims
  (elaborate, "enterprise-grade"-looking mark on a pre-revenue product) reads
  as incongruent and erodes trust faster than a plain one. Match visual
  ambition to actual proof.
- **Same competes on price, different on category.** A generic
  pin/chat-bubble/handshake mark makes the product look interchangeable with
  every competitor using the same stock metaphor. The Step 1 derivation
  (concept from mechanic, not category convention) is what buys the
  "different" positioning, not extra ornamentation.

## Anti-patterns (reject these on sight)

- Gradient-heavy "AI startup" orbs/blobs with no derivable meaning.
- Literal, clipart-style icons (an actual photo-realistic rocket, handshake,
  lightbulb).
- Wordmark-only when the product needs a standalone favicon/app-icon — always
  design the mark to work with the wordmark removed.
- More than one accent color in the mark itself — let the product's existing
  token system carry color, don't invent a new palette for the logo alone.
- Shipping only a 512px PNG and calling it done — see Step 4.
