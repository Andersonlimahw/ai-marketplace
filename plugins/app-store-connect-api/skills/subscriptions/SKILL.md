---
name: "subscriptions"
description: "Endpoints for managing auto-renewable subscriptions."
---

# Subscriptions
Endpoints for managing auto-renewable subscriptions.

## Endpoints

### `POST /v1/subscriptionAppStoreReviewScreenshots`
**Summary**: No summary provided.

### `GET /v1/subscriptionAppStoreReviewScreenshots/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[subscriptionAppStoreReviewScreenshots]` (query, optional): the fields to include for returned resources of type subscriptionAppStoreReviewScreenshots
- `fields[subscriptions]` (query, optional): the fields to include for returned resources of type subscriptions
- `include` (query, optional): comma-separated list of relationships to include

### `PATCH /v1/subscriptionAppStoreReviewScreenshots/{id}`
**Summary**: No summary provided.

### `DELETE /v1/subscriptionAppStoreReviewScreenshots/{id}`
**Summary**: No summary provided.

### `POST /v1/subscriptionAvailabilities`
**Summary**: No summary provided.

### `GET /v1/subscriptionAvailabilities/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[subscriptionAvailabilities]` (query, optional): the fields to include for returned resources of type subscriptionAvailabilities
- `fields[territories]` (query, optional): the fields to include for returned resources of type territories
- `include` (query, optional): comma-separated list of relationships to include
- `limit[availableTerritories]` (query, optional): maximum number of related availableTerritories returned (when they are included)

### `GET /v1/subscriptionGracePeriods/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[subscriptionGracePeriods]` (query, optional): the fields to include for returned resources of type subscriptionGracePeriods

### `PATCH /v1/subscriptionGracePeriods/{id}`
**Summary**: No summary provided.

### `POST /v1/subscriptionGroupLocalizations`
**Summary**: No summary provided.

### `GET /v1/subscriptionGroupLocalizations/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[subscriptionGroupLocalizations]` (query, optional): the fields to include for returned resources of type subscriptionGroupLocalizations
- `fields[subscriptionGroups]` (query, optional): the fields to include for returned resources of type subscriptionGroups
- `include` (query, optional): comma-separated list of relationships to include

### `PATCH /v1/subscriptionGroupLocalizations/{id}`
**Summary**: No summary provided.

### `DELETE /v1/subscriptionGroupLocalizations/{id}`
**Summary**: No summary provided.

### `POST /v1/subscriptionGroupSubmissions`
**Summary**: No summary provided.

### `POST /v1/subscriptionGroups`
**Summary**: No summary provided.

### `GET /v1/subscriptionGroups/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[subscriptionGroups]` (query, optional): the fields to include for returned resources of type subscriptionGroups
- `fields[subscriptions]` (query, optional): the fields to include for returned resources of type subscriptions
- `fields[subscriptionGroupLocalizations]` (query, optional): the fields to include for returned resources of type subscriptionGroupLocalizations
- `include` (query, optional): comma-separated list of relationships to include
- `limit[subscriptionGroupLocalizations]` (query, optional): maximum number of related subscriptionGroupLocalizations returned (when they are included)
- `limit[subscriptions]` (query, optional): maximum number of related subscriptions returned (when they are included)

### `PATCH /v1/subscriptionGroups/{id}`
**Summary**: No summary provided.

### `DELETE /v1/subscriptionGroups/{id}`
**Summary**: No summary provided.

### `POST /v1/subscriptionImages`
**Summary**: No summary provided.

### `GET /v1/subscriptionImages/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[subscriptionImages]` (query, optional): the fields to include for returned resources of type subscriptionImages
- `fields[subscriptions]` (query, optional): the fields to include for returned resources of type subscriptions
- `include` (query, optional): comma-separated list of relationships to include

### `PATCH /v1/subscriptionImages/{id}`
**Summary**: No summary provided.

### `DELETE /v1/subscriptionImages/{id}`
**Summary**: No summary provided.

