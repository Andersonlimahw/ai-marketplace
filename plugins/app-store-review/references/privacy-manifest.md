# Privacy Manifest Reference

## Contents
- When a Privacy Manifest Is Required
- Privacy Manifest Structure
- Required API Reason Codes
- Privacy Manifest Keys Reference
- Third-Party SDK Manifests
- Collected Data Types Declaration
- Sources To Re-Check

## When a Privacy Manifest Is Required

A `PrivacyInfo.xcprivacy` file is required if your app or any dependency uses these API categories:

- File timestamp APIs (`NSPrivacyAccessedAPICategoryFileTimestamp`)
- System boot time APIs (`NSPrivacyAccessedAPICategorySystemBootTime`)
- Disk space APIs (`NSPrivacyAccessedAPICategoryDiskSpace`)
- User defaults (`NSPrivacyAccessedAPICategoryUserDefaults`)
- Active keyboard APIs (`NSPrivacyAccessedAPICategoryActiveKeyboards`)

Apple updates required-reason API coverage over time. Before final submission or release, re-check the current `NSPrivacyAccessedAPIType` and `NSPrivacyAccessedAPITypeReasons` documentation and do not invent broad or convenient reasons.

## Privacy Manifest Structure

```xml
<!-- PrivacyInfo.xcprivacy -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>NSPrivacyTracking</key>
    <false/>
    <key>NSPrivacyTrackingDomains</key>
    <array/>
    <key>NSPrivacyCollectedDataTypes</key>
    <array>
        <!-- Declare every data type you collect -->
    </array>
    <key>NSPrivacyAccessedAPITypes</key>
    <array>
        <dict>
            <key>NSPrivacyAccessedAPIType</key>
            <string>NSPrivacyAccessedAPICategoryUserDefaults</string>
            <key>NSPrivacyAccessedAPITypeReasons</key>
            <array>
                <string>CA92.1</string>
            </array>
        </dict>
    </array>
</dict>
</plist>
```

## Required API Reason Codes

Use the exact approved reason that matches the app or SDK behavior. Do not use a broad reason code because it is convenient; Apple requires the declared reason to match the presented functionality and derived-data use.

Before final submission, re-check Apple's current required-reason API documentation. Reason-code coverage can change, and invented or overly broad reasons are not acceptable.

| API Category | Code | Reason |
|---|---|---|
| FileTimestamp | `DDA9.1` | Display file timestamps to the person using the device |
| FileTimestamp | `C617.1` | Access timestamps, size, or metadata for files in the app, app group, or CloudKit container |
| FileTimestamp | `3B52.1` | Access timestamps, size, or metadata for user-granted files or directories |
| FileTimestamp | `0A2A.1` | Third-party SDK wrapper around file timestamp APIs, only when called by the app |
| SystemBootTime | `35F9.1` | Measure elapsed time between events |
| SystemBootTime | `8FFB.1` | Calculate absolute timestamps for events that occurred within the app |
| SystemBootTime | `3D61.1` | Include system boot time in an optional user-submitted bug report |
| DiskSpace | `85F4.1` | Display disk space information to the person using the device |
| DiskSpace | `E174.1` | Check available or low disk space before writes or cleanup |
| DiskSpace | `7D9E.1` | Include disk space information in an optional user-submitted bug report |
| DiskSpace | `B728.1` | Health research app detects low disk space impacting research data collection |
| ActiveKeyboards | `3EC4.1` | Custom keyboard app checks active keyboards |
| ActiveKeyboards | `54BD.1` | Present UI that visibly changes based on active keyboards |
| UserDefaults | `CA92.1` | Read/write information accessible only to the app itself |
| UserDefaults | `1C8F.1` | Read/write information accessible only within the same App Group |
| UserDefaults | `C56D.1` | Third-party SDK wrapper around UserDefaults APIs, only when called by the app |
| UserDefaults | `AC6B.1` | Managed app configuration or managed feedback keys for MDM |

## Privacy Manifest Keys Reference

| Key | Type | Purpose |
|---|---|---|
| `NSPrivacyTracking` | Boolean | Whether the app tracks users (triggers ATT requirement) |
| `NSPrivacyTrackingDomains` | Array of strings | Domains used for tracking (connected only after ATT consent) |
| `NSPrivacyCollectedDataTypes` | Array of dicts | Each data type collected, its purpose, and whether it is linked to identity |
| `NSPrivacyAccessedAPITypes` | Array of dicts | Each required-reason API used and the justification codes |

## Third-Party SDK Manifests

- Verify each SDK, executable, or dynamic library that uses required-reason APIs includes `PrivacyInfo.xcprivacy` in the bundle containing that code
- Ensure SDK reason codes match actual SDK usage; an SDK cannot rely on the host app's manifest to report the SDK's own required-reason API use
- Update SDK versions when required manifests or reason declarations are missing
- Keep the app's manifest focused on app code and app-level collected data/tracking declarations

## Collected Data Types Declaration

Each `NSPrivacyCollectedDataTypes` entry must specify:

- `NSPrivacyCollectedDataType` (category)
- `NSPrivacyCollectedDataTypeLinked` (linked to identity)
- `NSPrivacyCollectedDataTypeTracking` (used for tracking)
- `NSPrivacyCollectedDataTypePurposes` (purposes array)

Keep manifests, privacy nutrition labels, SDK behavior, and app functionality consistent. Mismatches cause rejection.

## Sources To Re-Check

- Required-reason API overview: https://sosumi.ai/documentation/bundleresources/describing-use-of-required-reason-api
- Required-reason API categories: https://sosumi.ai/documentation/bundleresources/app-privacy-configuration/nsprivacyaccessedapitypes/nsprivacyaccessedapitype
- Required-reason codes: https://sosumi.ai/documentation/bundleresources/app-privacy-configuration/nsprivacyaccessedapitypes/nsprivacyaccessedapitypereasons
