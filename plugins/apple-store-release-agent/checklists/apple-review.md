# Apple Review Checklist

Walk this checklist before any submission. Items marked ⚠️ BLOCKER force NO_GO if failed.

## App Completeness
- [ ] App launches without crash on cold start
- [ ] Cold-launched the **Release** build 5× — a recently added native package (`expo-*`/`react-native-*`) imported at top-of-file crashes on launch with no JS stack trace; Debug/dev-client builds do not reproduce this — ⚠️ BLOCKER if any recently added native package is imported statically
- [ ] All primary flows functional (no "coming soon", no dead buttons)
- [ ] No `accessibilityRole="button"` element without a matching `onPress` — ⚠️ BLOCKER (reliably triggers 2.1(a))
- [ ] No destructive action wired to nested confirmation sheets (a second `confirmAction` fired from inside the first's `onConfirm`) — races the dismiss animation, mainly on iPad
- [ ] The full route table was audited for the above two patterns, not just screens currently linked from a tab bar or stack — an unlinked-but-registered route is still reachable
- [ ] No placeholder/lorem-ipsum content visible to users
- [ ] No debug/staging menus reachable in prod build
- [ ] `EXPO_PUBLIC_USE_MOCK` is NOT `true` in production env

## Metadata Accuracy
- [ ] Description matches shipping functionality
- [ ] Keywords relevant, no competitor trademarks, no spam
- [ ] Screenshots from the **shipping** build, correct device sizes
- [ ] App category + age rating correct
- [ ] No forbidden wording (aposta, betting, gambling, cashout garantido, ganhe dinheiro, lucro, renda garantida, saque garantido) — ⚠️ BLOCKER

## Login & Demo Account
- [ ] Demo account credentials provided in Review Notes — ⚠️ BLOCKER (login-gated apps)
- [ ] Demo account has enough data/state to exercise main flows
- [ ] Third-party login (Sign in with Apple/Google) configured and documented

## Account Deletion — ⚠️ BLOCKER (if signup exists)
- [ ] In-app account deletion reachable from settings
- [ ] Deletion explains data retention/erasure behavior
- [ ] Deletion path tested end-to-end

## IAP / Subscriptions
- [ ] All purchasable items use Apple IAP (no external payment links) — ⚠️ BLOCKER
- [ ] Restore Purchases reachable and functional — ⚠️ BLOCKER
- [ ] Subscription terms + auto-renew disclosed near purchase
- [ ] Virtual currency framed as non-monetary (no cash/withdraw wording) — ⚠️ BLOCKER

## Privacy & Legal
- [ ] Privacy Policy URL reachable — ⚠️ BLOCKER
- [ ] Terms of Service URL reachable — ⚠️ BLOCKER
- [ ] App Privacy labels declared in App Store Connect
- [ ] ATT prompt present if tracking SDKs used

## Stability
- [ ] No known crashes on key devices (iPhone + iPad if universal)
- [ ] Offline / poor-network states handled gracefully
- [ ] No ANR / infinite spinners on main flows

## Review Notes
- [ ] APP_STORE_REVIEW_NOTES.md populated (see templates/review-notes.md)
- [ ] Special configurations flagged for reviewer (feature flags, env)

## Rejection Response Discipline (if responding to a prior rejection)
- [ ] Reproduced (or confirmed fixed) against **current** code, not just the commit that claims the fix — the reviewed build may be behind `main`
- [ ] Checked whether the cited guideline is actually an App Store Connect metadata issue (IAP localization, description, review notes, age rating) before assuming it's a code change
- [ ] Each finding split into code-provable (typecheck/test/grep) vs human-only (physical device, ASC UI, agreements, sandbox tester) — a green CI run does not close a human-only finding
- [ ] Each closed finding has a static regression test that would have caught it
- [ ] Reviewer response drafted for the **Resolution Center**; App Review Appeal (`https://developer.apple.com/contact/request/app-review/appeal/`) only considered if that exchange doesn't resolve it

## Final
- [ ] Build version incremented vs last App Store version
- [ ] All five pipeline states verified independently (build finished, submit processed, TestFlight Ready to Submit, build attached to version, Update Review) — not assumed from the first
- [ ] Decision is GO or GO_WITH_WARNINGS (no open BLOCKER)
