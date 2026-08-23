---
name: "in-app-purchases"
description: "Endpoints for managing in-app purchases and promoted purchases."
---

# In-App Purchases
Endpoints for managing in-app purchases and promoted purchases.

## Endpoints

### `POST /v1/inAppPurchaseAppStoreReviewScreenshots`
**Summary**: No summary provided.

### `GET /v1/inAppPurchaseAppStoreReviewScreenshots/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[inAppPurchaseAppStoreReviewScreenshots]` (query, optional): the fields to include for returned resources of type inAppPurchaseAppStoreReviewScreenshots
- `fields[inAppPurchases]` (query, optional): the fields to include for returned resources of type inAppPurchases
- `include` (query, optional): comma-separated list of relationships to include

### `PATCH /v1/inAppPurchaseAppStoreReviewScreenshots/{id}`
**Summary**: No summary provided.

### `DELETE /v1/inAppPurchaseAppStoreReviewScreenshots/{id}`
**Summary**: No summary provided.

### `POST /v1/inAppPurchaseAvailabilities`
**Summary**: No summary provided.

### `GET /v1/inAppPurchaseAvailabilities/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[inAppPurchaseAvailabilities]` (query, optional): the fields to include for returned resources of type inAppPurchaseAvailabilities
- `fields[territories]` (query, optional): the fields to include for returned resources of type territories
- `include` (query, optional): comma-separated list of relationships to include
- `limit[availableTerritories]` (query, optional): maximum number of related availableTerritories returned (when they are included)

### `GET /v1/inAppPurchaseContents/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[inAppPurchaseContents]` (query, optional): the fields to include for returned resources of type inAppPurchaseContents
- `fields[inAppPurchases]` (query, optional): the fields to include for returned resources of type inAppPurchases
- `include` (query, optional): comma-separated list of relationships to include

### `POST /v1/inAppPurchaseImages`
**Summary**: No summary provided.

### `GET /v1/inAppPurchaseImages/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[inAppPurchaseImages]` (query, optional): the fields to include for returned resources of type inAppPurchaseImages
- `fields[inAppPurchases]` (query, optional): the fields to include for returned resources of type inAppPurchases
- `include` (query, optional): comma-separated list of relationships to include

### `PATCH /v1/inAppPurchaseImages/{id}`
**Summary**: No summary provided.

### `DELETE /v1/inAppPurchaseImages/{id}`
**Summary**: No summary provided.

### `POST /v1/inAppPurchaseLocalizations`
**Summary**: No summary provided.

### `GET /v1/inAppPurchaseLocalizations/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[inAppPurchaseLocalizations]` (query, optional): the fields to include for returned resources of type inAppPurchaseLocalizations
- `fields[inAppPurchases]` (query, optional): the fields to include for returned resources of type inAppPurchases
- `include` (query, optional): comma-separated list of relationships to include

### `PATCH /v1/inAppPurchaseLocalizations/{id}`
**Summary**: No summary provided.

### `DELETE /v1/inAppPurchaseLocalizations/{id}`
**Summary**: No summary provided.

### `POST /v1/inAppPurchaseOfferCodeCustomCodes`
**Summary**: No summary provided.

### `GET /v1/inAppPurchaseOfferCodeCustomCodes/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[inAppPurchaseOfferCodeCustomCodes]` (query, optional): the fields to include for returned resources of type inAppPurchaseOfferCodeCustomCodes
- `fields[actors]` (query, optional): the fields to include for returned resources of type actors
- `include` (query, optional): comma-separated list of relationships to include

### `PATCH /v1/inAppPurchaseOfferCodeCustomCodes/{id}`
**Summary**: No summary provided.

### `POST /v1/inAppPurchaseOfferCodeOneTimeUseCodes`
**Summary**: No summary provided.

### `GET /v1/inAppPurchaseOfferCodeOneTimeUseCodes/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[inAppPurchaseOfferCodeOneTimeUseCodes]` (query, optional): the fields to include for returned resources of type inAppPurchaseOfferCodeOneTimeUseCodes
- `fields[actors]` (query, optional): the fields to include for returned resources of type actors
- `include` (query, optional): comma-separated list of relationships to include

### `PATCH /v1/inAppPurchaseOfferCodeOneTimeUseCodes/{id}`
**Summary**: No summary provided.

