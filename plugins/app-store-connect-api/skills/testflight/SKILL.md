---
name: "testflight"
description: "Endpoints for managing TestFlight beta testing, builds, and testers."
---

# TestFlight
Endpoints for managing TestFlight beta testing, builds, and testers.

## Endpoints

### `POST /v1/betaAppClipInvocationLocalizations`
**Summary**: No summary provided.

### `PATCH /v1/betaAppClipInvocationLocalizations/{id}`
**Summary**: No summary provided.

### `DELETE /v1/betaAppClipInvocationLocalizations/{id}`
**Summary**: No summary provided.

### `POST /v1/betaAppClipInvocations`
**Summary**: No summary provided.

### `GET /v1/betaAppClipInvocations/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[betaAppClipInvocations]` (query, optional): the fields to include for returned resources of type betaAppClipInvocations
- `fields[betaAppClipInvocationLocalizations]` (query, optional): the fields to include for returned resources of type betaAppClipInvocationLocalizations
- `include` (query, optional): comma-separated list of relationships to include
- `limit[betaAppClipInvocationLocalizations]` (query, optional): maximum number of related betaAppClipInvocationLocalizations returned (when they are included)

### `PATCH /v1/betaAppClipInvocations/{id}`
**Summary**: No summary provided.

### `DELETE /v1/betaAppClipInvocations/{id}`
**Summary**: No summary provided.

### `GET /v1/betaAppLocalizations`
**Summary**: No summary provided.

**Parameters**:
- `filter[locale]` (query, optional): filter by attribute 'locale'
- `filter[app]` (query, optional): filter by id(s) of related 'app'
- `fields[betaAppLocalizations]` (query, optional): the fields to include for returned resources of type betaAppLocalizations
- `fields[apps]` (query, optional): the fields to include for returned resources of type apps
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include

### `POST /v1/betaAppLocalizations`
**Summary**: No summary provided.

### `GET /v1/betaAppLocalizations/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[betaAppLocalizations]` (query, optional): the fields to include for returned resources of type betaAppLocalizations
- `fields[apps]` (query, optional): the fields to include for returned resources of type apps
- `include` (query, optional): comma-separated list of relationships to include

### `PATCH /v1/betaAppLocalizations/{id}`
**Summary**: No summary provided.

### `DELETE /v1/betaAppLocalizations/{id}`
**Summary**: No summary provided.

### `GET /v1/betaAppReviewDetails`
**Summary**: No summary provided.

**Parameters**:
- `filter[app]` (query, required): filter by id(s) of related 'app'
- `fields[betaAppReviewDetails]` (query, optional): the fields to include for returned resources of type betaAppReviewDetails
- `fields[apps]` (query, optional): the fields to include for returned resources of type apps
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include

### `GET /v1/betaAppReviewDetails/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[betaAppReviewDetails]` (query, optional): the fields to include for returned resources of type betaAppReviewDetails
- `fields[apps]` (query, optional): the fields to include for returned resources of type apps
- `include` (query, optional): comma-separated list of relationships to include

### `PATCH /v1/betaAppReviewDetails/{id}`
**Summary**: No summary provided.

### `GET /v1/betaAppReviewSubmissions`
**Summary**: No summary provided.

**Parameters**:
- `filter[betaReviewState]` (query, optional): filter by attribute 'betaReviewState'
- `filter[build]` (query, required): filter by id(s) of related 'build'
- `fields[betaAppReviewSubmissions]` (query, optional): the fields to include for returned resources of type betaAppReviewSubmissions
- `fields[builds]` (query, optional): the fields to include for returned resources of type builds
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include

### `POST /v1/betaAppReviewSubmissions`
**Summary**: No summary provided.

### `GET /v1/betaAppReviewSubmissions/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[betaAppReviewSubmissions]` (query, optional): the fields to include for returned resources of type betaAppReviewSubmissions
- `fields[builds]` (query, optional): the fields to include for returned resources of type builds
- `include` (query, optional): comma-separated list of relationships to include

### `GET /v1/betaBuildLocalizations`
**Summary**: No summary provided.

**Parameters**:
- `filter[locale]` (query, optional): filter by attribute 'locale'
- `filter[build]` (query, optional): filter by id(s) of related 'build'
- `fields[betaBuildLocalizations]` (query, optional): the fields to include for returned resources of type betaBuildLocalizations
- `fields[builds]` (query, optional): the fields to include for returned resources of type builds
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include

### `POST /v1/betaBuildLocalizations`
**Summary**: No summary provided.

### `GET /v1/betaBuildLocalizations/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[betaBuildLocalizations]` (query, optional): the fields to include for returned resources of type betaBuildLocalizations
- `fields[builds]` (query, optional): the fields to include for returned resources of type builds
- `include` (query, optional): comma-separated list of relationships to include

### `PATCH /v1/betaBuildLocalizations/{id}`
**Summary**: No summary provided.

