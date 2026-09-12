---
name: "app-store-connect-api"
description: "Expert agent for the Apple Store Connect API. Use when the user asks questions about the App Store Connect API or needs to automate tasks involving TestFlight, In-App Purchases, Provisioning, App Metadata, Reporting, or Game Center."
---

# Apple Store Connect API Expert

This skill acts as the entry point and overarching knowledge base for the Apple Store Connect API.
It is composed of multiple specialized skills that cover the specific domains of the API:

- **App Management & Metadata**: Managing app versions, screenshots, localizations, and app reviews.
- **TestFlight & Provisioning**: Managing beta testers, build deployments, profiles, and certificates.
- **Monetization**: In-app purchases, Subscriptions, and Pricing.
- **Reporting & Analytics**: Sales, Financial reports, and app analytics.
- **Game Center & App Clips**: Managing achievements, leaderboards, and App Clip experiences.
- **Users & Customer Reviews**: Managing team roles and responding to user reviews.

## Capabilities
When tasked with an App Store Connect API operation, refer to the corresponding domain skill to access detailed endpoint paths, required parameters, and best practices.

## What the API Can and Cannot Do

Field-observed from real release/review cycles — the gap between "the OpenAPI spec has an endpoint" and "this is actually usable for the task" is the single most expensive thing to learn by trial and error. Re-check against Apple's current API reference before treating any row as a hard blocker; this surface changes.

| Action | API? | Note |
|---|---|---|
| Read submission state, builds, IAPs, age rating | ✅ Yes | Read-only queries are safe to automate |
| Age Rating declaration | ✅ `PATCH /v1/ageRatingDeclarations/{id}` | Confirm with the account owner before writing |
| IAP / subscription localization (name, description) | ✅ `PATCH /v1/inAppPurchaseLocalizations/{id}` | Hard limits: display name 30 chars, description 45 chars |
| Delete a promotional image | ✅ `DELETE /v1/promotedPurchaseImages/{id}` | Often simpler than authoring two visually distinct images |
| Upload a promotional image | ⚠️ Yes, but 3-step (reserve → upload → commit) | The App Store Connect UI is faster for a one-off |
| Upload App Store screenshots | ⚠️ Technically yes | Possible but painful; the UI's Media Manager is recommended |
| **Read a crash log the reviewer attached** | ❌ No | `GET /v1/builds/{id}/diagnosticSignatures` returns empty for reviewer-attached reports — the attachment only exists in the Resolution Center UI |
| **Read or reply to the Resolution Center thread** | ❌ No | No endpoint surfaces reviewer messages; UI only |
| **Create a sandbox tester** | ❌ No | `POST /v1/sandboxTesters` returns `404 PATH_ERROR`; Users and Access UI only |
| Submit for review / Update Review | ✅ Technically yes | 🚫 Never call without explicit, visible confirmation from the account owner — this is outward-facing and effectively irreversible |

**Credential hygiene (non-negotiable):** the `.p8` private key, issuer ID, and key ID live outside any repo (e.g. `~/.config/asc/`), are `.gitignore`d (`*.p8`, `AuthKey_*.p8`, `credentials.env`), and generated JWTs (20-minute lifetime) are never logged or committed in plaintext. Scope the API key role to the minimum the task needs. On any suspected leak: revoke in App Store Connect, recreate, rotate.

For the official human-contact channels when the API and the Resolution Center both fall short (there is no direct email or executive contact), see `app-store-review`'s field lessons.

## OpenAPI Reference
The agent derives its knowledge from the official App Store Connect OpenAPI specification. Always ensure requests match the expected payload structure defined in the `openapi.oas.json`.
