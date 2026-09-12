# Google Play Review Checklist

Use before submitting. Every box must be checked for **GO**.

## App completeness
- [ ] App name, package, versionCode, versionName set
- [ ] App builds a signed `.aab` for production
- [ ] Target SDK meets the current Play requirement
- [ ] No mock data in release build (`EXPO_PUBLIC_USE_MOCK=false`)
- [ ] No debug flags / test endpoints

## Authentication
- [ ] Login works on a clean install
- [ ] Account creation flow complete
- [ ] **Account deletion** available in-app (required if accounts exist)
- [ ] Password reset / re-auth works

## Stability
- [ ] No crashes on cold start
- [ ] Cold-launched the release build 5× after adding any native package (`expo-*`/`react-native-*`) — a broken native link imported at top-of-file crashes before the root component mounts on Android too, and does not reproduce in a debug build (cross-platform with the iOS crash-on-launch pattern)
- [ ] No interactive element (button, pressable) with a visible/accessible role and no press handler — same failure class as iOS's dead-button rejection
- [ ] No ANRs on main flows
- [ ] Pre-launch report reviewed (Roboto test)
- [ ] Crashlytics / crash reporting configured

## Store listing
- [ ] Title (≤30 chars)
- [ ] Short description (≤80 chars)
- [ ] Full description (≤4000 chars)
- [ ] App icon (512x512, 32-bit PNG)
- [ ] Feature graphic (1024x500)
- [ ] Screenshots (min 2, max 8 per type: phone, tablet optional)
- [ ] No gambling/betting/money-guarantee language anywhere

## Categorization
- [ ] Content rating questionnaire complete
- [ ] App category selected
- [ ] Tags added
- [ ] Target audience set

## Contact & policy
- [ ] Contact email / details valid
- [ ] Privacy Policy URL live and reachable
- [ ] Terms of Service URL (if applicable)

## Access
- [ ] App access instructions provided (if login-gated)
- [ ] Test account credentials provided to reviewers (if needed)

## Policy risks
- [ ] No sensitive permissions without justification
- [ ] Data Safety Form reviewed by a human
- [ ] No IAP products referenced without Play Console product
- [ ] No "guaranteed" money/payout/withdrawal claims

## Production readiness
- [ ] Internal testing passed
- [ ] Closed testing completed
- [ ] Human explicitly approved this release
