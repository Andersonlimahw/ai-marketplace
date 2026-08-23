# Field Lessons — React Native / Expo / EAS App Store Rejections

Rejection patterns observed across five consecutive App Review cycles on a production React Native + Expo + EAS + RevenueCat app (July–August 2026). Every entry below is a rejection that actually happened, its confirmed root cause, and the gate that prevents it. Use this alongside `review-checklists.md`; this file covers what the generic Apple guidance does not: the cross-stack failure modes specific to RN/Expo/EAS/RevenueCat submissions.

## Contents

- [Rejection Timeline](#rejection-timeline)
- [2.1(a) — Dead Interactive Elements](#21a--dead-interactive-elements)
- [2.1(a) — Login Loop from Auth Listener Null-Flash](#21a--login-loop-from-auth-listener-null-flash)
- [2.1(b) — Entitlement Locked After Sandbox Purchase](#21b--entitlement-locked-after-sandbox-purchase)
- [3.1.2(c) — Subscription Price Hierarchy](#312c--subscription-price-hierarchy)
- [3.1.1 — Non-IAP Digital Currency Paths](#311--non-iap-digital-currency-paths)
- [2.3.2 — Duplicate IAP Metadata and Promo Images](#232--duplicate-iap-metadata-and-promo-images)
- [2.3.6 — Age Rating Declares Features That Do Not Exist](#236--age-rating-declares-features-that-do-not-exist)
- [2.3.10 / 2.3.3 — Screenshots](#2310--233--screenshots)
- [5.1.1(iv) — Pre-Permission Button Copy](#511iv--pre-permission-button-copy)
- [5.1.1(ix) — Individual vs Organization Enrollment](#511ix--individual-vs-organization-enrollment)
- [4.8 — Login Services Equivalence](#48--login-services-equivalence)
- [1.5 — Support URL Must Actually Support](#15--support-url-must-actually-support)
- [3.1.2 — Terms of Use / EULA Link](#312--terms-of-use--eula-link)
- [Build, Version, and Submission Pipeline](#build-version-and-submission-pipeline)
- [iPad Is the Review Device](#ipad-is-the-review-device)
- [App Store Connect API — What It Can and Cannot Do](#app-store-connect-api--what-it-can-and-cannot-do)
- [Pre-Submission Gate Script](#pre-submission-gate-script)

---

## Rejection Timeline

Five cycles on one app. The pattern to internalize: **each fix surfaced the next layer of issues.** Assume at least two more rounds after any fix, and front-load the full checklist rather than fixing only what the reviewer cited.

| Date | Guidelines cited | Theme |
|---|---|---|
| Jul 15, 2026 | 2.3.10, 4.8, 2.1(a) | Screenshots with non-iOS status bars; no Sign in with Apple; login loop |
| Jul 21, 2026 | 2.1(b), 5.1.1(ix), 3.1.1, 2.3.6, 1.5 | Business model questions; individual account; non-IAP currency; age rating; dead support URL |
| Jul 25, 2026 | 2.1(a), 2.3.3 | Login loop persisted (reviewed build predated the fix); iPad screenshots were mockups |
| Aug 18, 2026 | 2.3.2 ×2, 2.3.6, 3.1.2(c), 2.1(b), 2.1(a), 5.1.1(iv) | Duplicate IAP metadata; price hierarchy; entitlement locked; dead buttons; permission copy |

**Meta-lesson:** the same guideline was cited across cycles for *different* root causes (2.1(a) was first an auth bug, later a missing `onPress`). Never assume a repeat citation means the previous fix regressed — re-diagnose from scratch.

---

## 2.1(a) — Dead Interactive Elements

**What happened:** a `TouchableOpacity` had `accessibilityRole="button"` and full styling but **no `onPress`**. The reviewer tapped "Rate app" on iPad; nothing happened. Instant 2.1(a).

```tsx
// REJECTED — signals interactive to VoiceOver and to the reviewer, does nothing
<TouchableOpacity style={styles.menuButton} accessibilityRole="button">
  <Text>{t("settings.support.rateApp")}</Text>
</TouchableOpacity>
```

**Gate — run before every submission:**

```bash
rg -n "TouchableOpacity|Pressable" src --glob '*.tsx' -A6 \
  | rg -B6 "accessibilityRole" | rg -v "onPress"
# expect: no results
```

**Related trap — native review prompt is a silent no-op.** `StoreReview.requestReview()` (Expo) / `SKStoreReviewController` does nothing in App Review builds, and is rate-limited to ~3 prompts per year per user. A "Rate app" button wired only to the native prompt still reads as broken to the reviewer. **Always fall back to the App Store product page:**

```ts
if (await StoreReview.hasAction()) {
  await StoreReview.requestReview();       // may be a silent no-op
} else {
  await Linking.openURL(`https://apps.apple.com/app/id${APP_ID}?action=write-review`);
}
```

Treat "nothing visible happened" as a failing state: surface a snackbar rather than returning silently.

**Related trap — nested confirmation sheets race on iPad.** Two chained `confirmAction()` calls (second fired inside the first's `onConfirm`) raced against the first sheet's dismissal animation. On iPhone it worked; on iPad's larger layout and different animation timing, the second sheet never rendered — "Delete account" appeared dead. Use one confirmation at a time (explicit step state, or a single sheet with the irreversible copy inline). Apple does not require double confirmation — only that deletion *works*.

---

## 2.1(a) — Login Loop from Auth Listener Null-Flash

**What happened:** "we were unable to login as the app kept bringing us back to the login screen." Reproduced on iPad, in release builds only.

**Root cause:** during `signInWithCredential`, native Firebase Auth emits a **transient `onAuthStateChanged(null)`** followed by the real user event. In release builds the JS bridge batches differently: the recovery event arrived *while* the store was still ignoring events (`loading === true`) and was discarded, then the stale null arrived *after* `loading = false` and destroyed the freshly-created session. No error, no crash — the user just bounced back to login. A cold start restored the session from the keychain, which is why it looked unreproducible locally.

**Fix — two independent layers:**

1. **Repository layer:** a null auth event is re-checked against `getAuth().currentUser` with progressive delays (e.g. 250 + 300 + 300 ms). If the native side already recovered a user, the null is *dropped* and never reaches consumers.
2. **Store layer:** a late null arriving while a session is established triggers a revalidation via `getCurrentUser()` before clearing. User present = null-flash, keep the session. User absent = real sign-out, clear. Revalidation failure = keep the session (safe default).

**Generalize:** never apply `user: null` from an auth event without either a settle window at the SDK boundary or a revalidation against the native source. "Ignore events while loading" guards are necessary but never sufficient — native event delivery has no ordering guarantee relative to JS promises.

**Related trap — logout must not disable the next login.** Sign-out that tears down the auth listener lifecycle leaves the following `signIn()` with nothing to publish the user. Keep the listener alive after explicit logout; reserve full lifecycle teardown for app shutdown.

**Related trap — offline is not signed-out.** A Firestore `client is offline` error is a read/network failure, not proof the user is logged out. Preserve the known session, classify the error, offer recovery.

**Gate:** test cold start, reload with a persisted session, logout, user switch, transient network loss and recovery — on **both** iPhone and iPad, in a **release/TestFlight build**, not a dev build.

---

## 2.1(b) — Entitlement Locked After Sandbox Purchase

**What happened:** "the premium content remained locked after purchase" in the sandbox on iPad. Confirmed architectural root cause, not a flake.

**Root cause:** the purchase flow validated against a server-side webhook and treated `entitlementGranted === false` as `"pending"` with no retry and no local fallback. In sandbox the RevenueCat/StoreKit webhook frequently has not processed the transaction when the app asks — so the app locked premium permanently while the **local `customerInfo` already had the entitlement active**.

```ts
// REJECTED — no refresh, no retry, no local fallback
async syncEntitlements(userId: string) {
  return this.fetchEntitlement(userId);   // reads backend only
}

// CORRECT — invalidate cache, read fresh customerInfo, fall back to backend
async syncEntitlements(userId: string) {
  await Purchases.invalidateCustomerInfoCache();
  const info = await Purchases.getCustomerInfo();
  const active = info.entitlements.active[PREMIUM_ENTITLEMENT_ID];
  if (active) return mapCustomerInfoToEntitlement(userId, active, info);
  return this.fetchEntitlement(userId);
}
```

Plus, in the purchase use case: when validation succeeds but the entitlement is not yet granted, retry `syncEntitlements` with backoff (e.g. 500 / 1500 / 3000 ms) and, if still empty, grant from the local `customerInfo`. The RevenueCat SDK knows the entitlement the instant the purchase completes; depending solely on the webhook is what produces "premium remained locked."

**Trade-off to state explicitly in the PR:** granting from local `customerInfo` weakens the anti-fraud barrier. Mitigation: the backend continues validating asynchronously and can revoke. This is an optimistic-UX decision that satisfies 2.1(b) — get the account owner's sign-off rather than making it silently.

**UI gate:** after the entitlement is granted, the paywall must close or flip to "already premium" **without an app restart**. Audit every entitlement consumer for reactive re-render.

**Environment gates that block IAP entirely:**
- **Paid Applications Agreement must be `Active`** (Agreements, Tax, and Banking). Pending banking or tax = no purchase works for anyone, including the reviewer.
- Sandbox testers exist and are signed in under **Settings → App Store → Sandbox Account** (not the main Apple ID).
- Test on a **physical iPad**. The simulator does not reproduce sandbox IAP behavior faithfully.

---

## 3.1.2(c) — Subscription Price Hierarchy

**What happened:** the paywall rendered the calculated per-month figure ("R$ 8,33/mês") at the same visual weight as the amount actually billed ("R$ 99,90/ano"). Apple requires the **billed amount to be clear and conspicuous**, with everything else subordinate in size *and* position.

**Required hierarchy inside the plan card:**

```
┌─────────────────────────────────┐
│  Annual                         │  plan name
│  $99.90 / year                  │  BILLED AMOUNT — largest, highest contrast
│  equivalent to $8.33/month      │  calculated — smaller, muted
│  Renews automatically           │  disclosure
└─────────────────────────────────┘
```

The billed amount must be the largest typographic element in the card. No badge ("Best value", "Save 40%") may compete with it in size or contrast.

**Related trap — hardcoded derived prices.** The per-month string was a fixed literal in the locale file rather than derived from `product.price / 12`. Any price tier or storefront change makes it a lie — a future 2.3.2 on its own. Always compute the equivalent from the live product price, respecting the product's currency and locale.

**Also required before purchase:** duration, billing frequency, auto-renewal terms, and for trials the trial length, post-trial price, and cancellation terms.

---

## 3.1.1 — Non-IAP Digital Currency Paths

**What happened:** "The Sport Coins can be purchased in the app using payment mechanisms other than In-App Purchase."

**Root cause:** a legacy wallet flow that called a local credit path after an external checkout, letting balance be credited without server-side confirmation.

**Fix pattern:**
1. Remove every external purchase path, link, button, and CTA for digital goods from the iOS build — not just the button, but the routes, deep links, offering loads, and shortcuts.
2. Make the server webhook the **only** origin of credit ledger entries, with an idempotent transaction keyed on the provider `event.id`.
3. Block client-side creation of purchase-credit entries in Firestore/backend security rules.
4. Where a feature cannot be made compliant in time, gate it off for iOS via a remote config flag with an OS-name condition — and verify the tab, menu entries, home CTAs, routes, **and deep links** all redirect, not just the visible entry point.

**Verification:** confirm the gated surface is unreachable via deep link and that no offering for the removed SKUs is loaded on iOS.

**Note (5.3.3):** IAP may not be used to buy credit or currency used for real-money gaming. If the product looks like that to Apple, no amount of StoreKit correctness fixes it.

---

## 2.3.2 — Duplicate IAP Metadata and Promo Images

Two distinct rejections from the same guideline in one cycle:

1. **Identical display name + description** across the monthly and annual subscriptions. Each product must be unique **within each locale** — differing in PT while EN and ES stay identical still fails.
   - Hard limits: display name **30 characters**, description **45 characters**.
2. **The same promotional image** uploaded for two promoted IAPs.
   - Cheapest fix, offered by Apple in the rejection text itself: if you have no plans to promote the IAP, **delete the promotional image**.
   - If promoting: 1024×1024 PNG/JPG, no transparency, no rounded corners, and **visually distinct** per product — swapping one word is not enough.

**Gate:** enumerate every product × locale combination and diff them pairwise before submitting.

---

## 2.3.6 — Age Rating Declares Features That Do Not Exist

**What happened:** the Age Rating declared *In-App Controls*, but the reviewer found neither Parental Controls nor an Age Assurance mechanism.

Age rating answers are metadata claims. If you declare a control, the reviewer must be able to **find and operate it**. Either set the declaration to `None`, or reply with the precise navigation path to the feature (screen, action, and the exact gate it enforces).

This one cost two cycles: the first response argued the feature existed via a video-age-gate sheet; the reviewer still could not locate it. When a declaration is defensible only via a written explanation, prefer setting it to `None` unless the feature is genuinely front-and-center.

---

## 2.3.10 / 2.3.3 — Screenshots

Two separate rejections, both about screenshots:

- **2.3.10:** screenshots contained **non-iOS status bars** (Android frames / third-party mockup templates).
- **2.3.3:** iPad 13-inch screenshots were **marketing mockups**, not the app in use. Apple requires the majority of screenshots to highlight the app's actual main features.

**Rules learned:**

- Capture from the **candidate iOS build itself**. Never mockups, never promotional renders, never Android frames or third-party device chrome.
- The binary's language does **not** select the metadata language. Upload is per App Store Connect locale — English assets to `English (U.S.)`, Portuguese to `Portuguese (Brazil)`, and so on.
- Every device family, size, and orientation is an **independent slot set**. Use **View All Sizes in Media Manager** and scroll each tab to the end. The default preview hides slots that still hold old assets.
- Record file, locale, device slot, dimensions, and visual confirmation for each upload. Do not declare "screenshots fixed" while any stale slot remains.
- Dimensions accepted in practice for this app: iPhone 6.9" — `1320×2868` (also `1284×2778`, `1242×2688`, `2688×1242`, `2778×1284`); iPad 13" — `2064×2752` or `2048×2732`; iPad 11" — `1668×2388`. Always confirm against the slot App Store Connect displays.
- Re-capture screenshots whenever the reviewed UI changed. Shipping a paywall fix while the store still shows the old paywall invites a fresh 2.3.2.

---

## 5.1.1(iv) — Pre-Permission Button Copy

**What happened:** the custom pre-permission screen before the camera prompt had a button labeled "Grant Permission" / "Conceder Permissão". Apple's instruction was literal: *"Use words like 'Continue' or 'Next' on the button instead."*

A pre-permission screen may explain **why** you need access, but its button must not imply it grants the permission — only the system prompt does that. Change the visible label **and** the `accessibilityLabel` (reviewers use VoiceOver).

The recovery branch (permission already denied, `!canAskAgain`) may still say "Open Settings" — that is not a pre-permission button.

**Gate:**

```bash
rg -n "Grant Permission|Conceder Permissão|Otorgar Permiso" src/
# expect: no results
```

Apply the same rule to every permission pre-prompt: camera, photos, notifications, location, contacts, microphone.

---

## 5.1.1(ix) — Individual vs Organization Enrollment

**What happened:** Apple classified the app as offering highly regulated services / handling sensitive user data and required the submitting account to be enrolled as an **organization**, not an individual.

This is not fixable in code. There is no documentation workaround — Apple states explicitly that permission letters do not resolve it. Options: enroll a new organization account, or request conversion of the individual account through Apple Developer Support.

**Front-load this check.** If the app touches finance, wagering, health, or similarly regulated territory, resolve enrollment before spending cycles on code fixes — every other fix is blocked behind it.

---

## 4.8 — Login Services Equivalence

**What happened:** the app offered third-party login (Google) without an equivalent option that limits collection to name and email, lets the user keep the email private, and does not collect in-app interactions for advertising without consent.

**Fix:** add Sign in with Apple, which satisfies all three by definition.

**Implementation traps specific to RN/Firebase:**
- Generate a **fresh nonce per attempt**; reuse fails credential exchange.
- Handle **silent cancellation** — the user dismissing the sheet must not surface as an error state or leave a spinner.
- Apple returns the display name **only on first authorization**. Persist it then; never overwrite a stored name with a later empty value.
- `@privaterelay.appleid.com` addresses are valid — do not treat them as malformed or reject them in validation.
- Verify Hide My Email / Private Relay end-to-end on a real device.

---

## 1.5 — Support URL Must Actually Support

**What happened:** the Support URL pointed to an anchor (`/#faq`) that did not render a functional support section.

The URL must resolve to a page where a user can genuinely ask a question — a contact address, a form, or documented support instructions. Verify the deployed public page, including the anchor, before pasting it into App Store Connect. Deploy the site *before* submitting; a URL that will be live "soon" fails review.

---

## 3.1.2 — Terms of Use / EULA Link

Auto-renewable subscriptions require a **functional Terms of Use (EULA) link in the app's metadata**. Configure all three:

1. **App Information → EULA** — custom EULA URL or full text.
2. **App Description** — Terms + Privacy links in **every** locale.
3. **Subscription → Terms of Use URL** — per subscription in the group.

```bash
curl -sS -o /dev/null -w "terms: %{http_code}\n"   -L https://example.com/terms
curl -sS -o /dev/null -w "privacy: %{http_code}\n" -L https://example.com/privacy
# both must be 200
```

**Latent risk:** 3.1.2 also expects the user to reach Terms/Privacy **inside the app** before subscribing. Metadata links satisfy the metadata rejection; a Settings → Terms/Privacy screen with `Linking.openURL` closes the in-app gap before it becomes the next rejection.

---

## Build, Version, and Submission Pipeline

**Four distinct states, routinely conflated.** "EAS build finished" ≠ "submit processed" ≠ "build attached to the App Store version" ≠ "Update Review submitted". Verify each one independently; a green EAS status proves only the first.

**Build numbers are monotonic and single-use.** Reusing one fails upload with `bundle version must be higher than previously uploaded version`. Confirm the last accepted build via the App Store Connect API before submitting:

```bash
curl -s -H "Authorization: Bearer $ASC_JWT" \
  "https://api.appstoreconnect.apple.com/v1/builds?filter[app]=$APP_ID&sort=-uploadedDate&limit=5" \
  | jq '.data[] | {version: .attributes.version, state: .attributes.processingState}'
```

`package.json` version is the marketing version; the build number is the Apple-facing monotonic counter. With EAS `appVersionSource: remote` + `autoIncrement: true`, the **remote counter is the authority** — not any local file.

**Lockfile must be in sync, generated on the CI Node major.** EAS runs `npm ci`, which fails hard on any `package.json` / `package-lock.json` drift. Regenerate the lock with the same Node major the build profile pins, and commit both files together, before the cloud build.

**Verify the reviewed build actually contains the fix.** One rejection repeated purely because the reviewed build predated the fix commit. Before responding to a reviewer, confirm the fix commit is an ancestor of the submitted build's revision — a fix on `main` proves nothing about the binary Apple tested.

**Stop before `Update Review`.** Submitting is outward-facing and irreversible in effect. Get explicit confirmation from the account owner. Same for replying to the reviewer and releasing.

**A rejected submission can be withdrawn to unblock metadata edits.** IAP localization `PATCH` calls returned `409 UNMODIFIABLE` while the version sat in `WAITING_FOR_REVIEW`. Using "Remove from Review" in App Store Connect moved it to `DEVELOPER_REJECTED` → `PREPARE_FOR_SUBMISSION`, which unblocked editing **without destroying** the attached build, screenshots, or linked IAPs.

---

## iPad Is the Review Device

Every rejection in this timeline was found on an **iPad Air 11-inch (M3)**. Reviewers commonly use iPad for universal apps, and several bugs reproduced **only** there:

- Nested confirmation sheets racing (different animation timing / layout).
- The auth null-flash surfacing under release-build event batching.

**Gate:** run the full smoke test on a physical iPad in a release/TestFlight build before every submission — login (each provider), session persistence across cold start, purchase, and every Settings action. iPhone-only testing is not coverage.

---

## App Store Connect API — What It Can and Cannot Do

| Action | API? | Note |
|---|---|---|
| Read submission state, builds, IAPs, age rating | Yes | Read-only queries are safe to automate |
| Age Rating declaration | `PATCH /v1/ageRatingDeclarations/{id}` | Confirm with the owner first |
| IAP / subscription display name and description | `PATCH /v1/inAppPurchaseLocalizations/{id}` | 30 / 45 char limits |
| Delete a promo image | `DELETE /v1/promotedPurchaseImages/{id}` | Simpler than authoring two unique images |
| Upload a promo image | Three-step (reserve → upload → commit) | Painful; the App Store Connect UI is faster |
| Upload App Store screenshots | Technically yes | Recommended: do it manually |
| **Create sandbox testers** | **No** | `/v1/sandboxTesters` returns `404 PATH_ERROR`; UI only |
| Submit for review | Yes | **Do not run without explicit owner confirmation** |

**Credential hygiene:** the `.p8` private key, issuer ID, and key ID live outside the repo (e.g. `~/.config/asc/`), are `.gitignore`d (`*.p8`, `AuthKey_*.p8`, `credentials.env`), and JWTs (20-minute lifetime) are never logged in plaintext or committed. Use the minimum API key role for the task. On leak: revoke in App Store Connect, recreate, rotate.

---

## Pre-Submission Gate Script

Run all of these green before building the submission candidate.

```bash
# Dead interactive elements (2.1(a))
rg -n "TouchableOpacity|Pressable" src --glob '*.tsx' -A6 \
  | rg -B6 "accessibilityRole" | rg -v "onPress"

# Pre-permission button copy (5.1.1(iv))
rg -n "Grant Permission|Conceder Permissão|Otorgar Permiso" src/

# Native alerts instead of in-app confirmation UI (review-flow reliability)
rg -n "Alert\.(alert|prompt)" src/

# Terms / privacy reachable
curl -sS -o /dev/null -w "terms: %{http_code}\n"   -L "$TERMS_URL"
curl -sS -o /dev/null -w "privacy: %{http_code}\n" -L "$PRIVACY_URL"
curl -sS -o /dev/null -w "support: %{http_code}\n" -L "$SUPPORT_URL"

# Build hygiene
npm run validate:lockfile     # package.json / package-lock.json in sync on the CI Node major
tsc --noEmit                  # zero errors
npx vitest run                # suite green
```

**Manual gates that no script covers:**

- [ ] Physical iPad, release/TestFlight build: login with **every** provider, session survives cold start
- [ ] Physical iPad sandbox: monthly **and** annual purchase each unlock premium **without restart**
- [ ] Paid Applications Agreement is `Active`
- [ ] Every Settings action does something visible (rate, delete account, logout, support)
- [ ] Billed amount is the largest element in each plan card
- [ ] IAP display names and descriptions unique per product **per locale**
- [ ] Promo images deleted or visually distinct per product
- [ ] Age Rating claims only features a reviewer can find and operate
- [ ] Screenshots captured from the candidate build, audited slot-by-slot in **View All Sizes in Media Manager**, all locales
- [ ] Build number is higher than the last uploaded build (verified via API)
- [ ] The fix commit is an ancestor of the submitted build's revision
- [ ] Reviewer response drafted; **stop and get owner confirmation before `Update Review`**