### `DELETE /v1/betaBuildLocalizations/{id}`
**Summary**: No summary provided.

### `GET /v1/betaCrashLogs/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[betaCrashLogs]` (query, optional): the fields to include for returned resources of type betaCrashLogs

### `GET /v1/betaFeedbackCrashSubmissions/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[betaFeedbackCrashSubmissions]` (query, optional): the fields to include for returned resources of type betaFeedbackCrashSubmissions
- `fields[builds]` (query, optional): the fields to include for returned resources of type builds
- `fields[betaTesters]` (query, optional): the fields to include for returned resources of type betaTesters
- `include` (query, optional): comma-separated list of relationships to include

### `DELETE /v1/betaFeedbackCrashSubmissions/{id}`
**Summary**: No summary provided.

### `GET /v1/betaFeedbackScreenshotSubmissions/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[betaFeedbackScreenshotSubmissions]` (query, optional): the fields to include for returned resources of type betaFeedbackScreenshotSubmissions
- `fields[builds]` (query, optional): the fields to include for returned resources of type builds
- `fields[betaTesters]` (query, optional): the fields to include for returned resources of type betaTesters
- `include` (query, optional): comma-separated list of relationships to include

### `DELETE /v1/betaFeedbackScreenshotSubmissions/{id}`
**Summary**: No summary provided.

### `GET /v1/betaGroups`
**Summary**: No summary provided.

**Parameters**:
- `filter[name]` (query, optional): filter by attribute 'name'
- `filter[isInternalGroup]` (query, optional): filter by attribute 'isInternalGroup'
- `filter[publicLinkEnabled]` (query, optional): filter by attribute 'publicLinkEnabled'
- `filter[publicLinkLimitEnabled]` (query, optional): filter by attribute 'publicLinkLimitEnabled'
- `filter[publicLink]` (query, optional): filter by attribute 'publicLink'
- `filter[app]` (query, optional): filter by id(s) of related 'app'
- `filter[builds]` (query, optional): filter by id(s) of related 'builds'
- `filter[id]` (query, optional): filter by id(s)
- `sort` (query, optional): comma-separated list of sort expressions; resources will be sorted as specified
- `fields[betaGroups]` (query, optional): the fields to include for returned resources of type betaGroups
- `fields[apps]` (query, optional): the fields to include for returned resources of type apps
- `fields[builds]` (query, optional): the fields to include for returned resources of type builds
- `fields[betaTesters]` (query, optional): the fields to include for returned resources of type betaTesters
- `fields[betaRecruitmentCriteria]` (query, optional): the fields to include for returned resources of type betaRecruitmentCriteria
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include
- `limit[betaTesters]` (query, optional): maximum number of related betaTesters returned (when they are included)
- `limit[builds]` (query, optional): maximum number of related builds returned (when they are included)

### `POST /v1/betaGroups`
**Summary**: No summary provided.

### `GET /v1/betaGroups/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[betaGroups]` (query, optional): the fields to include for returned resources of type betaGroups
- `fields[apps]` (query, optional): the fields to include for returned resources of type apps
- `fields[builds]` (query, optional): the fields to include for returned resources of type builds
- `fields[betaTesters]` (query, optional): the fields to include for returned resources of type betaTesters
- `fields[betaRecruitmentCriteria]` (query, optional): the fields to include for returned resources of type betaRecruitmentCriteria
- `include` (query, optional): comma-separated list of relationships to include
- `limit[betaTesters]` (query, optional): maximum number of related betaTesters returned (when they are included)
- `limit[builds]` (query, optional): maximum number of related builds returned (when they are included)

### `PATCH /v1/betaGroups/{id}`
**Summary**: No summary provided.

### `DELETE /v1/betaGroups/{id}`
**Summary**: No summary provided.

### `GET /v1/betaLicenseAgreements`
**Summary**: No summary provided.

**Parameters**:
- `filter[app]` (query, optional): filter by id(s) of related 'app'
- `fields[betaLicenseAgreements]` (query, optional): the fields to include for returned resources of type betaLicenseAgreements
- `fields[apps]` (query, optional): the fields to include for returned resources of type apps
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include

### `GET /v1/betaLicenseAgreements/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[betaLicenseAgreements]` (query, optional): the fields to include for returned resources of type betaLicenseAgreements
- `fields[apps]` (query, optional): the fields to include for returned resources of type apps
- `include` (query, optional): comma-separated list of relationships to include

### `PATCH /v1/betaLicenseAgreements/{id}`
**Summary**: No summary provided.

### `POST /v1/betaRecruitmentCriteria`
**Summary**: No summary provided.

### `PATCH /v1/betaRecruitmentCriteria/{id}`
**Summary**: No summary provided.

### `DELETE /v1/betaRecruitmentCriteria/{id}`
**Summary**: No summary provided.

### `GET /v1/betaRecruitmentCriterionOptions`
**Summary**: No summary provided.

