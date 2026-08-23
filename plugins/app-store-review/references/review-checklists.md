# App Store Review Checklists

## Contents
- App Review Information Checklist
- Privacy Manifest Checklist
- In-App Purchase Checklist
- Screenshot and App Preview Checklist
- HIG Compliance Checklist
- Pre-Submission Checklist
- Cross-Platform Stack Checklist (React Native / Expo / EAS / RevenueCat)

## App Review Information Checklist

Use this to avoid Guideline 2.1 rejections:

- [ ] Demo credentials provided in App Review Information notes (if login required)
- [ ] Demo mode available if credentials are impractical or account state is hard to reproduce
- [ ] Demo account works and has access to all features
- [ ] App Review notes explain login-gated, role-gated, region-gated, hardware-gated, or otherwise non-obvious features
- [ ] All screens have real content (no placeholders or Lorem Ipsum)
- [ ] No broken links or dead-end flows
- [ ] All hardware-required features have fallback or reviewer instructions

## Privacy Manifest Checklist

Verify PrivacyInfo.xcprivacy completeness:

- [ ] `PrivacyInfo.xcprivacy` exists where app code, SDK code, executables, or dynamic libraries need it
- [ ] All required-reason API categories in app and bundled SDK code are declared with approved reason codes
- [ ] `NSPrivacyTracking` is true only if tracking occurs
- [ ] Third-party SDK manifests present and up to date when SDKs collect data, use required-reason APIs, enable data collection, or contact tracking domains
- [ ] Privacy nutrition labels match actual data collection
- [ ] Audit runtime network traffic and SDK transmissions; observed behavior must match privacy labels, manifests, privacy policy, and ATT state

## In-App Purchase Checklist

- [ ] Digital goods and subscriptions use StoreKit IAP unless current storefront rules or approved entitlements allow otherwise
- [ ] Subscription price, duration, billing frequency, auto-renewal terms, and any trial duration/post-trial price shown before purchase
- [ ] Restore purchases button present and functional
- [ ] No external purchase path, link, button, or call to action for digital goods unless current rules or approved entitlements allow it
- [ ] Ask-to-buy and interrupted purchases handled
- [ ] Transaction verification uses StoreKit 2 or server-side verification

## Screenshot and App Preview Checklist

- [ ] 1-10 screenshots uploaded for each required platform and localization
- [ ] iPhone screenshots use current App Store Connect accepted sizes; 6.9-inch iPhone screenshots are the primary set as of May 2026
- [ ] 6.5-inch iPhone screenshots provided only when 6.9-inch iPhone screenshots are not provided or when manually optimizing that fallback
- [ ] 13-inch iPad screenshots provided if the app runs on iPad
- [ ] Screenshots and preview videos show actual app UI and do not misrepresent unavailable features
- [ ] App previews are 30 seconds or shorter, with a poster frame that works without autoplay

## HIG Compliance Checklist

### Navigation
- [ ] `NavigationStack` used (not `NavigationView`)
- [ ] System back chevron used; no custom back icons
- [ ] Tab bar uses <= 5 tabs; use More tab if needed
- [ ] Avoid hamburger menus

### Modals and Sheets
- [ ] Sheets have a visible dismiss control
- [ ] Full-screen modals have close/done button
- [ ] Alerts use system alert styles

### System Feature Support
- [ ] Dark Mode renders correctly
- [ ] Dynamic Type supported throughout
- [ ] iPad multitasking supported (Slide Over, Split View)
- [ ] Dynamic Island / Live Activities render correctly when used
- [ ] System gestures not disabled

### Widgets and Live Activities
- [ ] Widgets show real content (not placeholders)
- [ ] Timelines update meaningfully
- [ ] Live Activities show time-sensitive info
- [ ] Lock Screen widgets are legible at small sizes

## Pre-Submission Checklist

### Completeness
- [ ] No placeholder or test content
- [ ] All features functional without special hardware
- [ ] Demo credentials or demo mode provided, with App Review notes for gated or non-obvious features
- [ ] No dead-end screens

### Metadata
- [ ] App name matches functionality
- [ ] Screenshots are real app screenshots using current required platform sizes, including 6.9-inch iPhone and 13-inch iPad when applicable
- [ ] Description contains no prices or competitor mentions
- [ ] Category is correct

### Privacy
- [ ] Privacy manifest present where required, with approved reason codes
- [ ] Third-party SDK manifests verified
- [ ] Privacy policy URL present and accessible
- [ ] Audit runtime network traffic and SDK transmissions; nutrition labels, privacy manifest declarations, privacy policy, and observed behavior match actual data collection
- [ ] ATT prompt only if tracking occurs