### `POST /v1/inAppPurchaseOfferCodes`
**Summary**: No summary provided.

### `GET /v1/inAppPurchaseOfferCodes/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[inAppPurchaseOfferCodes]` (query, optional): the fields to include for returned resources of type inAppPurchaseOfferCodes
- `fields[inAppPurchaseOfferCodeOneTimeUseCodes]` (query, optional): the fields to include for returned resources of type inAppPurchaseOfferCodeOneTimeUseCodes
- `fields[inAppPurchaseOfferCodeCustomCodes]` (query, optional): the fields to include for returned resources of type inAppPurchaseOfferCodeCustomCodes
- `fields[inAppPurchaseOfferPrices]` (query, optional): the fields to include for returned resources of type inAppPurchaseOfferPrices
- `include` (query, optional): comma-separated list of relationships to include
- `limit[customCodes]` (query, optional): maximum number of related customCodes returned (when they are included)
- `limit[oneTimeUseCodes]` (query, optional): maximum number of related oneTimeUseCodes returned (when they are included)
- `limit[prices]` (query, optional): maximum number of related prices returned (when they are included)

### `PATCH /v1/inAppPurchaseOfferCodes/{id}`
**Summary**: No summary provided.

### `POST /v1/inAppPurchasePriceSchedules`
**Summary**: No summary provided.

### `GET /v1/inAppPurchasePriceSchedules/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[inAppPurchasePriceSchedules]` (query, optional): the fields to include for returned resources of type inAppPurchasePriceSchedules
- `fields[territories]` (query, optional): the fields to include for returned resources of type territories
- `fields[inAppPurchasePrices]` (query, optional): the fields to include for returned resources of type inAppPurchasePrices
- `include` (query, optional): comma-separated list of relationships to include
- `limit[automaticPrices]` (query, optional): maximum number of related automaticPrices returned (when they are included)
- `limit[manualPrices]` (query, optional): maximum number of related manualPrices returned (when they are included)

### `POST /v1/inAppPurchaseSubmissions`
**Summary**: No summary provided.

### `GET /v1/inAppPurchases/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[inAppPurchases]` (query, optional): the fields to include for returned resources of type inAppPurchases
- `fields[apps]` (query, optional): the fields to include for returned resources of type apps
- `include` (query, optional): comma-separated list of relationships to include
- `limit[apps]` (query, optional): maximum number of related apps returned (when they are included)

### `POST /v1/promotedPurchases`
**Summary**: No summary provided.

### `GET /v1/promotedPurchases/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[promotedPurchases]` (query, optional): the fields to include for returned resources of type promotedPurchases
- `fields[inAppPurchases]` (query, optional): the fields to include for returned resources of type inAppPurchases
- `fields[subscriptions]` (query, optional): the fields to include for returned resources of type subscriptions
- `include` (query, optional): comma-separated list of relationships to include

### `PATCH /v1/promotedPurchases/{id}`
**Summary**: No summary provided.

### `DELETE /v1/promotedPurchases/{id}`
**Summary**: No summary provided.

### `GET /v1/inAppPurchaseAvailabilities/{id}/relationships/availableTerritories`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `GET /v1/inAppPurchaseAvailabilities/{id}/availableTerritories`
**Summary**: No summary provided.

**Parameters**:
- `fields[territories]` (query, optional): the fields to include for returned resources of type territories
- `limit` (query, optional): maximum resources per page

### `GET /v1/inAppPurchaseOfferCodeOneTimeUseCodes/{id}/values`
**Summary**: No summary provided.

### `GET /v1/inAppPurchaseOfferCodes/{id}/relationships/customCodes`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `GET /v1/inAppPurchaseOfferCodes/{id}/customCodes`
**Summary**: No summary provided.

**Parameters**:
- `fields[inAppPurchaseOfferCodeCustomCodes]` (query, optional): the fields to include for returned resources of type inAppPurchaseOfferCodeCustomCodes
- `fields[actors]` (query, optional): the fields to include for returned resources of type actors
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include

### `GET /v1/inAppPurchaseOfferCodes/{id}/relationships/oneTimeUseCodes`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `GET /v1/inAppPurchaseOfferCodes/{id}/oneTimeUseCodes`
**Summary**: No summary provided.