**Parameters**:
- `fields[betaRecruitmentCriterionOptions]` (query, optional): the fields to include for returned resources of type betaRecruitmentCriterionOptions
- `limit` (query, optional): maximum resources per page

### `POST /v1/betaTesterInvitations`
**Summary**: No summary provided.

### `GET /v1/betaTesters`
**Summary**: No summary provided.

**Parameters**:
- `filter[firstName]` (query, optional): filter by attribute 'firstName'
- `filter[lastName]` (query, optional): filter by attribute 'lastName'
- `filter[email]` (query, optional): filter by attribute 'email'
- `filter[inviteType]` (query, optional): filter by attribute 'inviteType'
- `filter[apps]` (query, optional): filter by id(s) of related 'apps'
- `filter[betaGroups]` (query, optional): filter by id(s) of related 'betaGroups'
- `filter[builds]` (query, optional): filter by id(s) of related 'builds'
- `filter[id]` (query, optional): filter by id(s)
- `sort` (query, optional): comma-separated list of sort expressions; resources will be sorted as specified
- `fields[betaTesters]` (query, optional): the fields to include for returned resources of type betaTesters
- `fields[apps]` (query, optional): the fields to include for returned resources of type apps
- `fields[betaGroups]` (query, optional): the fields to include for returned resources of type betaGroups
- `fields[builds]` (query, optional): the fields to include for returned resources of type builds
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include
- `limit[apps]` (query, optional): maximum number of related apps returned (when they are included)
- `limit[betaGroups]` (query, optional): maximum number of related betaGroups returned (when they are included)
- `limit[builds]` (query, optional): maximum number of related builds returned (when they are included)

### `POST /v1/betaTesters`
**Summary**: No summary provided.

### `GET /v1/betaTesters/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[betaTesters]` (query, optional): the fields to include for returned resources of type betaTesters
- `fields[apps]` (query, optional): the fields to include for returned resources of type apps
- `fields[betaGroups]` (query, optional): the fields to include for returned resources of type betaGroups
- `fields[builds]` (query, optional): the fields to include for returned resources of type builds
- `include` (query, optional): comma-separated list of relationships to include
- `limit[apps]` (query, optional): maximum number of related apps returned (when they are included)
- `limit[betaGroups]` (query, optional): maximum number of related betaGroups returned (when they are included)
- `limit[builds]` (query, optional): maximum number of related builds returned (when they are included)

### `DELETE /v1/betaTesters/{id}`
**Summary**: No summary provided.

### `GET /v1/buildBetaDetails`
**Summary**: No summary provided.

**Parameters**:
- `filter[build]` (query, optional): filter by id(s) of related 'build'
- `filter[id]` (query, optional): filter by id(s)
- `fields[buildBetaDetails]` (query, optional): the fields to include for returned resources of type buildBetaDetails
- `fields[builds]` (query, optional): the fields to include for returned resources of type builds
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include

### `GET /v1/buildBetaDetails/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[buildBetaDetails]` (query, optional): the fields to include for returned resources of type buildBetaDetails
- `fields[builds]` (query, optional): the fields to include for returned resources of type builds
- `include` (query, optional): comma-separated list of relationships to include

### `PATCH /v1/buildBetaDetails/{id}`
**Summary**: No summary provided.

### `POST /v1/buildBetaNotifications`
**Summary**: No summary provided.

### `POST /v1/buildUploadFiles`
**Summary**: No summary provided.

### `GET /v1/buildUploadFiles/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[buildUploadFiles]` (query, optional): the fields to include for returned resources of type buildUploadFiles

### `PATCH /v1/buildUploadFiles/{id}`
**Summary**: No summary provided.

### `POST /v1/buildUploads`
**Summary**: No summary provided.

### `GET /v1/buildUploads/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[buildUploads]` (query, optional): the fields to include for returned resources of type buildUploads
- `fields[builds]` (query, optional): the fields to include for returned resources of type builds
- `fields[buildUploadFiles]` (query, optional): the fields to include for returned resources of type buildUploadFiles
- `include` (query, optional): comma-separated list of relationships to include

### `DELETE /v1/buildUploads/{id}`
**Summary**: No summary provided.

### `GET /v1/builds`
**Summary**: No summary provided.

