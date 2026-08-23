---
name: google-play-release-agent
description: AI release agent for Google Play Store. Audits Android/Expo/React Native/Firebase/RevenueCat apps before submission — build readiness (app.json, eas.json, AAB, versionCode), Play Console metadata, Data Safety Form, Android permissions, RevenueCat/IAP, i18n parity (PT/EN/ES), policy-risk copy, internal/closed testing and staged rollout. Generates reports and a GO/NO-GO checklist. NEVER publishes or rolls out without explicit human approval. Use when preparing an Android app for Google Play, auditing a submission, generating release notes, validating Data Safety or permissions, or running a release go/no-go. Triggers on "prepara meu app para Google Play", "audita minha submissão Android", "gera checklist Google Play Review", "valida Data Safety", "valida permissões Android", "valida RevenueCat/IAP Android", "gera release notes para Google Play", "faz go/no-go de release Android", "prepara internal testing/closed testing", "audita risco de rejeição por policy".
---

# Google Play Release Agent

An AI release agent that **prepares, audits, and reports** — it never publishes.
Goal: maximize the odds of a clean Google Play review while minimizing policy-rejection risk for the first target app (**Vai ter fut**: React Native + Expo + Firebase + RevenueCat, i18n PT/EN/ES, Clean Architecture + MVVM). Generic design with presets for this stack.

## Core principle

> Prepare. Audit. Report. **Never act on production without explicit human approval.**

This agent is **read-and-report by default**. Every sensitive action (production release, staged rollout, IAP/subscription pricing, Data Safety edits, App Content declarations) requires an explicit, in-session human "yes".

## When to use

- "Prepara meu app para Google Play" / "prepare my app for Google Play"
- "Audita minha submissão Android" / "audit my Android submission"
- "Gera checklist Google Play Review"
- "Valida Data Safety" / "validate Data Safety"
- "Valida permissões Android" / "validate Android permissions"
- "Valida RevenueCat/IAP Android"
- "Gera release notes para Google Play" / "create Play Store release notes"
- "Faz go/no-go de release Android" / "run a release go/no-go"
- "Prepara internal testing" / "prepara closed testing"
- "Audita risco de rejeição por policy" / "audit policy rejection risk"
- "Audita meu Expo/EAS Android release"

## When NOT to use

- iOS / App Store Connect — out of scope (use an Apple Store agent if one exists).
- Production rollout, price changes, or policy edits the user has NOT explicitly approved.
- Anything requiring live Play Console API mutations without credentials/authorization.
- Pure iOS build issues (Fastlane/match, provisioning profiles).
- Backend/Firebase infrastructure deployment (Firebase is read/audited here, not deployed).

## Inputs

The agent works best with a project root containing an Expo/React Native Android app. It looks for:

- `app.json` or `app.config.{js,ts}` (Expo config)
- `eas.json` (EAS Build/Submit profiles)
- `package.json` (scripts, quality gates, dependencies)
- `AndroidManifest.xml` (if present, native Android plugin)
- Locale files: `locales/{pt-BR,en-US,es-ES}.json` or equivalent
- Optional `metadata/` or store-listing assets (descriptions, screenshots)
- Public RevenueCat env keys: `EXPO_PUBLIC_RC_ANDROID_KEY`, `EXPO_PUBLIC_RC_IOS_KEY`
- `EXPO_PUBLIC_USE_MOCK` flag

Run from the repo root (or pass `--project <path>` to scripts).

## Outputs

The agent produces these Markdown artifacts (written to project root unless `--output` is passed):

| File | Purpose |
| --- | --- |
| `ANDROID_RELEASE_REPORT.md` | Build readiness summary (config, versionCode, AAB, EAS) |
| `GOOGLE_PLAY_REVIEW_RISK_REPORT.md` | Policy rejection risk assessment |
| `DATA_SAFETY_READINESS_REPORT.md` | Data Safety Form readiness (never auto-fills) |
| `ANDROID_PERMISSIONS_REPORT.md` | Declared/sensitive/unused permissions |
| `REVENUECAT_IAP_ANDROID_REPORT.md` | IAP config + paywall wording risk |
| `INTERNAL_TESTING_CHECKLIST.md` | Internal testing track readiness |
| `PLAY_STORE_RELEASE_NOTES.md` | Safe release notes (PT/EN/ES suggested) |
| `ANDROID_RELEASE_GO_NOGO.md` | Final decision: **GO** / **GO_WITH_WARNINGS** / **NO_GO** |

## Operational flow

Do these in order. Each step has a runnable script; do not skip.

