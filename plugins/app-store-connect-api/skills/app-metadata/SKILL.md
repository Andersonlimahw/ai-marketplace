---
name: "app-metadata"
description: "Endpoints for managing app screenshots, product pages, and localizations."
---

# App Metadata
Endpoints for managing app screenshots, product pages, and localizations.

## Endpoints

### `POST /v1/appCustomProductPages`
**Summary**: No summary provided.

### `GET /v1/appCustomProductPages/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[appCustomProductPages]` (query, optional): the fields to include for returned resources of type appCustomProductPages
- `fields[apps]` (query, optional): the fields to include for returned resources of type apps
- `fields[appCustomProductPageVersions]` (query, optional): the fields to include for returned resources of type appCustomProductPageVersions
- `include` (query, optional): comma-separated list of relationships to include
- `limit[appCustomProductPageVersions]` (query, optional): maximum number of related appCustomProductPageVersions returned (when they are included)

### `PATCH /v1/appCustomProductPages/{id}`
**Summary**: No summary provided.

### `DELETE /v1/appCustomProductPages/{id}`
**Summary**: No summary provided.

### `POST /v1/appEventLocalizations`
**Summary**: No summary provided.

### `GET /v1/appEventLocalizations/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[appEventLocalizations]` (query, optional): the fields to include for returned resources of type appEventLocalizations
- `fields[appEvents]` (query, optional): the fields to include for returned resources of type appEvents
- `fields[appEventScreenshots]` (query, optional): the fields to include for returned resources of type appEventScreenshots
- `fields[appEventVideoClips]` (query, optional): the fields to include for returned resources of type appEventVideoClips
- `include` (query, optional): comma-separated list of relationships to include
- `limit[appEventScreenshots]` (query, optional): maximum number of related appEventScreenshots returned (when they are included)
- `limit[appEventVideoClips]` (query, optional): maximum number of related appEventVideoClips returned (when they are included)

### `PATCH /v1/appEventLocalizations/{id}`
**Summary**: No summary provided.

### `DELETE /v1/appEventLocalizations/{id}`
**Summary**: No summary provided.

### `POST /v1/appInfoLocalizations`
**Summary**: No summary provided.

### `GET /v1/appInfoLocalizations/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[appInfoLocalizations]` (query, optional): the fields to include for returned resources of type appInfoLocalizations
- `fields[appInfos]` (query, optional): the fields to include for returned resources of type appInfos
- `include` (query, optional): comma-separated list of relationships to include

### `PATCH /v1/appInfoLocalizations/{id}`
**Summary**: No summary provided.

### `DELETE /v1/appInfoLocalizations/{id}`
**Summary**: No summary provided.

### `POST /v1/appScreenshots`
**Summary**: No summary provided.

### `GET /v1/appScreenshots/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[appScreenshots]` (query, optional): the fields to include for returned resources of type appScreenshots
- `fields[appScreenshotSets]` (query, optional): the fields to include for returned resources of type appScreenshotSets
- `include` (query, optional): comma-separated list of relationships to include

### `PATCH /v1/appScreenshots/{id}`
**Summary**: No summary provided.

### `DELETE /v1/appScreenshots/{id}`
**Summary**: No summary provided.

### `GET /v1/appCustomProductPages/{id}/relationships/appCustomProductPageVersions`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `GET /v1/appCustomProductPages/{id}/appCustomProductPageVersions`
**Summary**: No summary provided.

**Parameters**:
- `filter[state]` (query, optional): filter by attribute 'state'
- `fields[appCustomProductPageVersions]` (query, optional): the fields to include for returned resources of type appCustomProductPageVersions
- `fields[appCustomProductPages]` (query, optional): the fields to include for returned resources of type appCustomProductPages
- `fields[appCustomProductPageLocalizations]` (query, optional): the fields to include for returned resources of type appCustomProductPageLocalizations
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include
- `limit[appCustomProductPageLocalizations]` (query, optional): maximum number of related appCustomProductPageLocalizations returned (when they are included)

### `GET /v1/appEventLocalizations/{id}/relationships/appEventScreenshots`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `GET /v1/appEventLocalizations/{id}/appEventScreenshots`
**Summary**: No summary provided.

**Parameters**:
- `fields[appEventScreenshots]` (query, optional): the fields to include for returned resources of type appEventScreenshots
- `fields[appEventLocalizations]` (query, optional): the fields to include for returned resources of type appEventLocalizations
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include

### `GET /v1/appEventLocalizations/{id}/relationships/appEventVideoClips`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `GET /v1/appEventLocalizations/{id}/appEventVideoClips`
**Summary**: No summary provided.

**Parameters**:
- `fields[appEventVideoClips]` (query, optional): the fields to include for returned resources of type appEventVideoClips
- `fields[appEventLocalizations]` (query, optional): the fields to include for returned resources of type appEventLocalizations
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include

## Typical Workflows
Use these endpoints to automate app metadata tasks within Apple Store Connect.

## Best Practices
- Always authenticate requests using your Apple Store Connect API key (JWT token).
- Handle rate limiting gracefully, as the Apple Store Connect API enforces quotas.
- When writing integrations, refer back to the exact schemas for precise payload construction.

## App Review metadata audit

- Age Rating answers must declare only controls and features a reviewer can locate and operate in the candidate build. Prefer `None` over a claim that depends on an explanation outside the app.
- Treat every screenshot set as an independent matrix of locale × device family × size × orientation. Audit via App Store Connect's **View All Sizes in Media Manager**; the binary language does not select the metadata locale.
- Screenshots must be captured from the candidate build, not mockups, promotional renders, or Android device chrome. Re-capture every affected slot when the reviewed UI changes.
- `app-store-review` owns the rejection-risk decision; this skill owns the App Store Connect metadata resources and upload operations.