**Parameters**:
- `filter[version]` (query, optional): filter by attribute 'version'
- `filter[expired]` (query, optional): filter by attribute 'expired'
- `filter[processingState]` (query, optional): filter by attribute 'processingState'
- `filter[betaAppReviewSubmission.betaReviewState]` (query, optional): filter by attribute 'betaAppReviewSubmission.betaReviewState'
- `filter[usesNonExemptEncryption]` (query, optional): filter by attribute 'usesNonExemptEncryption'
- `filter[preReleaseVersion.version]` (query, optional): filter by attribute 'preReleaseVersion.version'
- `filter[preReleaseVersion.platform]` (query, optional): filter by attribute 'preReleaseVersion.platform'
- `filter[buildAudienceType]` (query, optional): filter by attribute 'buildAudienceType'
- `filter[preReleaseVersion]` (query, optional): filter by id(s) of related 'preReleaseVersion'
- `filter[app]` (query, optional): filter by id(s) of related 'app'
- `filter[betaGroups]` (query, optional): filter by id(s) of related 'betaGroups'
- `filter[appStoreVersion]` (query, optional): filter by id(s) of related 'appStoreVersion'
- `filter[id]` (query, optional): filter by id(s)
- `exists[usesNonExemptEncryption]` (query, optional): filter by attribute 'usesNonExemptEncryption'
- `sort` (query, optional): comma-separated list of sort expressions; resources will be sorted as specified
- `fields[builds]` (query, optional): the fields to include for returned resources of type builds
- `fields[preReleaseVersions]` (query, optional): the fields to include for returned resources of type preReleaseVersions
- `fields[betaTesters]` (query, optional): the fields to include for returned resources of type betaTesters
- `fields[betaGroups]` (query, optional): the fields to include for returned resources of type betaGroups
- `fields[betaBuildLocalizations]` (query, optional): the fields to include for returned resources of type betaBuildLocalizations
- `fields[appEncryptionDeclarations]` (query, optional): the fields to include for returned resources of type appEncryptionDeclarations
- `fields[betaAppReviewSubmissions]` (query, optional): the fields to include for returned resources of type betaAppReviewSubmissions
- `fields[apps]` (query, optional): the fields to include for returned resources of type apps
- `fields[buildBetaDetails]` (query, optional): the fields to include for returned resources of type buildBetaDetails
- `fields[appStoreVersions]` (query, optional): the fields to include for returned resources of type appStoreVersions
- `fields[buildIcons]` (query, optional): the fields to include for returned resources of type buildIcons
- `fields[buildBundles]` (query, optional): the fields to include for returned resources of type buildBundles
- `fields[buildUploads]` (query, optional): the fields to include for returned resources of type buildUploads
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include
- `limit[betaBuildLocalizations]` (query, optional): maximum number of related betaBuildLocalizations returned (when they are included)
- `limit[betaGroups]` (query, optional): maximum number of related betaGroups returned (when they are included)
- `limit[buildBundles]` (query, optional): maximum number of related buildBundles returned (when they are included)
- `limit[icons]` (query, optional): maximum number of related icons returned (when they are included)
- `limit[individualTesters]` (query, optional): maximum number of related individualTesters returned (when they are included)

### `GET /v1/builds/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[builds]` (query, optional): the fields to include for returned resources of type builds
- `fields[preReleaseVersions]` (query, optional): the fields to include for returned resources of type preReleaseVersions
- `fields[betaTesters]` (query, optional): the fields to include for returned resources of type betaTesters
- `fields[betaGroups]` (query, optional): the fields to include for returned resources of type betaGroups
- `fields[betaBuildLocalizations]` (query, optional): the fields to include for returned resources of type betaBuildLocalizations
- `fields[appEncryptionDeclarations]` (query, optional): the fields to include for returned resources of type appEncryptionDeclarations
- `fields[betaAppReviewSubmissions]` (query, optional): the fields to include for returned resources of type betaAppReviewSubmissions
- `fields[apps]` (query, optional): the fields to include for returned resources of type apps
- `fields[buildBetaDetails]` (query, optional): the fields to include for returned resources of type buildBetaDetails
- `fields[appStoreVersions]` (query, optional): the fields to include for returned resources of type appStoreVersions
- `fields[buildIcons]` (query, optional): the fields to include for returned resources of type buildIcons
- `fields[buildBundles]` (query, optional): the fields to include for returned resources of type buildBundles
- `fields[buildUploads]` (query, optional): the fields to include for returned resources of type buildUploads
- `include` (query, optional): comma-separated list of relationships to include
- `limit[betaBuildLocalizations]` (query, optional): maximum number of related betaBuildLocalizations returned (when they are included)
- `limit[betaGroups]` (query, optional): maximum number of related betaGroups returned (when they are included)
- `limit[buildBundles]` (query, optional): maximum number of related buildBundles returned (when they are included)
- `limit[icons]` (query, optional): maximum number of related icons returned (when they are included)
- `limit[individualTesters]` (query, optional): maximum number of related individualTesters returned (when they are included)

### `PATCH /v1/builds/{id}`
**Summary**: No summary provided.

### `GET /v1/preReleaseVersions`
**Summary**: No summary provided.