### `POST /v1/subscriptionIntroductoryOffers`
**Summary**: No summary provided.

### `PATCH /v1/subscriptionIntroductoryOffers/{id}`
**Summary**: No summary provided.

### `DELETE /v1/subscriptionIntroductoryOffers/{id}`
**Summary**: No summary provided.

### `POST /v1/subscriptionLocalizations`
**Summary**: No summary provided.

### `GET /v1/subscriptionLocalizations/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[subscriptionLocalizations]` (query, optional): the fields to include for returned resources of type subscriptionLocalizations
- `fields[subscriptions]` (query, optional): the fields to include for returned resources of type subscriptions
- `include` (query, optional): comma-separated list of relationships to include

### `PATCH /v1/subscriptionLocalizations/{id}`
**Summary**: No summary provided.

### `DELETE /v1/subscriptionLocalizations/{id}`
**Summary**: No summary provided.

### `POST /v1/subscriptionOfferCodeCustomCodes`
**Summary**: No summary provided.

### `GET /v1/subscriptionOfferCodeCustomCodes/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[subscriptionOfferCodeCustomCodes]` (query, optional): the fields to include for returned resources of type subscriptionOfferCodeCustomCodes
- `fields[subscriptionOfferCodes]` (query, optional): the fields to include for returned resources of type subscriptionOfferCodes
- `include` (query, optional): comma-separated list of relationships to include

### `PATCH /v1/subscriptionOfferCodeCustomCodes/{id}`
**Summary**: No summary provided.

### `POST /v1/subscriptionOfferCodeOneTimeUseCodes`
**Summary**: No summary provided.

### `GET /v1/subscriptionOfferCodeOneTimeUseCodes/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[subscriptionOfferCodeOneTimeUseCodes]` (query, optional): the fields to include for returned resources of type subscriptionOfferCodeOneTimeUseCodes
- `fields[subscriptionOfferCodes]` (query, optional): the fields to include for returned resources of type subscriptionOfferCodes
- `include` (query, optional): comma-separated list of relationships to include

### `PATCH /v1/subscriptionOfferCodeOneTimeUseCodes/{id}`
**Summary**: No summary provided.

### `POST /v1/subscriptionOfferCodes`
**Summary**: No summary provided.

### `GET /v1/subscriptionOfferCodes/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[subscriptionOfferCodes]` (query, optional): the fields to include for returned resources of type subscriptionOfferCodes
- `fields[subscriptions]` (query, optional): the fields to include for returned resources of type subscriptions
- `fields[subscriptionOfferCodeOneTimeUseCodes]` (query, optional): the fields to include for returned resources of type subscriptionOfferCodeOneTimeUseCodes
- `fields[subscriptionOfferCodeCustomCodes]` (query, optional): the fields to include for returned resources of type subscriptionOfferCodeCustomCodes
- `fields[subscriptionOfferCodePrices]` (query, optional): the fields to include for returned resources of type subscriptionOfferCodePrices
- `include` (query, optional): comma-separated list of relationships to include
- `limit[customCodes]` (query, optional): maximum number of related customCodes returned (when they are included)
- `limit[oneTimeUseCodes]` (query, optional): maximum number of related oneTimeUseCodes returned (when they are included)
- `limit[prices]` (query, optional): maximum number of related prices returned (when they are included)

### `PATCH /v1/subscriptionOfferCodes/{id}`
**Summary**: No summary provided.

### `POST /v1/subscriptionPlanAvailabilities`
**Summary**: No summary provided.

### `GET /v1/subscriptionPlanAvailabilities/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[subscriptionPlanAvailabilities]` (query, optional): the fields to include for returned resources of type subscriptionPlanAvailabilities
- `fields[territories]` (query, optional): the fields to include for returned resources of type territories
- `include` (query, optional): comma-separated list of relationships to include
- `limit[availableTerritories]` (query, optional): maximum number of related availableTerritories returned (when they are included)

