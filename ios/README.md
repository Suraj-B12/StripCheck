# StripCheck for iPhone and iPad

A native SwiftUI client for the same local StripCheck API used by the website. It targets iOS 17 and later, with system material surfaces, readable Dynamic Type, VoiceOver labels, and reduced-motion-aware transitions. No third-party iOS libraries or cloud APIs are used.

## Open and run

1. Open `StripCheck.xcodeproj` in Xcode 15 or later with an iOS 17+ SDK.
2. Select the **StripCheck** scheme and an iPhone simulator, then Run.
3. Start the Python server from the repository root: `.venv/bin/python cli.py serve`.
4. In the simulator, open the app’s connection settings and use `http://localhost:8000`.

The Python environment and backend dependencies must be installed first; follow [the repository setup instructions](../README.md#first-setup-on-a-fresh-clone). Real pack checks need the official alert lists loaded on that server. Synthetic examples work without downloaded alert data. The server must remain running while the app checks a pack. Use the actual configured port if it differs from 8000.

For a physical iPhone, start the server with `--lan`, keep the phone and computer on the same trusted Wi-Fi, and enter the host address shown by the website’s phone-pairing screen. If pairing is protected, enter its token separately. Allow the system’s Local Network prompt. `localhost` on an iPhone refers to the phone, not the computer.

Running on a physical device requires selecting your own development team in Xcode Signing & Capabilities. This repository does not contain signing credentials or a distribution profile. No account has been used and no app has been submitted or installed on a device during this implementation.

## Included flows

- Camera and Photos picker with preview, image resizing and an explicit upload button.
- Typed pack details, 11 synthetic demonstrations, all confirmation questions, carton-photo continuation, and resumable checks.
- Server-authored verdicts and source citations; the client never generates a medicine verdict.
- Alert search and pagination, saved-pack cabinet, delete and recheck, and recent activity.
- JSON content negotiation, request timeouts, cancellation, readable server errors and empty states.
- Backend address in app-only preferences, pairing token in Keychain, last opened check cached with iOS file protection. Photos are not cached by the app. Uploaded photos and check history remain in the selected server’s local data until removed there; automatic retention cleanup is not implemented. Deleting a cabinet entry does not delete its original photo or check.

The app requires its configured server for checks. It can display the last cached check while disconnected. Demo data remains explicitly synthetic. The native client does not sync CDSCO lists itself; use the website or CLI to manage the server’s data.

## Validation

The API models/client are also a standalone Swift package. Run:

```sh
swift run --package-path ios StripCheckVerify
swift test --package-path ios
```

`StripCheckVerify` executes 14 compiled checks covering snapshot/citation decoding, local address restrictions, JSON negotiation, pairing headers, multipart upload, resume routes, query encoding, typed-field payloads, bounded image downsampling, corrupt/oversized images, redirect refusal, HTTP errors, malformed responses, and cancellation. The XCTest suite adds nine focused model, route, address and image tests for a full Xcode installation.

On the implementation machine, only Command Line Tools were installed. The package library and executable compiled, and all 14 executable checks passed. A live native URLSession round-trip also passed against the local server: health, all 11 synthetic demo definitions, batch confirmation and resumed verdict, cabinet save/read/delete, activity, and alert decoding. Set `STRIPCHECK_TEST_SERVER=http://127.0.0.1:8000` when running `StripCheckVerify` to repeat that optional check; it creates a synthetic check and removes its temporary cabinet item.

The SwiftUI files passed a syntax parse; the Xcode project, Info.plist and privacy manifest passed `plutil` validation. [Hosted verification](https://github.com/Suraj-B12/StripCheck/actions/runs/40449407179) subsequently passed all 14 executable checks, all nine XCTest cases and a complete unsigned simulator build with Xcode 16.4 and the iOS 18.5 SDK. The build emitted an App Intents metadata notice because the app has no App Intents dependency. **Simulator interaction, camera permission tests, VoiceOver interaction and device signing remain unverified.** Local Command Line Tools cannot run XCTest; hosted checks do not substitute for those device validations.

For a simulator build on a machine with Xcode:

```sh
xcodebuild -project ios/StripCheck.xcodeproj -scheme StripCheck \
  -sdk iphonesimulator -destination 'generic/platform=iOS Simulator' \
  CODE_SIGNING_ALLOWED=NO build
```

The project can be regenerated deterministically with `python3 ios/generate_project.py` after changes to the source list. Its `.xcodeproj` is already included, so generation is not required to open it.

## Privacy and network configuration

The app requests Camera and Local Network access only for their described functions. The Photos picker grants access only to selected images. Selected photos are downsampled to at most 2400 pixels before preview and upload; new JPEGs omit the original metadata. The token is transmitted in `X-StripCheck-Key`, never as a query parameter. HTTP is accepted only for local addresses; HTTPS is accepted for a configured server. Redirects are refused, and the app does not disable certificate validation. `NSAllowsLocalNetworking` declares local connection intent; there is no blanket ATS exemption. Apple documents this key’s scope in [NSAllowsLocalNetworking](https://developer.apple.com/documentation/bundleresources/information-property-list/nsapptransportsecurity/nsallowslocalnetworking).

`PrivacyInfo.xcprivacy` declares no tracking, and declares app-only UserDefaults use with reason `CA92.1`. Review the manifest against your actual hosting and release practices before distribution; refer to [Apple’s required-reason API documentation](https://developer.apple.com/documentation/bundleresources/app-privacy-configuration/nsprivacyaccessedapitypes/nsprivacyaccessedapitype). Interface copy and verdicts are English; other languages require reviewed translations.