**Parameters**:
- `filter[builds.buildAudienceType]` (query, optional): filter by attribute 'builds.buildAudienceType'
- `filter[builds.expired]` (query, optional): filter by attribute 'builds.expired'
- `filter[builds.processingState]` (query, optional): filter by attribute 'builds.processingState'
- `filter[builds.version]` (query, optional): filter by attribute 'builds.version'
- `filter[platform]` (query, optional): filter by attribute 'platform'
- `filter[version]` (query, optional): filter by attribute 'version'
- `filter[app]` (query, optional): filter by id(s) of related 'app'
- `filter[builds]` (query, optional): filter by id(s) of related 'builds'
- `sort` (query, optional): comma-separated list of sort expressions; resources will be sorted as specified
- `fields[preReleaseVersions]` (query, optional): the fields to include for returned resources of type preReleaseVersions
- `fields[builds]` (query, optional): the fields to include for returned resources of type builds
- `fields[apps]` (query, optional): the fields to include for returned resources of type apps
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include
- `limit[builds]` (query, optional): maximum number of related builds returned (when they are included)

### `GET /v1/preReleaseVersions/{id}`
**Summary**: No summary provided.

**Parameters**:
- `fields[preReleaseVersions]` (query, optional): the fields to include for returned resources of type preReleaseVersions
- `fields[builds]` (query, optional): the fields to include for returned resources of type builds
- `fields[apps]` (query, optional): the fields to include for returned resources of type apps
- `include` (query, optional): comma-separated list of relationships to include
- `limit[builds]` (query, optional): maximum number of related builds returned (when they are included)

### `GET /v1/betaAppLocalizations/{id}/relationships/app`
**Summary**: No summary provided.

### `GET /v1/betaAppLocalizations/{id}/app`
**Summary**: No summary provided.

**Parameters**:
- `fields[apps]` (query, optional): the fields to include for returned resources of type apps

### `GET /v1/betaAppReviewDetails/{id}/relationships/app`
**Summary**: No summary provided.

### `GET /v1/betaAppReviewDetails/{id}/app`
**Summary**: No summary provided.

**Parameters**:
- `fields[apps]` (query, optional): the fields to include for returned resources of type apps

### `GET /v1/betaAppReviewSubmissions/{id}/relationships/build`
**Summary**: No summary provided.

### `GET /v1/betaAppReviewSubmissions/{id}/build`
**Summary**: No summary provided.

**Parameters**:
- `fields[builds]` (query, optional): the fields to include for returned resources of type builds

### `GET /v1/betaBuildLocalizations/{id}/relationships/build`
**Summary**: No summary provided.

### `GET /v1/betaBuildLocalizations/{id}/build`
**Summary**: No summary provided.

**Parameters**:
- `fields[builds]` (query, optional): the fields to include for returned resources of type builds

### `GET /v1/betaFeedbackCrashSubmissions/{id}/relationships/crashLog`
**Summary**: No summary provided.

### `GET /v1/betaFeedbackCrashSubmissions/{id}/crashLog`
**Summary**: No summary provided.

**Parameters**:
- `fields[betaCrashLogs]` (query, optional): the fields to include for returned resources of type betaCrashLogs

### `GET /v1/betaGroups/{id}/relationships/app`
**Summary**: No summary provided.

### `GET /v1/betaGroups/{id}/app`
**Summary**: No summary provided.

**Parameters**:
- `fields[apps]` (query, optional): the fields to include for returned resources of type apps

### `GET /v1/betaGroups/{id}/relationships/betaRecruitmentCriteria`
**Summary**: No summary provided.

### `GET /v1/betaGroups/{id}/betaRecruitmentCriteria`
**Summary**: No summary provided.

**Parameters**:
- `fields[betaRecruitmentCriteria]` (query, optional): the fields to include for returned resources of type betaRecruitmentCriteria

### `GET /v1/betaGroups/{id}/relationships/betaRecruitmentCriterionCompatibleBuildCheck`
**Summary**: No summary provided.

### `GET /v1/betaGroups/{id}/betaRecruitmentCriterionCompatibleBuildCheck`
**Summary**: No summary provided.

**Parameters**:
- `fields[betaRecruitmentCriterionCompatibleBuildChecks]` (query, optional): the fields to include for returned resources of type betaRecruitmentCriterionCompatibleBuildChecks

### `GET /v1/betaGroups/{id}/relationships/betaTesters`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `POST /v1/betaGroups/{id}/relationships/betaTesters`
**Summary**: No summary provided.

### `DELETE /v1/betaGroups/{id}/relationships/betaTesters`
**Summary**: No summary provided.

### `GET /v1/betaGroups/{id}/betaTesters`
**Summary**: No summary provided.

**Parameters**:
- `fields[betaTesters]` (query, optional): the fields to include for returned resources of type betaTesters
- `limit` (query, optional): maximum resources per page

### `GET /v1/betaGroups/{id}/relationships/builds`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `POST /v1/betaGroups/{id}/relationships/builds`
**Summary**: No summary provided.

### `DELETE /v1/betaGroups/{id}/relationships/builds`
**Summary**: No summary provided.

### `GET /v1/betaGroups/{id}/builds`
**Summary**: No summary provided.

