---
name: app-store-review
description: "Prepare for Apple App Store review and prevent rejections. Covers generic App Review guidelines, PrivacyInfo.xcprivacy and required-reason APIs, ATT, EU DMA, HIG, metadata, screenshots, entitlements, StoreKit/IAP, widgets, Live Activities, and submission workflow. Includes React Native, Expo, EAS, and RevenueCat field patterns: dead buttons without onPress, auth listener null-flash login loops, entitlement locked after sandbox purchase, subscription price hierarchy, duplicate IAP metadata, pre-permission button copy, screenshot slot audits, build number and lockfile pipeline gates, and App Store Connect API automation limits. Use when preparing for submission, responding to an App Review rejection, fixing rejection reasons, auditing privacy/metadata/IAP, implementing ATT, or debugging why premium stays locked after purchase."
---

# App Store Review Preparation

Guidance for catching App Store rejection risks before submission. Apple's May 2026 fraud-prevention update says App Review evaluated more than 9.1 million submissions in 2025 and rejected more than 2 million, so treat rejection prevention as a normal release-readiness step and re-check official Apple sources before quoting annual statistics.

## Contents

- [Overview](#overview)
- [Top Rejection Reasons and How to Avoid Them](#top-rejection-reasons-and-how-to-avoid-them)
- [Field-Tested Rejection Patterns (React Native / Expo / EAS)](#field-tested-rejection-patterns-react-native--expo--eas)
- [PrivacyInfo.xcprivacy -- Privacy Manifest Requirements](#privacyinfoxcprivacy-privacy-manifest-requirements)
- [Data Use, Sharing, and Privacy Policy (Guideline 5.1.2)](#data-use-sharing-and-privacy-policy-guideline-512)
- [In-App Purchase and StoreKit Rules (Guideline 3.1.1)](#in-app-purchase-and-storekit-rules-guideline-311)
- [HIG Compliance Checklist](#hig-compliance-checklist)
- [App Tracking Transparency (ATT)](#app-tracking-transparency-att)
- [EU Digital Markets Act (DMA) Considerations](#eu-digital-markets-act-dma-considerations)
- [Entitlements and Capabilities](#entitlements-and-capabilities)
- [Submission Workflow](#submission-workflow)
- [Metadata Best Practices](#metadata-best-practices)
- [Appeal Process](#appeal-process)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Overview

Use this SKILL.md for quick guidance on common rejection reasons and key policies. Use the references for detailed checklists and privacy manifest specifics.

For prompts about keywords, screenshot captions, product-page metadata, or metadata rejection risk, answer from a compliance angle and explicitly defer keyword research, ranking strategy, conversion optimization, screenshot ordering, and A/B testing to `app-store-optimization`. Keep App Review metadata guidance limited to accuracy, field limits, misleading-content risk, and screenshot compliance. Always surface the rejection-prone format checks: app name 30 characters, subtitle 30 characters, keyword field 100 characters with comma-separated keywords and no spaces after commas, screenshots showing actual app UI, 6.9-inch iPhone screenshots as the primary current iPhone set, and 13-inch iPad screenshots when the app runs on iPad.

For full submission readiness audits, separate blocking upload/review issues from ordinary cleanup. Treat Xcode 26+ with the relevant platform SDK 26+ as a blocking App Store Connect upload requirement after April 28, 2026. Cross-check privacy manifests, App Store privacy nutrition labels, privacy policy, ATT state, runtime network behavior, and SDK behavior against each other; the declarations and observed behavior must align.

### Blocking Submission Checks

Escalate these as blockers before ordinary cleanup:

- Uploads after April 28, 2026 that are not built with Xcode 26+ and the relevant platform SDK 26+
- Privacy manifest, privacy label, privacy policy, ATT state, SDK transmissions, or audited runtime network behavior mismatches
- Digital goods and subscriptions that bypass StoreKit IAP, or external purchase paths/links/buttons/CTAs for digital goods, unless current rules or approved entitlements allow them
- Missing required screenshot sets: 6.9-inch iPhone screenshots, and 13-inch iPad screenshots when the app runs on iPad
- Login-gated or non-obvious features without demo credentials, demo mode, and clear App Review notes

## Top Rejection Reasons and How to Avoid Them

### Guideline 2.1 -- App Completeness

The app must be fully functional when reviewed. Apple rejects for:

- Placeholder content, lorem ipsum, or test data visible anywhere
- Broken links or empty screens
- Features behind logins without demo credentials provided in App Review notes
- Features that require hardware Apple does not have access to

**Prevention:**
- Provide demo account credentials in the App Review Information notes field in App Store Connect
- Walk through every screen and verify real content is present
- Test all flows end-to-end, including edge cases like empty states and error conditions

### Guideline 2.3 -- Accurate Metadata

- App name must match what the app actually does
- Screenshots must show the actual app UI, not marketing renders or mockups
- Description must not contain prices (they vary by region)
- No references to other platforms ("Also available on Android")
- Keywords must be relevant -- no competitor names or unrelated terms
- Category must match the app's primary function

### Guideline 4.2 -- Minimum Functionality

Apple rejects apps that are too simple or are just websites in a wrapper:

- WKWebView-only apps are rejected unless they add meaningful native functionality
- Single-feature apps may be rejected if the feature is better suited as part of another app
- Apps that duplicate built-in iOS functionality without significant improvement are rejected

### Guideline 2.5.1 -- Software Requirements

- Must use public APIs only -- private API usage is an instant rejection
- As of April 28, 2026, uploads to App Store Connect must be built with Xcode 26 or later using the relevant platform SDK 26 or later
- Deployment target support is a product and compatibility decision, not an App Review rule
- Must not download or execute code that introduces or changes app features or functionality after review, except where Apple guidelines and agreements explicitly allow interpreted code

## Field-Tested Rejection Patterns (React Native / Expo / EAS)

These are rejections that actually occurred across five consecutive review cycles on a production RN + Expo + EAS + RevenueCat app, with confirmed root causes. The generic guidelines above tell you the rule; these tell you how cross-platform stacks break it.

**See:** [references/field-lessons-rn-expo.md](references/field-lessons-rn-expo.md) for full root-cause analysis, code diffs, and the complete gate script.

### The meta-lessons

1. **Expect multiple rounds.** Each fix surfaced the next layer. Front-load the entire checklist rather than fixing only the cited findings.
2. **The same guideline recurs for different root causes.** 2.1(a) was an auth bug in one cycle and a missing `onPress` in another. Re-diagnose from scratch; never assume a regression.
3. **iPad is the review device.** Every finding in that timeline came from an iPad Air 11-inch. Several bugs reproduced *only* there (sheet animation races, release-build event batching). iPhone-only testing is not coverage.
4. **Release builds behave differently.** The auth bug was invisible in dev builds; JS bridge batching changed native event ordering. Smoke-test a release/TestFlight build.
5. **Verify the reviewed binary contains the fix.** One rejection repeated purely because the reviewed build predated the fix commit. A fix on `main` proves nothing about the binary Apple tested.
6. **A citation does not mean the fix is in the codebase.** One 2.3.10 rejection was an App Store Connect IAP localization field, not app code — the repo was already clean with a passing regression spec. Audit App Store Connect metadata directly before assuming the fix is a code change.
7. **One static regression test per closed finding.** A finding without a test that would have caught it comes back — either as a regression, or as the same bug class on a screen nobody thought to re-check (an unlinked-but-reachable route repeated a sheet-race bug for exactly this reason).

### High-frequency root causes

| Guideline | Failure | Root cause | Gate |
|---|---|---|---|
| 2.1 | Crash on launch, no JS stack trace | recently added native module imported at top-of-file; `requireNativeModule` runs at import time, before the root component mounts | cold-launch 5× in a **Release** build; move the import behind a function-scoped dynamic import |
| 2.1(a) | Button does nothing | `accessibilityRole="button"` with no `onPress` | grep for interactive elements missing a handler |
| 2.1(a) | "Rate app" inert | native review prompt is a silent no-op in review builds and rate-limited | always fall back to the App Store product page URL |
| 2.1(a) | Confirmation never appears | nested confirmation sheets race the first sheet's dismissal on iPad | one confirmation at a time |
| 2.1(a) | Login bounces back to login | auth SDK emits a transient `null` that lands after the sign-in completes | settle/revalidate before clearing a session |
| 2.1(b) | Premium locked after purchase | entitlement read only from a backend webhook that has not processed yet | invalidate cache, retry with backoff, fall back to local `customerInfo` |
| 3.1.2(c) | Price hierarchy | calculated per-month figure rendered at the same weight as the billed amount | billed amount is the largest element in the card |
| 2.3.2 | Duplicate IAP metadata | display name/description identical across products, per locale | diff every product × locale pair |
| 2.3.6 | Age rating overclaims | declared a control the reviewer could not find | set to `None` unless the feature is front-and-center |
| 2.3.3 / 2.3.10 | Screenshots | marketing mockups, non-iOS status bars, stale slots | capture from the candidate build; audit via View All Sizes in Media Manager |
| 2.3.10 | Cites a competing platform, code is clean | the flagged text is an App Store Connect **IAP localization** field, not app code | audit ASC IAP localizations per product/locale before touching the repo |
| 5.1.1(iv) | Permission copy | pre-permission button said "Grant Permission" | use "Continue" / "Next"; change `accessibilityLabel` too |
| 5.1.1(ix) | Account type | individual enrollment for a regulated-category app | not fixable in code — resolve enrollment first |
| 4.8 | Login services | third-party login without an equivalent privacy-preserving option | add Sign in with Apple |

### Pipeline gates that block submission regardless of code

- **Paid Applications Agreement must be `Active`** — pending banking or tax means no purchase works, including the reviewer's.
- **Build numbers are monotonic and single-use** — verify the last accepted build via the App Store Connect API before submitting.
- **`npm ci` fails on any lockfile drift** — regenerate the lock on the CI Node major and commit both files together.
- **Five distinct states, routinely conflated:** cloud build finished ≠ submit processed ≠ TestFlight Ready to Submit ≠ build attached to the version ≠ Update Review submitted.
- **Sandbox testers cannot be created via the API** (`404 PATH_ERROR`) — App Store Connect UI only.
- **Stop before `Update Review`** and get explicit owner confirmation. Same for replying to the reviewer and releasing.

## PrivacyInfo.xcprivacy -- Privacy Manifest Requirements

A privacy manifest is required when your app code, an executable, a dynamic library, or a third-party SDK uses Apple's required-reason API categories or declares collected data/tracking behavior.

**See:** [references/privacy-manifest.md](references/privacy-manifest.md) for the full structure, reason codes, and checklists.

### Summary

- Required-reason API categories are file timestamps, system boot time, disk space, active keyboards, and UserDefaults; each requires an approved reason code when used.
- Before final submission, re-check Apple's current required-reason API documentation and do not choose broad, convenient, or invented reason codes.
- Required-reason API declarations belong in the bundle that contains the code using the API; every app target, executable, dynamic library, framework, or SDK bundle containing manifest-relevant code needs the matching manifest declarations.
- Each SDK, executable, or dynamic library that collects data, uses required-reason APIs, enables data collection/tracking, or contacts tracking domains needs manifest attention in the bundle containing that code; SDK code cannot rely on the host app's manifest to report the SDK's own usage.
- Manifest declarations must match App Store privacy nutrition labels, SDK behavior, and the app's presented functionality.

## Data Use, Sharing, and Privacy Policy (Guideline 5.1.2)

- A privacy policy URL must be set in App Store Connect AND accessible within the app
- The privacy policy must accurately describe what data you collect, how you use it, and who you share it with
- App Store privacy nutrition labels must match your actual data collection practices
- Privacy labels, privacy manifests, SDK disclosures, and runtime behavior should tell the same story

## In-App Purchase and StoreKit Rules (Guideline 3.1.1)

IAP rules are strict and heavily enforced.

### What Generally Requires Apple IAP

Digital content, features, subscriptions, and services unlocked in the app generally must use Apple's In-App Purchase system unless a specific App Review guideline exception, regional rule, or approved entitlement applies. Remove external purchase paths unless the current rules or an approved entitlement allow them:

- Premium features or content unlocks
- Subscriptions to app functionality
- Virtual currency, coins, gems
- Ad removal
- Digital tips or donations

### What Does NOT Require IAP

- Physical products (e-commerce)
- Ride-sharing, food delivery, real-world services
- One-to-one services (tutoring, consulting booked through the app)
- Enterprise/B2B apps distributed through Apple Business Manager

### Subscription Display Requirements

- Price, duration, and auto-renewal terms must be clearly displayed before purchase
- Free trials must clearly show trial duration, post-trial price, billing frequency, auto-renewal, and cancellation terms before purchase
- Remove external purchase links, buttons, calls to action, or purchase paths for digital goods unless the current storefront rules or an approved entitlement explicitly allow them
- "Reader" apps (Netflix, Spotify) may link to external sign-up but cannot offer IAP bypass

### StoreKit Implementation Checklist

- Consumables, non-consumables, and subscriptions must be correctly categorized in App Store Connect
- Restore purchases functionality must be present and working
- Transaction verification should use StoreKit 2 `Transaction.currentEntitlements` or server-side validation
- Handle interrupted purchases, deferred transactions, and ask-to-buy gracefully

## HIG Compliance Checklist

See [references/review-checklists.md](references/review-checklists.md) for the full HIG checklist (navigation, modals, widgets, system feature support, launch screen, empty states). This section stays intentionally brief to keep SKILL.md concise.

## App Tracking Transparency (ATT)

### When ATT Is Required

If your app tracks users across other companies' apps or websites, you must:

1. Request permission via `ATTrackingManager.requestTrackingAuthorization` before any cross-app or cross-website tracking occurs, including tracking-capable SDK behavior
2. Respect the user's choice -- disable cross-app and cross-website tracking if the user denies permission
3. Not gate app functionality behind tracking consent ("Accept tracking or you cannot use this app" is rejected)
4. Provide a clear purpose string in `NSUserTrackingUsageDescription` explaining what tracking is used for

### When ATT Is NOT Required

If you do not track users across apps or websites, do not show the ATT prompt. Apple rejects unnecessary ATT prompts.

### ATT Implementation

```swift
import AppTrackingTransparency

@MainActor
func requestTrackingPermission() async {
    let status = await ATTrackingManager.requestTrackingAuthorization()
    switch status {
    case .authorized:
        // Enable tracking, initialize ad SDKs with tracking
        break
    case .denied, .restricted:
        // Use non-personalized ads and disable cross-app/cross-website tracking
        break
    case .notDetermined:
        // Should not happen after request, handle gracefully
        break
    @unknown default:
        break
    }
}
```

**Timing:** Request ATT permission after the app is active and the user has context for why tracking is being requested. Do not show the prompt immediately on first launch or stack it with another system permission prompt.

## EU Digital Markets Act (DMA) Considerations

For apps distributed in the EU, and for other region-specific distribution models as Apple updates them:

- Alternative browser engines are permitted on iOS in the EU
- Alternative app marketplaces exist -- apps may be distributed outside the App Store
- External payment links may be allowed under specific conditions, with Apple's commission structure adjusted
- Notarization is required even for sideloaded apps distributed outside the App Store
- Apps using alternative distribution must still meet Apple's notarization requirements for security

## Entitlements and Capabilities

Every entitlement must be justified. Apple reviews these closely:

| Entitlement | Apple Scrutiny |
|---|---|
| Camera | Must explain purpose in `NSCameraUsageDescription` |
| Location (Always) | Must have clear, user-visible reason for background location |
| Push Notifications | Must not be used for marketing without user opt-in |
| HealthKit | Must actually use health data in a meaningful way |
| Background Modes | Each mode (audio, location, VoIP, fetch) must be justified and actively used |
| App Groups | Must explain what shared data is needed |
| Associated Domains | Universal links must actually resolve and function |

### Usage Description Strings

Usage descriptions in Info.plist must be specific about what data is accessed and why:

```xml
// REJECTED -- too vague

// APPROVED -- specific purpose
"Your location is used to show nearby restaurants on the map."

// REJECTED -- too vague
"This app needs access to your camera."

// APPROVED -- specific purpose
"The camera is used to scan barcodes for price comparison."
```

Apple rejects vague usage descriptions. Always state what the data is used for in user-facing terms.

## Submission Workflow

### Pre-Submission Steps

1. **Archive in Xcode.** Product > Archive (requires a Distribution signing identity). Verify the archive builds clean with zero warnings in Release configuration.
2. **Upload to App Store Connect.** Use the Organizer window (Distribute App > App Store Connect) or `xcodebuild -exportArchive`. Automated uploads via `altool` or Transporter also work.
3. **TestFlight internal testing.** The build is available to internal testers (your team) within minutes of processing. Walk through every screen and flow on at least two device sizes.
4. **TestFlight external testing.** External groups require Beta App Review before first external distribution. Use this to validate with real users before full submission.
5. **Submit for App Review.** In App Store Connect, select the build, fill in all metadata fields, attach screenshots, and click Submit for Review. Review timing varies; allow buffer for rejections, appeals, and metadata fixes.

### Expedited Review Requests

Apple grants expedited reviews for critical situations only:

- Critical bug fix affecting existing users
- Time-sensitive event (holiday launch, legal compliance deadline)
- Security vulnerability patch

Request via the Contact Us form in App Store Connect (App Review > Expedite Request). Provide a specific, factual justification. Do not request expedited review for initial launches or feature updates.

### Phased Release

After approval, you can enable phased release to gradually roll out the update:

| Day | Percentage of Users |
|-----|---------------------|
| 1   | 1%                  |
| 2   | 2%                  |
| 3   | 5%                  |
| 4   | 10%                 |
| 5   | 20%                 |
| 6   | 50%                 |
| 7   | 100%                |

Users who manually check for updates in the App Store will receive the update immediately regardless of phased release stage. You can pause, resume, or complete the rollout at any time from App Store Connect.

## Metadata Best Practices

### App Name and Subtitle

- **30 characters max** for the app name. Keep it memorable and unique.
- **30 characters max** for the subtitle. Use it for a concise value proposition.
- No generic terms that describe a category ("Photo Editor" alone is likely rejected).
- No competitor names or trademarked terms you do not own.
- No pricing information in the name or subtitle.
- Name must be unique on the App Store -- Apple rejects duplicates.

### Screenshot Requirements

- Provide 1-10 screenshots per required platform and localization.
- For iPhone, use the current App Store Connect screenshot specifications. As of May 2026, 6.9-inch iPhone screenshots are the primary accepted iPhone set; 6.5-inch screenshots are required only when 6.9-inch screenshots are not provided, and smaller iPhone displays can use scaled screenshots from larger sets.
- For iPad apps, 13-inch iPad screenshots are required; smaller iPad displays can use scaled screenshots from larger sets.
- Screenshots must show the **actual app UI** -- no misleading content, no features that do not exist.
- Text overlays and marketing frames are allowed but must not obscure or misrepresent the actual interface.
- Up to 10 screenshots per localization.
- Screenshots for different localizations should show localized UI.

### Keyword Field Compliance

- 100-character limit, comma-separated, no spaces after commas.
- Do not duplicate words already in your app name or subtitle (Apple indexes those automatically).
- Use singular or plural, not both ("game" not "game,games").
- No competitor names, trademarked terms, or irrelevant words.

### App Preview Videos

- **30 seconds max** per preview video.
- Up to 3 preview videos per localization.
- Must show the actual app running on device -- no pre-rendered animations of features that look different in practice.
- App audio is captured; narration and background music are optional.
- Avoid any framing, hand footage, or visual treatment that makes the preview misleading about the actual app experience.
- First frame is used as the poster frame on the product page (choose carefully).

## Appeal Process

### Replying to Rejections

All rejections appear in the **Resolution Center** in App Store Connect. To respond:

1. Read the rejection message carefully -- it cites the specific guideline violated.
2. Reply directly in the Resolution Center thread with a clear, factual explanation.
3. If you made a fix, describe exactly what changed and resubmit the binary.
4. If you believe the rejection is incorrect, explain why your app complies, with references to the specific guideline text.

**Tone matters.** Be professional, specific, and concise. Provide demo credentials, screenshots, or screen recordings that demonstrate compliance. Avoid emotional language or threats.

There is no direct email or executive contact channel — see [references/field-lessons-rn-expo.md#apple-contact-channels](references/field-lessons-rn-expo.md#apple-contact-channels) for the three official paths (Resolution Center, App Review Appeal, Developer Support) in escalation order.

### Escalation to App Review Board

If the Resolution Center exchange does not resolve the issue:

1. Request an appeal to the **App Review Board** via the Resolution Center or the App Store Contact form (App Review > Appeal).
2. The Board is a separate team from the original reviewer. Provide all context -- they review the full history.
3. Board decisions are final for that submission, but you can always modify the app and resubmit.

### Common Successful Appeal Strategies

- **Provide a video walkthrough** showing the feature the reviewer could not find or access.
- **Cite the specific guideline** and explain how the app satisfies each requirement.
- **Include demo credentials** if the reviewer could not log in (the most common 2.1 rejection cause).
- **Reference precedent** -- if similar apps exist on the App Store with the same pattern, note them (respectfully).
- **Offer a compromise** -- if Apple objects to a specific implementation, propose an alternative that satisfies both sides.

## Common Mistakes

1. **Missing demo credentials.** Provide App Review login credentials in App Store Connect notes. Most Guideline 2.1 rejections are from reviewers unable to test behind a login.
2. **Privacy manifest mismatch.** Declared data collection in PrivacyInfo.xcprivacy must match App Store privacy nutrition labels, SDK behavior, and app functionality.
3. **Unnecessary ATT prompt.** Do not show the App Tracking Transparency prompt unless you actually track users across apps or websites. Apple rejects unnecessary prompts.
4. **Vague usage descriptions.** "This app needs your location" is rejected. State the specific feature that uses the data.
5. **Unapproved external purchase paths.** External payment links for digital goods are region- and entitlement-sensitive; do not add them without checking current Guideline 3.1.1(a) rules.
6. **Treating code quality as review compliance.** Swift 6 concurrency annotations and StoreKit transaction handling matter, but they do not replace privacy, payment, metadata, and entitlement compliance checks.

## Review Checklist

Quick-check before every submission (full version in [references/review-checklists.md](references/review-checklists.md)):

- [ ] No placeholder/test content; all features functional; demo credentials provided
- [ ] App name matches functionality; screenshots are real; no prices in description; 6.9-inch iPhone and 13-inch iPad screenshots supplied when applicable
- [ ] PrivacyInfo.xcprivacy present when required-reason APIs, tracking, collected data declarations, or SDK tracking domains apply; nutrition labels match reality
- [ ] Privacy policy URL set and accessible in-app
- [ ] Digital content uses IAP; subscription terms visible; restore purchases works; external purchase links/buttons/CTAs removed unless current rules or approved entitlements allow them
- [ ] Dark Mode and Dynamic Type supported; standard navigation patterns
- [ ] Built with Xcode 26+ and platform SDK 26+ for uploads after April 28, 2026; no private APIs; entitlements justified
- [ ] ATT prompt only if cross-app or cross-website tracking occurs
- [ ] Every interactive element has a handler; smoke-tested on a physical iPad in a release build
- [ ] Purchase in sandbox unlocks the entitlement without an app restart; Paid Applications Agreement is `Active`
- [ ] Build number higher than the last uploaded build; the fix commit is an ancestor of the submitted build's revision

## References

- Review checklists: [references/review-checklists.md](references/review-checklists.md)
- Privacy manifest guide: [references/privacy-manifest.md](references/privacy-manifest.md)
- Field lessons (React Native / Expo / EAS / RevenueCat): [references/field-lessons-rn-expo.md](references/field-lessons-rn-expo.md)
- Apple App Review Guidelines: https://developer.apple.com/app-store/review/guidelines/
- Apple upcoming SDK requirements: https://developer.apple.com/news/upcoming-requirements/
- App Store Connect screenshot specifications: https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications/
- Sosumi required-reason API docs: https://sosumi.ai/documentation/bundleresources/describing-use-of-required-reason-api