### `PATCH /v1/subscriptionPlanAvailabilities/{id}`
**Summary**: No summary provided.

### `GET /v1/subscriptionPricePoints/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[subscriptionPricePoints]` (query, optional): the fields to include for returned resources of type subscriptionPricePoints
- `fields[territories]` (query, optional): the fields to include for returned resources of type territories
- `include` (query, optional): comma-separated list of relationships to include

### `POST /v1/subscriptionPrices`
**Summary**: No summary provided.

### `DELETE /v1/subscriptionPrices/{id}`
**Summary**: No summary provided.

### `POST /v1/subscriptionPromotionalOffers`
**Summary**: No summary provided.

### `GET /v1/subscriptionPromotionalOffers/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[subscriptionPromotionalOffers]` (query, optional): the fields to include for returned resources of type subscriptionPromotionalOffers
- `fields[subscriptions]` (query, optional): the fields to include for returned resources of type subscriptions
- `fields[subscriptionPromotionalOfferPrices]` (query, optional): the fields to include for returned resources of type subscriptionPromotionalOfferPrices
- `include` (query, optional): comma-separated list of relationships to include
- `limit[prices]` (query, optional): maximum number of related prices returned (when they are included)

### `PATCH /v1/subscriptionPromotionalOffers/{id}`
**Summary**: No summary provided.

### `DELETE /v1/subscriptionPromotionalOffers/{id}`
**Summary**: No summary provided.

### `POST /v1/subscriptionSubmissions`
**Summary**: No summary provided.

### `POST /v1/subscriptions`
**Summary**: No summary provided.

### `GET /v1/subscriptions/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[subscriptions]` (query, optional): the fields to include for returned resources of type subscriptions
- `fields[subscriptionLocalizations]` (query, optional): the fields to include for returned resources of type subscriptionLocalizations
- `fields[subscriptionAppStoreReviewScreenshots]` (query, optional): the fields to include for returned resources of type subscriptionAppStoreReviewScreenshots
- `fields[subscriptionGroups]` (query, optional): the fields to include for returned resources of type subscriptionGroups
- `fields[subscriptionIntroductoryOffers]` (query, optional): the fields to include for returned resources of type subscriptionIntroductoryOffers
- `fields[subscriptionPromotionalOffers]` (query, optional): the fields to include for returned resources of type subscriptionPromotionalOffers
- `fields[subscriptionOfferCodes]` (query, optional): the fields to include for returned resources of type subscriptionOfferCodes
- `fields[subscriptionPrices]` (query, optional): the fields to include for returned resources of type subscriptionPrices
- `fields[promotedPurchases]` (query, optional): the fields to include for returned resources of type promotedPurchases
- `fields[subscriptionAvailabilities]` (query, optional): the fields to include for returned resources of type subscriptionAvailabilities
- `fields[winBackOffers]` (query, optional): the fields to include for returned resources of type winBackOffers
- `fields[subscriptionImages]` (query, optional): the fields to include for returned resources of type subscriptionImages
- `fields[subscriptionPlanAvailabilities]` (query, optional): the fields to include for returned resources of type subscriptionPlanAvailabilities
- `include` (query, optional): comma-separated list of relationships to include
- `limit[images]` (query, optional): maximum number of related images returned (when they are included)
- `limit[introductoryOffers]` (query, optional): maximum number of related introductoryOffers returned (when they are included)
- `limit[offerCodes]` (query, optional): maximum number of related offerCodes returned (when they are included)
- `limit[planAvailabilities]` (query, optional): maximum number of related planAvailabilities returned (when they are included)
- `limit[prices]` (query, optional): maximum number of related prices returned (when they are included)
- `limit[promotionalOffers]` (query, optional): maximum number of related promotionalOffers returned (when they are included)
- `limit[subscriptionLocalizations]` (query, optional): maximum number of related subscriptionLocalizations returned (when they are included)
- `limit[winBackOffers]` (query, optional): maximum number of related winBackOffers returned (when they are included)