**Parameters**:
- `fields[builds]` (query, optional): the fields to include for returned resources of type builds
- `limit` (query, optional): maximum resources per page

### `GET /v1/betaLicenseAgreements/{id}/relationships/app`
**Summary**: No summary provided.

### `GET /v1/betaLicenseAgreements/{id}/app`
**Summary**: No summary provided.

**Parameters**:
- `fields[apps]` (query, optional): the fields to include for returned resources of type apps

### `GET /v1/betaTesters/{id}/relationships/apps`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `DELETE /v1/betaTesters/{id}/relationships/apps`
**Summary**: No summary provided.

### `GET /v1/betaTesters/{id}/apps`
**Summary**: No summary provided.

**Parameters**:
- `fields[apps]` (query, optional): the fields to include for returned resources of type apps
- `limit` (query, optional): maximum resources per page

### `GET /v1/betaTesters/{id}/relationships/betaGroups`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `POST /v1/betaTesters/{id}/relationships/betaGroups`
**Summary**: No summary provided.

### `DELETE /v1/betaTesters/{id}/relationships/betaGroups`
**Summary**: No summary provided.

### `GET /v1/betaTesters/{id}/betaGroups`
**Summary**: No summary provided.

**Parameters**:
- `fields[betaGroups]` (query, optional): the fields to include for returned resources of type betaGroups
- `limit` (query, optional): maximum resources per page

### `GET /v1/betaTesters/{id}/relationships/builds`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `POST /v1/betaTesters/{id}/relationships/builds`
**Summary**: No summary provided.

### `DELETE /v1/betaTesters/{id}/relationships/builds`
**Summary**: No summary provided.

### `GET /v1/betaTesters/{id}/builds`
**Summary**: No summary provided.

**Parameters**:
- `fields[builds]` (query, optional): the fields to include for returned resources of type builds
- `limit` (query, optional): maximum resources per page

### `GET /v1/buildBetaDetails/{id}/relationships/build`
**Summary**: No summary provided.

### `GET /v1/buildBetaDetails/{id}/build`
**Summary**: No summary provided.

**Parameters**:
- `fields[builds]` (query, optional): the fields to include for returned resources of type builds
- `fields[preReleaseVersions]` (query, optional): the fields to include for returned resources of type preReleaseVersions
- `fields[betaTesters]` (query, optional): the fields to include for returned resources of type betaTesters
- `fields[betaGroups]` (query, optional): the fields to include for returned resources of type betaGroups
- `fields[betaBuildLocalizations]` (query, optional): the fields to include for returned resources of type betaBuildLocalizations
- `fields[appEncryptionDeclarations]` (query, optional): the fields to include for returned resources of type appEncryptionDeclarations
- `fields[betaAppReviewSubmissions]` (query, optional): the fields to include for returned resources of type betaAppReviewSubmissions
- `fields[apps]` (query, optional): the fields to include for returned resources of type apps
- `fields[buildBetaDetails]` (query, optional): the fields to include for returned resources of type buildBetaDetails
- `fields[appStoreVersions]` (query, optional): the fields to include for returned resources of type appStoreVersions
- `fields[buildIcons]` (query, optional): the fields to include for returned resources of type buildIcons
- `fields[buildBundles]` (query, optional): the fields to include for returned resources of type buildBundles
- `fields[buildUploads]` (query, optional): the fields to include for returned resources of type buildUploads
- `include` (query, optional): comma-separated list of relationships to include
- `limit[individualTesters]` (query, optional): maximum number of related individualTesters returned (when they are included)
- `limit[betaGroups]` (query, optional): maximum number of related betaGroups returned (when they are included)
- `limit[betaBuildLocalizations]` (query, optional): maximum number of related betaBuildLocalizations returned (when they are included)
- `limit[icons]` (query, optional): maximum number of related icons returned (when they are included)
- `limit[buildBundles]` (query, optional): maximum number of related buildBundles returned (when they are included)

### `GET /v1/buildBundles/{id}/relationships/appClipDomainCacheStatus`
**Summary**: No summary provided.

### `GET /v1/buildBundles/{id}/appClipDomainCacheStatus`
**Summary**: No summary provided.

**Parameters**:
- `fields[appClipDomainStatuses]` (query, optional): the fields to include for returned resources of type appClipDomainStatuses

### `GET /v1/buildBundles/{id}/relationships/appClipDomainDebugStatus`
**Summary**: No summary provided.

### `GET /v1/buildBundles/{id}/appClipDomainDebugStatus`
**Summary**: No summary provided.

**Parameters**:
- `fields[appClipDomainStatuses]` (query, optional): the fields to include for returned resources of type appClipDomainStatuses

### `GET /v1/buildBundles/{id}/relationships/betaAppClipInvocations`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `GET /v1/buildBundles/{id}/betaAppClipInvocations`
**Summary**: No summary provided.

