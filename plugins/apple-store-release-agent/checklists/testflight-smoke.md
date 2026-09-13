# TestFlight Smoke Checklist

Run on the TestFlight build before App Review. Mark each pass/fail.

## Install
- [ ] Install succeeds on target iOS version(s)
- [ ] App icon + launch screen correct (no default/Expo icon)
- [ ] First-launch size reasonable (no huge asset download)

## Cold Start
- [ ] Cold start < ~3s on mid-range device
- [ ] No crash on first launch
- [ ] Cold-launched **5×** on this Release/TestFlight build specifically — a broken top-level import of a recently added native package crashes before the root component mounts and does not reproduce in Debug/dev-client
- [ ] Splash → onboarding/home transitions smooth

## Auth
- [ ] Signup flow works (email + OAuth if present)
- [ ] Login flow works
- [ ] Sign in with Apple configured (if social login offered)
- [ ] Password reset / magic link works

## Onboarding
- [ ] Onboarding completes for new user
- [ ] Locale defaults correctly (PT/EN/ES by device)
- [ ] Permissions requested at the right moment with clear copy

## Main Flows
- [ ] Primary use-case flow completes (e.g. create/join match for a soccer app)
- [ ] Data persists across cold start
- [ ] Offline / poor-network states handled

## IAP (Sandbox)
- [ ] Paywall loads with correct prices
- [ ] Sandbox purchase grants entitlement
- [ ] Restore Purchases works after reinstall
- [ ] Consumable purchase (e.g. Soccer Coins) credits correctly

## Account Deletion
- [ ] Delete account reachable
- [ ] Deletion confirms and signs out
- [ ] Re-signup creates fresh state
- [ ] Destructive confirmation tested on a **physical iPad** — nested confirmation sheets (a second one fired from inside the first's `onConfirm`) race the dismiss animation and reproduce mainly there, not on iPhone

## Crash / Stability Review
- [ ] No crashes observed across smoke run
- [ ] Crashlytics reporting confirmed (if enabled)
- [ ] No infinite spinners / ANRs on main flows