### `PATCH /v1/subscriptions/{id}`
**Summary**: No summary provided.

### `DELETE /v1/subscriptions/{id}`
**Summary**: No summary provided.

### `GET /v1/subscriptionAvailabilities/{id}/relationships/availableTerritories`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `GET /v1/subscriptionAvailabilities/{id}/availableTerritories`
**Summary**: No summary provided.

**Parameters**:
- `fields[territories]` (query, optional): the fields to include for returned resources of type territories
- `limit` (query, optional): maximum resources per page

### `GET /v1/subscriptionGroups/{id}/relationships/subscriptionGroupLocalizations`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `GET /v1/subscriptionGroups/{id}/subscriptionGroupLocalizations`
**Summary**: No summary provided.

**Parameters**:
- `fields[subscriptionGroupLocalizations]` (query, optional): the fields to include for returned resources of type subscriptionGroupLocalizations
- `fields[subscriptionGroups]` (query, optional): the fields to include for returned resources of type subscriptionGroups
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include

### `GET /v1/subscriptionGroups/{id}/relationships/subscriptions`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `GET /v1/subscriptionGroups/{id}/subscriptions`
**Summary**: No summary provided.

**Parameters**:
- `filter[productId]` (query, optional): filter by attribute 'productId'
- `filter[name]` (query, optional): filter by attribute 'name'
- `filter[state]` (query, optional): filter by attribute 'state'
- `sort` (query, optional): comma-separated list of sort expressions; resources will be sorted as specified
- `fields[subscriptions]` (query, optional): the fields to include for returned resources of type subscriptions
- `fields[subscriptionLocalizations]` (query, optional): the fields to include for returned resources of type subscriptionLocalizations
- `fields[subscriptionAppStoreReviewScreenshots]` (query, optional): the fields to include for returned resources of type subscriptionAppStoreReviewScreenshots
- `fields[subscriptionGroups]` (query, optional): the fields to include for returned resources of type subscriptionGroups
- `fields[subscriptionIntroductoryOffers]` (query, optional): the fields to include for returned resources of type subscriptionIntroductoryOffers
- `fields[subscriptionPromotionalOffers]` (query, optional): the fields to include for returned resources of type subscriptionPromotionalOffers
- `fields[subscriptionOfferCodes]` (query, optional): the fields to include for returned resources of type subscriptionOfferCodes
- `fields[subscriptionPrices]` (query, optional): the fields to include for returned resources of type subscriptionPrices
- `fields[promotedPurchases]` (query, optional): the fields to include for returned resources of type promotedPurchases
- `fields[subscriptionAvailabilities]` (query, optional): the fields to include for returned resources of type subscriptionAvailabilities
- `fields[winBackOffers]` (query, optional): the fields to include for returned resources of type winBackOffers
- `fields[subscriptionImages]` (query, optional): the fields to include for returned resources of type subscriptionImages
- `fields[subscriptionPlanAvailabilities]` (query, optional): the fields to include for returned resources of type subscriptionPlanAvailabilities
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include
- `limit[subscriptionLocalizations]` (query, optional): maximum number of related subscriptionLocalizations returned (when they are included)
- `limit[introductoryOffers]` (query, optional): maximum number of related introductoryOffers returned (when they are included)
- `limit[promotionalOffers]` (query, optional): maximum number of related promotionalOffers returned (when they are included)
- `limit[offerCodes]` (query, optional): maximum number of related offerCodes returned (when they are included)
- `limit[prices]` (query, optional): maximum number of related prices returned (when they are included)
- `limit[winBackOffers]` (query, optional): maximum number of related winBackOffers returned (when they are included)
- `limit[images]` (query, optional): maximum number of related images returned (when they are included)
- `limit[planAvailabilities]` (query, optional): maximum number of related planAvailabilities returned (when they are included)

### `GET /v1/subscriptionOfferCodeOneTimeUseCodes/{id}/values`
**Summary**: No summary provided.