**Parameters**:
- `fields[betaAppClipInvocations]` (query, optional): the fields to include for returned resources of type betaAppClipInvocations
- `fields[betaAppClipInvocationLocalizations]` (query, optional): the fields to include for returned resources of type betaAppClipInvocationLocalizations
- `limit` (query, optional): maximum resources per page
- `include` (query, optional): comma-separated list of relationships to include
- `limit[betaAppClipInvocationLocalizations]` (query, optional): maximum number of related betaAppClipInvocationLocalizations returned (when they are included)

### `GET /v1/buildBundles/{id}/relationships/buildBundleFileSizes`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `GET /v1/buildBundles/{id}/buildBundleFileSizes`
**Summary**: No summary provided.

**Parameters**:
- `fields[buildBundleFileSizes]` (query, optional): the fields to include for returned resources of type buildBundleFileSizes
- `limit` (query, optional): maximum resources per page

### `GET /v1/buildUploads/{id}/relationships/buildUploadFiles`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `GET /v1/buildUploads/{id}/buildUploadFiles`
**Summary**: No summary provided.

**Parameters**:
- `fields[buildUploadFiles]` (query, optional): the fields to include for returned resources of type buildUploadFiles
- `limit` (query, optional): maximum resources per page

### `GET /v1/builds/{id}/relationships/app`
**Summary**: No summary provided.

### `GET /v1/builds/{id}/app`
**Summary**: No summary provided.

**Parameters**:
- `fields[apps]` (query, optional): the fields to include for returned resources of type apps

### `GET /v1/builds/{id}/relationships/appEncryptionDeclaration`
**Summary**: No summary provided.

### `PATCH /v1/builds/{id}/relationships/appEncryptionDeclaration`
**Summary**: No summary provided.

### `GET /v1/builds/{id}/appEncryptionDeclaration`
**Summary**: No summary provided.

**Parameters**:
- `fields[appEncryptionDeclarations]` (query, optional): the fields to include for returned resources of type appEncryptionDeclarations

### `GET /v1/builds/{id}/relationships/appStoreVersion`
**Summary**: No summary provided.

### `GET /v1/builds/{id}/appStoreVersion`
**Summary**: No summary provided.

**Parameters**:
- `fields[appStoreVersions]` (query, optional): the fields to include for returned resources of type appStoreVersions
- `fields[apps]` (query, optional): the fields to include for returned resources of type apps
- `fields[appStoreVersionLocalizations]` (query, optional): the fields to include for returned resources of type appStoreVersionLocalizations
- `fields[builds]` (query, optional): the fields to include for returned resources of type builds
- `fields[appStoreVersionPhasedReleases]` (query, optional): the fields to include for returned resources of type appStoreVersionPhasedReleases
- `fields[gameCenterAppVersions]` (query, optional): the fields to include for returned resources of type gameCenterAppVersions
- `fields[routingAppCoverages]` (query, optional): the fields to include for returned resources of type routingAppCoverages
- `fields[appStoreReviewDetails]` (query, optional): the fields to include for returned resources of type appStoreReviewDetails
- `fields[appStoreVersionSubmissions]` (query, optional): the fields to include for returned resources of type appStoreVersionSubmissions
- `fields[appClipDefaultExperiences]` (query, optional): the fields to include for returned resources of type appClipDefaultExperiences
- `fields[appStoreVersionExperiments]` (query, optional): the fields to include for returned resources of type appStoreVersionExperiments
- `fields[alternativeDistributionPackages]` (query, optional): the fields to include for returned resources of type alternativeDistributionPackages
- `include` (query, optional): comma-separated list of relationships to include
- `limit[appStoreVersionLocalizations]` (query, optional): maximum number of related appStoreVersionLocalizations returned (when they are included)
- `limit[appStoreVersionExperiments]` (query, optional): maximum number of related appStoreVersionExperiments returned (when they are included)
- `limit[appStoreVersionExperimentsV2]` (query, optional): maximum number of related appStoreVersionExperimentsV2 returned (when they are included)

### `GET /v1/builds/{id}/relationships/betaAppReviewSubmission`
**Summary**: No summary provided.

### `GET /v1/builds/{id}/betaAppReviewSubmission`
**Summary**: No summary provided.

**Parameters**:
- `fields[betaAppReviewSubmissions]` (query, optional): the fields to include for returned resources of type betaAppReviewSubmissions

### `GET /v1/builds/{id}/relationships/betaBuildLocalizations`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `GET /v1/builds/{id}/betaBuildLocalizations`
**Summary**: No summary provided.

**Parameters**:
- `fields[betaBuildLocalizations]` (query, optional): the fields to include for returned resources of type betaBuildLocalizations
- `limit` (query, optional): maximum resources per page

### `POST /v1/builds/{id}/relationships/betaGroups`
**Summary**: No summary provided.

### `DELETE /v1/builds/{id}/relationships/betaGroups`
**Summary**: No summary provided.

