# Build and Notarize the Tracker on macOS

This document describes how to test, build, sign, package, and notarize the GestureCap OSC tracker from source.

The published `gesturecap-tracker-macos-arm64.zip` asset is currently built for macOS Apple Silicon (`arm64`). An Intel release requires an x86_64 Python environment and a separate build, test, notarization, and release asset.

---

## Requirements

For the reproducible Apple Silicon release workflow, install:

- macOS on Apple Silicon
- Python 3.10.12
- Git
- `uv`
- PyInstaller 6.21.0
- current Xcode command-line tools

Public distribution additionally requires:

- an active Apple Developer Program membership
- a valid **Developer ID Application** certificate in Keychain Access
- two-factor authentication and an app-specific password, or an App Store Connect API key

The certificate identity and credentials must remain local. Never write them into the repository or the PyInstaller specification.

---

## Clone and Prepare the Environment

```bash
git clone https://github.com/mikaelmolliex/gesturecap-osc.git
cd gesturecap-osc

uv venv --python 3.10.12
uv pip install --no-deps -r requirements.txt
uv pip install pyinstaller==6.21.0
```

Verify the environment:

```bash
.venv/bin/python --version
.venv/bin/python -m PyInstaller --version
.venv/bin/python -c "import utils.no_matplotlib, cv2, mediapipe, pythonosc; print('Dependencies: OK')"
```

`requirements.txt` is the complete, pinned list of what the tracker needs. `--no-deps` keeps out the packages MediaPipe 0.10.14 declares but the tracker never uses (jax, jaxlib, matplotlib, sounddevice, and a second OpenCV). `utils/no_matplotlib.py` must be imported before `mediapipe`, as `utils/hand_pose_detector.py` does.

Calling `.venv/bin/python` directly also avoids activation-path problems if a virtual environment was created before the project directory was moved.

---

## Test the Python Tracker First

```bash
.venv/bin/python doublehand_mp.py
```

Expected behavior:

- the webcam opens
- MediaPipe initializes
- hand landmarks are detected
- OSC data is sent to `127.0.0.1:11111`

Stop the tracker with `Ctrl+C`. Do not create a release build until the source version works correctly.

---

## Unsigned Test Builds

Sign only a tracker that is known to work and to be portable. Until then, build an unsigned (ad-hoc) test version, and never release it:

```bash
GESTURECAP_UNSIGNED_TEST_BUILD=1 .venv/bin/python -m PyInstaller \
  --clean \
  --noconfirm \
  --workpath /private/tmp/gesturecap-test-work \
  --distpath /private/tmp/gesturecap-test-dist \
  doublehand_mp.spec
```

Without this variable, `doublehand_mp.spec` requires a signing identity.

---

## Configure the Signing Identity

List the available code-signing identities:

```bash
security find-identity -v -p codesigning
```

Set the Developer ID identity only in the current Terminal session:

```bash
export GESTURECAP_CODESIGN_IDENTITY="Developer ID Application: YOUR NAME (YOUR_TEAM_ID)"
```

`doublehand_mp.spec` reads this variable locally and deliberately fails when it is missing. The actual identity is never stored in the repository.

---

## Build Outside the Repository

Using temporary output directories avoids overwriting a known working `dist/` before the new build has been tested.

```bash
.venv/bin/python -m PyInstaller \
  --clean \
  --noconfirm \
  --workpath /private/tmp/gesturecap-release-work \
  --distpath /private/tmp/gesturecap-release-dist \
  doublehand_mp.spec
```

Expected structure:

```text
/private/tmp/gesturecap-release-dist/
└── doublehand_mp/
    ├── doublehand_mp
    └── _internal/
```

The complete `_internal/` directory must remain beside the executable.

---

## Add the Licence Texts

Every packaged tracker must carry its licence and the licences of what it embeds (see [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md)):