### `GET /v1/subscriptionOfferCodes/{id}/relationships/customCodes`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `GET /v1/subscriptionOfferCodes/{id}/customCodes`
**Summary**: No summary provided.

**Parameters**:
- `fields[subscriptionOfferCodeCustomCodes]` (query, optional): the fields to include for returned resources of type subscriptionOfferCodeCustomCodes
- `fields[subscriptionOfferCodes]` (query, optional): the fields to include for returned resources of type subscriptionOfferCodes
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include

### `GET /v1/subscriptionOfferCodes/{id}/relationships/oneTimeUseCodes`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `GET /v1/subscriptionOfferCodes/{id}/oneTimeUseCodes`
**Summary**: No summary provided.

**Parameters**:
- `fields[subscriptionOfferCodeOneTimeUseCodes]` (query, optional): the fields to include for returned resources of type subscriptionOfferCodeOneTimeUseCodes
- `fields[subscriptionOfferCodes]` (query, optional): the fields to include for returned resources of type subscriptionOfferCodes
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include

### `GET /v1/subscriptionOfferCodes/{id}/relationships/prices`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `GET /v1/subscriptionOfferCodes/{id}/prices`
**Summary**: No summary provided.

**Parameters**:
- `filter[territory]` (query, optional): filter by id(s) of related 'territory'
- `fields[subscriptionOfferCodePrices]` (query, optional): the fields to include for returned resources of type subscriptionOfferCodePrices
- `fields[territories]` (query, optional): the fields to include for returned resources of type territories
- `fields[subscriptionPricePoints]` (query, optional): the fields to include for returned resources of type subscriptionPricePoints
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include

### `GET /v1/subscriptionPlanAvailabilities/{id}/relationships/availableTerritories`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `PATCH /v1/subscriptionPlanAvailabilities/{id}/relationships/availableTerritories`
**Summary**: No summary provided.

### `GET /v1/subscriptionPlanAvailabilities/{id}/availableTerritories`
**Summary**: No summary provided.

**Parameters**:
- `fields[territories]` (query, optional): the fields to include for returned resources of type territories
- `limit` (query, optional): maximum resources per page

### `GET /v1/subscriptionPricePoints/{id}/relationships/equalizations`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `GET /v1/subscriptionPricePoints/{id}/equalizations`
**Summary**: No summary provided.

**Parameters**:
- `filter[territory]` (query, optional): filter by id(s) of related 'territory'
- `filter[subscription]` (query, optional): filter by id(s) of related 'subscription'
- `fields[subscriptionPricePoints]` (query, optional): the fields to include for returned resources of type subscriptionPricePoints
- `fields[territories]` (query, optional): the fields to include for returned resources of type territories
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include

### `GET /v1/subscriptionPromotionalOffers/{id}/relationships/prices`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `GET /v1/subscriptionPromotionalOffers/{id}/prices`
**Summary**: No summary provided.

**Parameters**:
- `filter[territory]` (query, optional): filter by id(s) of related 'territory'
- `fields[subscriptionPromotionalOfferPrices]` (query, optional): the fields to include for returned resources of type subscriptionPromotionalOfferPrices
- `fields[territories]` (query, optional): the fields to include for returned resources of type territories
- `fields[subscriptionPricePoints]` (query, optional): the fields to include for returned resources of type subscriptionPricePoints
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include

### `GET /v1/subscriptions/{id}/relationships/appStoreReviewScreenshot`
**Summary**: No summary provided.

### `GET /v1/subscriptions/{id}/appStoreReviewScreenshot`
**Summary**: No summary provided.

**Parameters**:
- `fields[subscriptionAppStoreReviewScreenshots]` (query, optional): the fields to include for returned resources of type subscriptionAppStoreReviewScreenshots
- `fields[subscriptions]` (query, optional): the fields to include for returned resources of type subscriptions
- `include` (query, optional): comma-separated list of relationships to include

