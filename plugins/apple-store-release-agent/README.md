# apple-store-release-agent

> AI release agent for the Apple App Store. Prepares, audits, and reports — **never submits**. Emits a GO / GO_WITH_WARNINGS / NO_GO decision with full risk, privacy, and IAP reports.

## What it does

Takes a React Native / Expo iOS app from "code looks done" to "ready for a low-rejection App Store submission" by:

- Auditing the Expo/EAS iOS build config (bundleId, version, profiles, mock flags).
- Scanning App Store metadata for high-rejection-risk wording (gambling, income-guarantee).
- Validating RevenueCat / IAP readiness (products, entitlements, restore, paywall fallback).
- Mapping detected SDKs (Firebase, RC, notifications, etc.) to suggested App Privacy labels.
- Checking i18n parity (PT / EN / ES) and flagging hardcoded strings.
- Flagging native `Alert.alert` usages that hurt the review UX.
- Generating review notes (demo account, IAP sandbox, account deletion) and store descriptions.
- Producing a TestFlight smoke checklist.
- Emitting a defensible **GO / GO_WITH_WARNINGS / NO_GO** decision.

Generic core with **presets** for Expo/RN, Firebase, RevenueCat/IAP, virtual currency, i18n, App Privacy, and TestFlight.

## Guardrails

- Never submits to App Review, never pays the Apple Developer Program, never publishes.
- Never alters IAP pricing or App Privacy labels without explicit human approval + diff.
- Never commits, logs, or prints secrets.
- Never treats virtual currency / rewards as gambling; never uses gambling or income-guarantee wording.

## Structure

```
plugins/apple-store-release-agent/
├── plugin.json
├── SKILL.md
├── README.md
├── checklists/
│   ├── apple-review.md
│   ├── privacy.md
│   ├── revenuecat-iap.md
│   ├── testflight-smoke.md
│   └── expo-eas-submit.md
├── templates/
│   ├── review-notes.md
│   ├── app-store-description-pt-BR.md
│   ├── app-store-description-en-US.md
│   ├── app-store-description-es-ES.md
│   └── release-report.md
└── scripts/
    ├── validate-ios-release.mjs
    ├── validate-app-store-metadata.mjs
    ├── validate-i18n-parity.mjs
    ├── validate-no-native-alerts.mjs
    ├── validate-revenuecat-iap.mjs
    ├── validate-privacy-readiness.mjs
    ├── validate-static-native-imports.mjs
    └── validate-missing-handlers.mjs
```

## Usage

In Claude Code (once the plugin is installed):

```
Use apple-store-release-agent para auditar meu app iOS antes da App Store.
Gere um GO/NO-GO report para submissão Apple.
Valide RevenueCat e App Privacy antes do review.
Crie review notes para o App Store Connect.
```

Or run a validator directly (Node.js ≥ 18, zero deps):

```bash
node scripts/validate-ios-release.mjs --project . --strict --json
node scripts/validate-revenuecat-iap.mjs --project . --strict --json
node scripts/validate-privacy-readiness.mjs --project . --strict --json
node scripts/validate-static-native-imports.mjs --project . --strict --json
node scripts/validate-missing-handlers.mjs --project . --strict --json
```

Flags accepted by all scripts: `--project <path>` (default cwd), `--output <path>` (write report), `--strict`, `--json`.

## Outputs (on a full run)

- `IOS_RELEASE_REPORT.md`
- `APPLE_REVIEW_RISK_REPORT.md`
- `PRIVACY_READINESS_REPORT.md`
- `REVENUECAT_IAP_REPORT.md`
- `TESTFLIGHT_SMOKE_CHECKLIST.md`
- `APP_STORE_REVIEW_NOTES.md`
- **Decision:** `GO` / `GO_WITH_WARNINGS` / `NO_GO`

## Limitations

Static analysis only (filesystem + regex). Does not run the app, hit live App Store Connect, or verify a real sandbox purchase. App Privacy suggestions are heuristic and require human confirmation. Requires Node.js ≥ 18.

## License

MIT — Anderson Lima.