### Payments
- [ ] Digital content uses StoreKit IAP unless current rules or approved entitlements allow otherwise
- [ ] Subscription price, duration, billing frequency, auto-renewal terms, and any trial duration/post-trial price visible before purchase
- [ ] No external purchase paths, payment links, buttons, or calls to action unless current storefront rules or approved entitlements allow them
- [ ] Free trial terms clear
- [ ] Restore purchases implemented

### Design
- [ ] Standard navigation patterns used
- [ ] Dark Mode supported
- [ ] Dynamic Type supported
- [ ] No custom alerts mimicking system alerts
- [ ] Launch screen not an ad
- [ ] Empty states provide guidance

### Technical
- [ ] Built with Xcode 26 or later and relevant platform SDK 26 or later for uploads after April 28, 2026
- [ ] No private API usage
- [ ] No dynamic code execution
- [ ] Entitlements justified with usage descriptions
- [ ] Background modes justified and used
- [ ] Deployment target is intentionally chosen and tested

## Cross-Platform Stack Checklist (React Native / Expo / EAS / RevenueCat)

Field-tested gates from real rejections. Full root-cause analysis in [field-lessons-rn-expo.md](field-lessons-rn-expo.md).

### Interactive elements (2.1(a))
- [ ] Every element with `accessibilityRole="button"` has an `onPress` (or an explicit, documented `disabled` state)
- [ ] "Rate app" falls back to the App Store product page — the native prompt is a silent no-op in review builds
- [ ] No nested confirmation sheets; one confirmation is presented at a time
- [ ] Every Settings action produces a visible result (rate, delete account, logout, support)

### Authentication (2.1(a), 4.8)
- [ ] A `null` auth event never clears an established session without a settle window or revalidation against the native SDK
- [ ] Sign-out does not tear down the listener lifecycle needed by the next sign-in
- [ ] Network/offline errors are not treated as sign-out
- [ ] Sign in with Apple present when third-party login is offered: fresh nonce per attempt, silent cancellation handled, name persisted only on first authorization, `@privaterelay.appleid.com` accepted
- [ ] Cold start, reload with persisted session, logout, user switch, and network loss tested on iPhone **and** iPad in a release build

### Purchases (2.1(b), 3.1.1, 3.1.2)
- [ ] Paid Applications Agreement is `Active`
- [ ] Entitlement sync invalidates the provider cache and reads fresh customer info before falling back to the backend
- [ ] Pending server validation retries with backoff, then falls back to local customer info — never leaves content locked
- [ ] Entitlement grant re-renders the UI without an app restart
- [ ] Purchase tested in sandbox on a **physical iPad** (simulator does not reproduce sandbox IAP faithfully)
- [ ] Billed amount is the largest, highest-contrast element in each plan card; derived per-period prices are computed from the live product price, never hardcoded
- [ ] No external purchase path, deep link, route, or offering load for digital goods remains reachable on iOS
- [ ] Credit ledger entries originate only from an authenticated server webhook, idempotent on the provider event id, and are blocked client-side by security rules

### App Store Connect metadata
- [ ] IAP display name (30 chars) and description (45 chars) unique per product **within each locale**
- [ ] Promo images deleted, or visually distinct per promoted product (1024×1024, no transparency, no rounded corners)
- [ ] Age Rating declares only features a reviewer can locate and operate
- [ ] Support URL resolves to a page where a user can actually request support (verify the deployed anchor)
- [ ] Terms of Use configured in all three places: App Information EULA, App Description (every locale), and Subscription Terms of Use URL; both Terms and Privacy return HTTP 200
- [ ] Screenshots captured from the candidate build — never mockups, promotional renders, or non-iOS device chrome
- [ ] Every locale, device family, size, and orientation slot audited via **View All Sizes in Media Manager**; no stale assets remain
- [ ] Upload target locale matches the asset language (the binary's language does not select metadata language)

### Permissions (5.1.1(iv))
- [ ] Pre-permission buttons say "Continue"/"Next", never "Grant Permission" — visible label **and** `accessibilityLabel`
- [ ] The "Open Settings" recovery branch is preserved for the already-denied case

### Account and enrollment (5.1.1(ix))
- [ ] Developer Program enrollment type matches the app category; regulated categories require organization enrollment (not fixable in code — resolve before spending cycles on fixes)

### Build and submission pipeline
- [ ] Lockfile in sync with the manifest, generated on the CI Node major; both files committed together
- [ ] Build number verified higher than the last uploaded build via the App Store Connect API
- [ ] The fix commit is an ancestor of the submitted build's revision
- [ ] Four states verified independently: cloud build finished → submit processed → build attached to the version → Update Review
- [ ] Sandbox testers created (App Store Connect UI only — no API endpoint)
- [ ] API credentials (`.p8`, issuer id, key id) outside the repo and gitignored; JWTs never logged or committed
- [ ] **Stopped before `Update Review`** and obtained explicit owner confirmation