### `GET /v1/subscriptions/{id}/relationships/images`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `GET /v1/subscriptions/{id}/images`
**Summary**: No summary provided.

**Parameters**:
- `fields[subscriptionImages]` (query, optional): the fields to include for returned resources of type subscriptionImages
- `fields[subscriptions]` (query, optional): the fields to include for returned resources of type subscriptions
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include

### `GET /v1/subscriptions/{id}/relationships/introductoryOffers`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `DELETE /v1/subscriptions/{id}/relationships/introductoryOffers`
**Summary**: No summary provided.

### `GET /v1/subscriptions/{id}/introductoryOffers`
**Summary**: No summary provided.

**Parameters**:
- `filter[territory]` (query, optional): filter by id(s) of related 'territory'
- `fields[subscriptionIntroductoryOffers]` (query, optional): the fields to include for returned resources of type subscriptionIntroductoryOffers
- `fields[subscriptions]` (query, optional): the fields to include for returned resources of type subscriptions
- `fields[territories]` (query, optional): the fields to include for returned resources of type territories
- `fields[subscriptionPricePoints]` (query, optional): the fields to include for returned resources of type subscriptionPricePoints
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include

### `GET /v1/subscriptions/{id}/relationships/offerCodes`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `GET /v1/subscriptions/{id}/offerCodes`
**Summary**: No summary provided.

**Parameters**:
- `filter[territory]` (query, optional): filter by territory
- `fields[subscriptionOfferCodes]` (query, optional): the fields to include for returned resources of type subscriptionOfferCodes
- `fields[subscriptions]` (query, optional): the fields to include for returned resources of type subscriptions
- `fields[subscriptionOfferCodeOneTimeUseCodes]` (query, optional): the fields to include for returned resources of type subscriptionOfferCodeOneTimeUseCodes
- `fields[subscriptionOfferCodeCustomCodes]` (query, optional): the fields to include for returned resources of type subscriptionOfferCodeCustomCodes
- `fields[subscriptionOfferCodePrices]` (query, optional): the fields to include for returned resources of type subscriptionOfferCodePrices
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include
- `limit[oneTimeUseCodes]` (query, optional): maximum number of related oneTimeUseCodes returned (when they are included)
- `limit[customCodes]` (query, optional): maximum number of related customCodes returned (when they are included)
- `limit[prices]` (query, optional): maximum number of related prices returned (when they are included)

### `GET /v1/subscriptions/{id}/relationships/planAvailabilities`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `GET /v1/subscriptions/{id}/planAvailabilities`
**Summary**: No summary provided.

**Parameters**:
- `fields[subscriptionPlanAvailabilities]` (query, optional): the fields to include for returned resources of type subscriptionPlanAvailabilities
- `fields[territories]` (query, optional): the fields to include for returned resources of type territories
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include
- `limit[availableTerritories]` (query, optional): maximum number of related availableTerritories returned (when they are included)

### `GET /v1/subscriptions/{id}/relationships/pricePoints`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `GET /v1/subscriptions/{id}/pricePoints`
**Summary**: No summary provided.

**Parameters**:
- `filter[territory]` (query, optional): filter by id(s) of related 'territory'
- `fields[subscriptionPricePoints]` (query, optional): the fields to include for returned resources of type subscriptionPricePoints
- `fields[territories]` (query, optional): the fields to include for returned resources of type territories
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include

### `GET /v1/subscriptions/{id}/relationships/prices`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `DELETE /v1/subscriptions/{id}/relationships/prices`
**Summary**: No summary provided.

### `GET /v1/subscriptions/{id}/prices`
**Summary**: No summary provided.

**Parameters**:
- `filter[planType]` (query, optional): filter by attribute 'planType'
- `filter[subscriptionPricePoint]` (query, optional): filter by id(s) of related 'subscriptionPricePoint'
- `filter[territory]` (query, optional): filter by id(s) of related 'territory'
- `fields[subscriptionPrices]` (query, optional): the fields to include for returned resources of type subscriptionPrices
- `fields[territories]` (query, optional): the fields to include for returned resources of type territories
- `fields[subscriptionPricePoints]` (query, optional): the fields to include for returned resources of type subscriptionPricePoints
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include