```bash
.venv/bin/python tools/collect_licenses.py /private/tmp/gesturecap-release-dist/doublehand_mp
```

This adds `LICENSE`, `THIRD_PARTY_NOTICES.md` and a `licenses/` folder beside the executable. Run it with the Python of the build environment: it reads the licence files of the installed packages.

---

## Verify and Test the Signed Build

Confirm the architecture:

```bash
file /private/tmp/gesturecap-release-dist/doublehand_mp/doublehand_mp
```

Verify the signature:

```bash
codesign --verify --deep --strict --verbose=4 \
  /private/tmp/gesturecap-release-dist/doublehand_mp/doublehand_mp
```

Inspect the identity, Team ID, and hardened runtime:

```bash
codesign -dvvv \
  /private/tmp/gesturecap-release-dist/doublehand_mp/doublehand_mp 2>&1 \
  | grep -E "Signature|Authority|TeamIdentifier|Runtime"
```

Then run the complete build:

```bash
/private/tmp/gesturecap-release-dist/doublehand_mp/doublehand_mp
```

Verify the camera, MediaPipe detection, and OSC output before continuing.

---

## Install the Tested Build Locally

Only after verification, replace the local generated tracker:

```text
dist/
└── doublehand_mp/
    ├── doublehand_mp
    └── _internal/
```

Keep the previous tracker as a temporary backup until the replacement works from Max/MSP. `dist/` is ignored by Git and must not be committed.

---

## Package the Release

Create the archive from the tested, signed output:

```bash
ditto -c -k --keepParent \
  /private/tmp/gesturecap-release-dist/doublehand_mp \
  gesturecap-tracker-macos-arm64.zip
```

Do not move the executable out of its directory or omit `_internal/`.

---

## Store Notarization Credentials

Create an app-specific password at [account.apple.com](https://account.apple.com), then store it securely in the macOS Keychain:

```bash
xcrun notarytool store-credentials "gesturecap-notary" \
  --apple-id "YOUR_APPLE_ACCOUNT" \
  --team-id "YOUR_TEAM_ID"
```

Enter the app-specific password when prompted. Do not place it directly in a shell command, source file, or document.

This credential-storage step is normally required only once on a development machine.

---

## Submit the Exact Release Archive

```bash
xcrun notarytool submit \
  gesturecap-tracker-macos-arm64.zip \
  --keychain-profile "gesturecap-notary" \
  --wait
```

Continue only when the final status is:

```text
status: Accepted
```

Do not modify, recompress, or replace the archive after it has been accepted. Any changed build must be signed, packaged, and notarized again.

Apple's current notarization guidance is available in [Notarizing macOS software before distribution](https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution).

---

## Generate and Verify the Checksum

```bash
shasum -a 256 gesturecap-tracker-macos-arm64.zip \
  > gesturecap-tracker-macos-arm64.zip.sha256

shasum -a 256 -c gesturecap-tracker-macos-arm64.zip.sha256
```

Expected result:

```text
gesturecap-tracker-macos-arm64.zip: OK
```

Publish these files as GitHub Release assets:

```text
gesturecap-tracker-macos-arm64.zip
gesturecap-tracker-macos-arm64.zip.sha256
ffmpeg-7.1.1.tar.xz
```

The packaged tracker embeds a GPL build of FFmpeg (see [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md)). Attaching the FFmpeg source archive of the same version, downloaded from [ffmpeg.org/releases](https://ffmpeg.org/releases/), keeps the corresponding source available beside the binary.

The ZIP, checksum, build directories, and `dist/` are generated outputs and must remain outside Git history.

---

## Max Standalone Applications

The notarized tracker can be embedded in a Max standalone application, but its signature does not cover the surrounding `.app`. For public distribution, sign nested executable components, sign the complete application with the required entitlements, and notarize the final ZIP, DMG, or installer package.

See [macOS Camera Permissions](macos-camera-permissions.md) for the standalone camera and signing workflow.