**Parameters**:
- `fields[inAppPurchaseOfferCodeOneTimeUseCodes]` (query, optional): the fields to include for returned resources of type inAppPurchaseOfferCodeOneTimeUseCodes
- `fields[actors]` (query, optional): the fields to include for returned resources of type actors
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include

### `GET /v1/inAppPurchaseOfferCodes/{id}/relationships/prices`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `GET /v1/inAppPurchaseOfferCodes/{id}/prices`
**Summary**: No summary provided.

**Parameters**:
- `filter[territory]` (query, optional): filter by id(s) of related 'territory'
- `fields[inAppPurchaseOfferPrices]` (query, optional): the fields to include for returned resources of type inAppPurchaseOfferPrices
- `fields[territories]` (query, optional): the fields to include for returned resources of type territories
- `fields[inAppPurchasePricePoints]` (query, optional): the fields to include for returned resources of type inAppPurchasePricePoints
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include

### `GET /v1/inAppPurchasePricePoints/{id}/relationships/equalizations`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `GET /v1/inAppPurchasePricePoints/{id}/equalizations`
**Summary**: No summary provided.

**Parameters**:
- `filter[territory]` (query, optional): filter by id(s) of related 'territory'
- `filter[inAppPurchaseV2]` (query, optional): filter by id(s) of related 'inAppPurchaseV2'
- `fields[inAppPurchasePricePoints]` (query, optional): the fields to include for returned resources of type inAppPurchasePricePoints
- `fields[territories]` (query, optional): the fields to include for returned resources of type territories
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include

### `GET /v1/inAppPurchasePriceSchedules/{id}/relationships/automaticPrices`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `GET /v1/inAppPurchasePriceSchedules/{id}/automaticPrices`
**Summary**: No summary provided.

**Parameters**:
- `filter[territory]` (query, optional): filter by id(s) of related 'territory'
- `fields[inAppPurchasePrices]` (query, optional): the fields to include for returned resources of type inAppPurchasePrices
- `fields[inAppPurchasePricePoints]` (query, optional): the fields to include for returned resources of type inAppPurchasePricePoints
- `fields[territories]` (query, optional): the fields to include for returned resources of type territories
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include

### `GET /v1/inAppPurchasePriceSchedules/{id}/relationships/baseTerritory`
**Summary**: No summary provided.

### `GET /v1/inAppPurchasePriceSchedules/{id}/baseTerritory`
**Summary**: No summary provided.

**Parameters**:
- `fields[territories]` (query, optional): the fields to include for returned resources of type territories

### `GET /v1/inAppPurchasePriceSchedules/{id}/relationships/manualPrices`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `GET /v1/inAppPurchasePriceSchedules/{id}/manualPrices`
**Summary**: No summary provided.

**Parameters**:
- `filter[territory]` (query, optional): filter by id(s) of related 'territory'
- `fields[inAppPurchasePrices]` (query, optional): the fields to include for returned resources of type inAppPurchasePrices
- `fields[inAppPurchasePricePoints]` (query, optional): the fields to include for returned resources of type inAppPurchasePricePoints
- `fields[territories]` (query, optional): the fields to include for returned resources of type territories
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include

## Typical Workflows
Use these endpoints to automate in-app purchases tasks within Apple Store Connect.

## Best Practices
- Always authenticate requests using your Apple Store Connect API key (JWT token).
- Handle rate limiting gracefully, as the Apple Store Connect API enforces quotas.
- When writing integrations, refer back to the exact schemas for precise payload construction.

## App Review metadata guardrails

When IAP resources are being prepared for App Review, keep the API operation and the compliance decision separate:

- Each localized IAP display name is unique within its locale and stays at or below 30 characters.
- Each localized IAP description is unique within its locale and stays at or below 45 characters.
- If promoted IAP images are duplicated, the lowest-cost remediation is to delete the image with `DELETE /v1/promotedPurchaseImages/{id}` rather than inventing a new asset.
- A `409 UNMODIFIABLE` response can occur while the app version is `WAITING_FOR_REVIEW`; remove the submission from review before editing locked metadata, then re-check the linked IAPs and screenshots.
- Audit every product × locale pair before a submission. App Store review compliance belongs to `app-store-review`; this skill supplies the API operations only.