### `GET /v1/subscriptions/{id}/relationships/promotedPurchase`
**Summary**: No summary provided.

### `GET /v1/subscriptions/{id}/promotedPurchase`
**Summary**: No summary provided.

**Parameters**:
- `fields[promotedPurchases]` (query, optional): the fields to include for returned resources of type promotedPurchases
- `fields[inAppPurchases]` (query, optional): the fields to include for returned resources of type inAppPurchases
- `fields[subscriptions]` (query, optional): the fields to include for returned resources of type subscriptions
- `include` (query, optional): comma-separated list of relationships to include

### `GET /v1/subscriptions/{id}/relationships/promotionalOffers`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `GET /v1/subscriptions/{id}/promotionalOffers`
**Summary**: No summary provided.

**Parameters**:
- `filter[territory]` (query, optional): filter by territory
- `fields[subscriptionPromotionalOffers]` (query, optional): the fields to include for returned resources of type subscriptionPromotionalOffers
- `fields[subscriptions]` (query, optional): the fields to include for returned resources of type subscriptions
- `fields[subscriptionPromotionalOfferPrices]` (query, optional): the fields to include for returned resources of type subscriptionPromotionalOfferPrices
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include
- `limit[prices]` (query, optional): maximum number of related prices returned (when they are included)

### `GET /v1/subscriptions/{id}/relationships/subscriptionAvailability`
**Summary**: No summary provided.

### `GET /v1/subscriptions/{id}/subscriptionAvailability`
**Summary**: No summary provided.

**Parameters**:
- `fields[subscriptionAvailabilities]` (query, optional): the fields to include for returned resources of type subscriptionAvailabilities
- `fields[territories]` (query, optional): the fields to include for returned resources of type territories
- `include` (query, optional): comma-separated list of relationships to include
- `limit[availableTerritories]` (query, optional): maximum number of related availableTerritories returned (when they are included)

### `GET /v1/subscriptions/{id}/relationships/subscriptionLocalizations`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `GET /v1/subscriptions/{id}/subscriptionLocalizations`
**Summary**: No summary provided.

**Parameters**:
- `fields[subscriptionLocalizations]` (query, optional): the fields to include for returned resources of type subscriptionLocalizations
- `fields[subscriptions]` (query, optional): the fields to include for returned resources of type subscriptions
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include

### `GET /v1/subscriptions/{id}/relationships/winBackOffers`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `GET /v1/subscriptions/{id}/winBackOffers`
**Summary**: No summary provided.

**Parameters**:
- `fields[winBackOffers]` (query, optional): the fields to include for returned resources of type winBackOffers
- `fields[winBackOfferPrices]` (query, optional): the fields to include for returned resources of type winBackOfferPrices
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include
- `limit[prices]` (query, optional): maximum number of related prices returned (when they are included)

## Typical Workflows
Use these endpoints to automate subscriptions tasks within Apple Store Connect.

## Best Practices
- Always authenticate requests using your Apple Store Connect API key (JWT token).
- Handle rate limiting gracefully, as the Apple Store Connect API enforces quotas.
- When writing integrations, refer back to the exact schemas for precise payload construction.

## App Review subscription guardrails

- Configure a Terms of Use URL for every subscription where the App Store Connect schema exposes that field, and keep it aligned with the app-level EULA and every localized description.
- Before review, verify both Terms of Use and Privacy URLs return HTTP 200 and are reachable from inside the app.
- In the paywall, the billed subscription amount must be the largest typographic element in the plan card. A calculated per-period amount is subordinate in size and position, and must be computed from the live product price rather than hardcoded per locale.
- Use `app-store-review` for the compliance audit; use this skill for the subscription API resources and relationships.