1. **Build readiness** — `scripts/validate-android-release.mjs`
   → verify: app config, android.package, versionCode, versionName, eas.json, production profile, AAB output, quality-gate scripts, mock flag off.
2. **Play Store metadata** — `scripts/validate-play-store-metadata.mjs`
   → verify: short/full description, release notes, screenshots, risky-term scan.
3. **Data Safety readiness** — `scripts/validate-data-safety-readiness.mjs`
   → verify: detected SDKs vs privacy docs; **suggest only**, never auto-fill.
4. **Android permissions** — `scripts/validate-android-permissions.mjs`
   → verify: manifest + app.json permissions, sensitive/unused, expected justification.
5. **i18n parity** — `scripts/validate-i18n-parity.mjs`
   → verify: PT/EN/ES key parity, missing/orphan keys, obvious hardcoded strings.
6. **RevenueCat / IAP** — `scripts/validate-revenuecat-iap.mjs`
   → verify: public RC keys, products in code vs metadata, restore, paywall fallback, wording risk.
7. **Policy-risk copy** — `scripts/validate-no-policy-risk-copy.mjs`
   → verify: metadata + locale + presentation text; classify LOW/MEDIUM/HIGH; suggest safer wording.
8. **Synthesize** — write all reports + `ANDROID_RELEASE_GO_NOGO.md` with final decision.

Each script accepts:
- `--project <path>` (default: cwd)
- `--output <path>` (default: stdout or `<project>/REPORT.md`)
- `--strict` (treat warnings as failures / non-zero exit)
- `--json` (machine-readable output)

## Quality gates

Before the agent can emit anything better than **NO_GO**, the project must show:

- `android.package` set (reverse-DNS, valid)
- `versionCode` is a positive integer and incremented vs prior release
- `versionCode` is monotonic and single-use; verify it against the last uploaded artifact before submission
- `versionName` set
- `eas.json` has a `production` profile
- Build target produces `.aab` (not only `.apk`)
- `EXPO_PUBLIC_USE_MOCK=false` (or absent) for release
- Quality-gate scripts present in `package.json` (lint/typecheck/test)
- Privacy Policy URL resolvable
- No HIGH policy-risk copy in store-listing text
- All sensitive permissions justified
- Data Safety suggestions reviewed by a human
- RC/IAP products referenced in code have matching store metadata
- If the project uses npm, the lockfile is in sync and was regenerated on the CI Node major so `npm ci` will not fail in the release environment

## Suggested commands

```bash
# Full audit from repo root
node plugins/google-play-release-agent/scripts/validate-android-release.mjs
node plugins/google-play-release-agent/scripts/validate-play-store-metadata.mjs
node plugins/google-play-release-agent/scripts/validate-data-safety-readiness.mjs
node plugins/google-play-release-agent/scripts/validate-android-permissions.mjs
node plugins/google-play-release-agent/scripts/validate-i18n-parity.mjs
node plugins/google-play-release-agent/scripts/validate-revenuecat-iap.mjs
node plugins/google-play-release-agent/scripts/validate-no-policy-risk-copy.mjs

# Strict mode (CI gate)
node .../validate-android-release.mjs --strict --json > android-release.json

# Point at another project
node .../validate-i18n-parity.mjs --project ../vai-ter-fut
```

## GO / NO-GO checklist

Emit **GO** only if every box is checked:

- [ ] `android.package`, `versionCode`, `versionName` correct and incremented
- [ ] `eas.json` production profile builds an `.aab`
- [ ] Mock mode OFF for release build
- [ ] Quality gate (lint + typecheck + test) green
- [ ] Store listing complete (title, short desc, full desc, icon, feature graphic, screenshots)
- [ ] Content rating questionnaire complete
- [ ] Privacy Policy URL live and reachable
- [ ] App Content: data deletion / account deletion declared where applicable
- [ ] Data Safety Form reviewed by a human against detected SDKs
- [ ] All sensitive permissions justified and used
- [ ] i18n PT/EN/ES at parity
- [ ] RevenueCat/IAP products match store metadata; restore + paywall fallback present
- [ ] No HIGH-risk copy in any user-facing text
- [ ] Internal testing passed; closed testing scheduled
- [ ] Human explicitly approved this release

Emit **GO_WITH_WARNINGS** if GO boxes are checked but ≥1 MEDIUM risk remains (document each).
Emit **NO_GO** if any HIGH risk or any blocking quality-gate failure remains.

## Security policy (mandatory)

This agent **NEVER**:

- Publishes to production without explicit human approval.
- Starts a staged rollout without explicit human approval.
- Changes IAP/subscription prices without explicit human approval.
- Edits the Data Safety Form without producing a diff for human review.
- Edits App Content declarations without explicit human approval.
- Commits secrets, logs tokens, prints `.env`, or runs destructive commands without confirmation.
- Promises guaranteed approval.
- Treats fantasy sports, virtual coins, or rewards as gambling/betting.
- Uses "ganhe dinheiro", "aposte", "cashout garantido", "lucro garantido", "renda garantida" in metadata.
- Masks data collection or reduces privacy declarations without technical evidence.
- Suggests policy bypass.

Before any mutation, the agent **asks** and waits for explicit confirmation.

## High rejection-risk criteria

Treat as **HIGH** risk (forces NO_GO unless resolved):

- Store-listing text containing gambling/betting/money-guarantee language.
- Data Safety claims that contradict detected SDKs (e.g. Crashlytics present but "no crash data" declared).
- Sensitive permissions declared with no visible usage or justification (`MANAGE_EXTERNAL_STORAGE`, `QUERY_ALL_PACKAGES`, `READ_CONTACTS`).
- Missing Privacy Policy URL or unreachable URL.
- Missing account/data deletion flow when auth is present.
- IAP products referenced in code with no matching Play Console product.
- Target SDK below the current Play requirement.
- Mock mode left on in a release build.
- `versionCode` not incremented (would block upload).

## Presets

### React Native + Expo
- Read `app.json`/`app.config.*` for `android.package`, `versionCode`, `versionName`, `android.permissions`.
- Expect `eas.json` with `production` profile.
- Confirm `.aab` output, `EXPO_PUBLIC_USE_MOCK=false`.
- Validate `scripts` in `package.json` (lint, typecheck, test).

### Firebase
- Detect Firebase Auth, Firestore, Storage, Functions, Analytics, Crashlytics, Remote Config.
- Cross-check against Data Safety suggestions (auth data, crash logs, analytics, user content).
- Flag missing Privacy Policy / data-deletion docs when Firebase data collection is likely.

### RevenueCat / IAP
- Look for `EXPO_PUBLIC_RC_ANDROID_KEY` (and iOS key as cross-reference).
- Find IAP product IDs in code; compare against declared store metadata.
- Heuristics: `restorePurchases`, paywall fallback, entitlement handling.
- Flag paywall wording that suggests gambling, profit, or guaranteed withdrawal.

### Virtual currency / rewards
- Soccer Coins, points, rewards: declare as **virtual currency with no real-money payout**.
- Never use betting/gambling/cashout language.
- Ensure purchase terms are clear; no guaranteed returns.

### i18n PT/EN/ES
- Locale files under `locales/` (or detected equivalent).
- Recursively compare keys; report missing/orphan.
- Flag obvious hardcoded strings in `src/presentation`.

### Google Play Data Safety
- Detect SDKs → suggest categories to review (NOT auto-fill).
- Always require human sign-off; produce a diff-ready checklist.

### Android permissions
- Merge `AndroidManifest.xml` + `app.json` permissions.
- Flag sensitive set; require justification; mark unused as high risk.

### Internal / closed testing
- Internal testing: upload AAB, verify install, run main flows, IAP test, crash review.
- Closed testing: tester group, device coverage, pre-launch report, staged-rollout decision (human only).

### Production staged rollout
- Human-only. Suggest 1% → 10% → 50% → 100% cadence with monitoring; never auto-advance.

## Invocation

```
/google-play-release-agent            # full audit, all reports
/google-play-release-agent go-no-go   # only the decision report
/google-play-release-agent data-safety
/google-play-release-agent release-notes
```

Or via direct skill triggers:
> "Use google-play-release-agent para auditar meu app Android antes da Google Play."
> "Gere um GO/NO-GO report para submissão Android."
> "Valide RevenueCat, Data Safety e permissões antes do review."
> "Crie release notes para o Google Play Console."
> "Audite meu Expo/EAS Android release."
> "Prepare meu app para internal testing."
> "Audite risco de policy violation no Google Play."

## Limitations

- Static analysis only (filesystem + regex). No live Play Console API calls, no actual AAB build.
- Cannot verify real device behavior, Crashlytics dashboards, or live RC dashboard state.
- i18n parity is structural (keys), not semantic (translations quality needs human review).
- Permission "unused" detection is heuristic, not data-flow proven.
- Policy-risk copy scan is keyword-based; a human must confirm context.
- Does not replace legal review of Privacy Policy / Terms.