### `GET /v1/builds/{id}/relationships/buildBetaDetail`
**Summary**: No summary provided.

### `GET /v1/builds/{id}/buildBetaDetail`
**Summary**: No summary provided.

**Parameters**:
- `fields[buildBetaDetails]` (query, optional): the fields to include for returned resources of type buildBetaDetails
- `fields[builds]` (query, optional): the fields to include for returned resources of type builds
- `include` (query, optional): comma-separated list of relationships to include

### `GET /v1/builds/{id}/relationships/diagnosticSignatures`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `GET /v1/builds/{id}/diagnosticSignatures`
**Summary**: No summary provided.

**Parameters**:
- `filter[diagnosticType]` (query, optional): filter by attribute 'diagnosticType'
- `fields[diagnosticSignatures]` (query, optional): the fields to include for returned resources of type diagnosticSignatures
- `limit` (query, optional): maximum resources per page

### `GET /v1/builds/{id}/relationships/icons`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `GET /v1/builds/{id}/icons`
**Summary**: No summary provided.

**Parameters**:
- `fields[buildIcons]` (query, optional): the fields to include for returned resources of type buildIcons
- `limit` (query, optional): maximum resources per page

### `GET /v1/builds/{id}/relationships/individualTesters`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `POST /v1/builds/{id}/relationships/individualTesters`
**Summary**: No summary provided.

### `DELETE /v1/builds/{id}/relationships/individualTesters`
**Summary**: No summary provided.

### `GET /v1/builds/{id}/individualTesters`
**Summary**: No summary provided.

**Parameters**:
- `fields[betaTesters]` (query, optional): the fields to include for returned resources of type betaTesters
- `limit` (query, optional): maximum resources per page

### `GET /v1/builds/{id}/perfPowerMetrics`
**Summary**: No summary provided.

**Parameters**:
- `filter[platform]` (query, optional): filter by attribute 'platform'
- `filter[metricType]` (query, optional): filter by attribute 'metricType'
- `filter[deviceType]` (query, optional): filter by attribute 'deviceType'

### `GET /v1/builds/{id}/relationships/preReleaseVersion`
**Summary**: No summary provided.

### `GET /v1/builds/{id}/preReleaseVersion`
**Summary**: No summary provided.

**Parameters**:
- `fields[preReleaseVersions]` (query, optional): the fields to include for returned resources of type preReleaseVersions

### `GET /v1/preReleaseVersions/{id}/relationships/app`
**Summary**: No summary provided.

### `GET /v1/preReleaseVersions/{id}/app`
**Summary**: No summary provided.

**Parameters**:
- `fields[apps]` (query, optional): the fields to include for returned resources of type apps

### `GET /v1/preReleaseVersions/{id}/relationships/builds`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum resources per page

### `GET /v1/preReleaseVersions/{id}/builds`
**Summary**: No summary provided.

**Parameters**:
- `fields[builds]` (query, optional): the fields to include for returned resources of type builds
- `limit` (query, optional): maximum resources per page

### `GET /v1/betaGroups/{id}/metrics/betaTesterUsages`
**Summary**: No summary provided.

**Parameters**:
- `period` (query, optional): the duration of the reporting period
- `groupBy` (query, optional): the dimension by which to group the results
- `filter[betaTesters]` (query, optional): filter by 'betaTesters' relationship dimension
- `limit` (query, optional): maximum number of groups to return per page

### `GET /v1/betaGroups/{id}/metrics/publicLinkUsages`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum number of groups to return per page

### `GET /v1/betaTesters/{id}/metrics/betaTesterUsages`
**Summary**: No summary provided.

**Parameters**:
- `period` (query, optional): the duration of the reporting period
- `filter[apps]` (query, required): filter by 'apps' relationship dimension
- `limit` (query, optional): maximum number of groups to return per page

### `GET /v1/builds/{id}/metrics/betaBuildUsages`
**Summary**: No summary provided.

**Parameters**:
- `limit` (query, optional): maximum number of groups to return per page

## Typical Workflows
Use these endpoints to automate testflight tasks within Apple Store Connect.

## Best Practices
- Always authenticate requests using your Apple Store Connect API key (JWT token).
- Handle rate limiting gracefully, as the Apple Store Connect API enforces quotas.
- When writing integrations, refer back to the exact schemas for precise payload construction.

## Build and submission state model

Keep these states distinct when auditing a candidate for App Review:

1. The cloud build finished and has a processed build number.
2. The submit process completed for that build.
3. The build is attached to the target App Store version.
4. `Update Review` was submitted.

Use the build and App Store Version relationships to verify each transition; an EAS `finished` status proves only the first state. Before the fourth state, verify the build number is monotonic and single-use, the fix commit is an ancestor of the build revision, and the lockfile passes `npm ci` on the CI Node major. Stop before `Update Review` for explicit account-owner confirmation. See `app-store-review` for the complete rejection-prevention checklist.
