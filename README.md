# GestureCap OSC

Run MediaPipe locally, route gesture data in Max/MSP, and control audio, visual, or other parameters.

GestureCap OSC packages the MediaPipe tracker so it can run locally without sending camera data to a cloud service. The tracker can be launched directly from Max/MSP, embedded in a Max Project, or included in a standalone application.

The repository connects three main stages:

```text
Local MediaPipe tracking
        ↓ OSC — 127.0.0.1:11111
Gesture routing matrix
        ↓
12 custom parameter dials
        ↓
Audio, visuals, or other processes
```

By default, tracking and OSC communication stay on the local machine. Camera frames are processed locally and only landmark data is sent to Max.

![GestureCap OSC demonstration](media/gesture-cap-demo.gif)

---

## Quick Start — Complete Project, No Python Installation

The recommended download is the ready-to-run macOS Apple Silicon package:

```text
gesturecap-osc-v0.1.0-macos-arm64-complete.zip
```

1. Download the complete package from the [latest GitHub Release](https://github.com/mikaelmolliex/gesturecap-osc/releases/latest).
2. Unzip it.
3. Open `max/GestureCap_Tracker_Test.maxpat` in Max/MSP.
4. Enable the camera/video control.

That is all. The complete release already contains the signed and notarized tracker at:

```text
dist/doublehand_mp/doublehand_mp
```

Python is not required on the performance machine, and no tracker folder needs to be moved. The `v0.1.0` tracker can take approximately 20–30 seconds to start. From the next version, the tracker runs as a single process without matplotlib: in our tests on an M1 Max, the first hand arrived about 1 second after launch. The very first launch on a computer stays slower while macOS checks the new files.

This ready-to-run build currently supports macOS Apple Silicon (`arm64`). If you only need the tracker for another Max Project, standalone, or OSC application, use the smaller tracker-only asset described in [Tracker-Only Download and Manual Integration](#tracker-only-download-and-manual-integration).

---

## Why This Repository

The main goal is to make a MediaPipe-based gesture pipeline portable and practical inside Max/MSP applications:

- Run hand tracking locally and privately
- Launch the packaged tracker from Max
- Embed the tracker in a Max Project or standalone application
- Visualize MediaPipe landmarks inside Max
- Route gesture axes to 12 destination parameters
- Calibrate and shape each parameter with custom JSUI dials
- Reuse the routing matrix with OSC, USB, or Bluetooth controllers

---

## Main Components

### MediaPipe Tracker

The packaged tracker runs MediaPipe and OpenCV locally. It supports up to two hands with 21 landmarks per hand and sends X, Y, and Z values to:

```text
/hand/left
/hand/right
```

Default OSC destination:

```text
127.0.0.1:11111
```

The tracker has no window of its own: `mediapipe_handdraw.js` renders the landmark data inside Max/MSP. (The `v0.1.0` tracker still opens an OpenCV preview.)

### Gesture Routing Matrix

The routing matrix is designed primarily around MediaPipe data.

![GestureCap OSC routing matrix](media/routing-matrix.png)

Primary modes:

- **Hands** — direct access to the 21 landmarks of each hand
- **Clusters** — grouped MediaPipe sources for higher-level gesture control

Additional controller modes:

- **Wearable** — OSC data from wearable controllers
- **Gamepad** — USB or Bluetooth exploration and parameter control
- **Mouse** — manual exploration, testing, and parameter control

Each mode preserves its own active sources, selections, and mappings.

#### Matrix messages

The matrix accepts the following control messages:

| Message | Behavior |
| --- | --- |
| `mode hands` | Selects the Hands mode. Replace `hands` with `clusters`, `wearable`, `gamepad`, or `mouse` to select another mode. |
| `clear` | Resets LEDs, gates, selections, and mappings for the current mode. Colors are preserved. |
| `clearall` | Resets states and mappings for every mode. Colors are preserved. |
| `clearmappings` | Clears only the mappings for the current mode. Active LEDs, gates, and selections are preserved. |
| `rightborderactive $1` | Sets the active-border value for the right-hand side. |
| `leftborderactive $1` | Sets the active-border value for the left-hand side. |
| `rightborderinactive $1` | Sets the inactive-border value for the right-hand side. |
| `leftborderinactive $1` | Sets the inactive-border value for the left-hand side. |
| `rightbgactive $1` | Sets the active-background value for the right-hand side. |
| `leftbgactive $1` | Sets the active-background value for the left-hand side. |
| `rightbginactive $1` | Sets the inactive-background value for the right-hand side. |
| `leftbginactive $1` | Sets the inactive-background value for the left-hand side. |
| `rightcolor $1` | Sets the right-hand display color value. |
| `leftcolor $1` | Sets the left-hand display color value. |

In Max message boxes, `$1` is replaced by the value sent to the message.

See [Gesture Routing Matrix](docs/routing-matrix.md) for messages, outputs, colors, and state behavior.

### Custom Parameter Dials

Twelve reusable JSUI dials process normalized controller data through:

![GestureCap OSC custom parameter dials](media/custom-dials.png)

```text
Raw Input
→ Near / Far
→ Invert
→ Exponent
→ Playable Range
→ Unit Display
→ Triggers
```

See [Custom JSUI Dials](docs/custom-dials.md) for messages, outlets, and display behavior.

---

## Tracker-Only Download and Manual Integration

Use this section if you cloned a version of the repository without `dist/`, or if you want to embed the tracker in your own Max Project, standalone, or OSC application. Users of the complete ready-to-run package can skip this section.

### 1. Download the tracker-only asset

Download the smaller tracker package from the [latest GitHub Release](https://github.com/mikaelmolliex/gesturecap-osc/releases/latest):

```text
gesturecap-tracker-macos-arm64.zip
```

To use it with this repository:

1. Unzip the archive.
2. Create `dist/` at the repository root if it is not already present.
3. Move the extracted `doublehand_mp/` folder into `dist/`.

This installation step is mandatory. The standard Max launcher cannot start MediaPipe until the executable exists at:

```text
dist/doublehand_mp/doublehand_mp
```

The current build is provided for macOS Apple Silicon (`arm64`). It is signed with an Apple Developer ID and notarized by Apple for distribution outside the Mac App Store.

The optional checksum asset is:

```text
gesturecap-tracker-macos-arm64.zip.sha256
```

To verify the download, place the ZIP and checksum file together, then run:

```bash
shasum -a 256 -c gesturecap-tracker-macos-arm64.zip.sha256
```

The expected result is:

```text
gesturecap-tracker-macos-arm64.zip: OK
```

The checksum verification is recommended but is not required to run the tracker. The archive contains `doublehand_mp/`; it does not create the parent `dist/` directory for you.

The final project structure for the standard ready-to-run repository must be:

```text
gesturecap-osc/
├── dist/
│   └── doublehand_mp/
│       ├── doublehand_mp
│       └── _internal/
└── max/
    ├── GestureCap_Tracker_Test.maxpat
    ├── run_mediapipe.js
    ├── mediapipe_handdraw.js
    ├── gesture_mapper_ui_multimode_extended.js
    └── custom.dial.v9.js
```

The complete `_internal/` directory must remain beside the `doublehand_mp` executable. Do not move the executable by itself.

On first launch, macOS may display its normal confirmation and camera-permission dialogs. If Gatekeeper reports that it cannot verify the tracker, confirm that you downloaded the current Release asset and that the SHA-256 verification succeeds. Do not replace the release signature with an ad-hoc signature.

### 2. Test with the included Max patch

```text
max/GestureCap_Tracker_Test.maxpat
```

**Folder access.** macOS protects the Desktop, Documents and Downloads folders. If the repository is in one of them, macOS asks whether Max may access that folder: click **Allow**, otherwise Max cannot load the patch's scripts (`.js` files) and the hand view, routing matrix and dials stay empty. If you clicked Don't Allow, turn Max on in System Settings > Privacy & Security > Files & Folders, then reopen the patch. A folder outside these three (for example `~/gesturecap-osc`) needs no permission.

### 3. Enable the camera/video control

Max launches the packaged tracker. The tracker sends MediaPipe landmarks to the visualizer embedded in the Max patch.

The first time, macOS asks whether Max may use the camera: click **Allow**. The tracker waits up to 60 seconds for this answer, then starts by itself. If nobody answers within 60 seconds, click Allow anyway, then turn the camera off and on again. If access was denied, turn Max on in System Settings > Privacy & Security > Camera: macOS then offers to quit and reopen Max, after which the camera works.

If the camera goes away while tracking (another app takes it, or you switch to another user account), the tracker waits for it and resumes by itself; the hand view shows "Camera unavailable" meanwhile.

With the `v0.1.0` tracker, the initial launch can take approximately 20–30 seconds. Later versions start in a few seconds once macOS has checked the files on the first launch.

### Tracker paths by integration mode

One launcher, [`max/run_mediapipe.js`](max/run_mediapipe.js), works in a regular patch, a Max Project and a standalone application. It finds the tracker by itself, going up at most four folders from the launcher and looking for `tracker/doublehand_mp/` or `dist/doublehand_mp/`, then inside `YourApp.app/Contents/Resources/tracker/`. The Max console shows the path it found, or every place it searched.

| Context | Where to put the tracker |
| --- | --- |
| This repository (regular patch) | `dist/doublehand_mp/` or `tracker/doublehand_mp/` at the repository root |
| Max Project | `tracker/doublehand_mp/` **beside** the project folder, never inside it: a Max Project moves every file inside its folder into its own subfolders, which breaks the tracker |
| Standalone application | `YourApp.app/Contents/Resources/tracker/doublehand_mp/` |

The tracker never keeps running without Max: turning the camera off, closing the patch or quitting Max stops it, and if Max crashes, the tracker stops by itself within about a second.

In every integration mode, keep the complete `_internal/` directory beside the `doublehand_mp` executable.

Embedding the signed tracker does not automatically sign or notarize the surrounding standalone application. The complete `.app` and its final distribution archive must be signed and notarized separately before public distribution.

See [Max/MSP Integration](docs/max-integration.md#universal-launcher) for the launcher's messages and the start-up messages shown in the patch.

---

## Packaged Tracker and `dist/`

The packaged tracker is distributed as a GitHub Release asset, `gesturecap-tracker-macos-arm64.zip`, not in the Git repository. Place the extracted `doublehand_mp/` folder in `dist/` (or `tracker/`) at the repository root; both folders are ignored by Git.

The `v0.1.0` tag is the exception: for that ready-to-run milestone, `dist/doublehand_mp/` was included in the release commit.

Release workflow:

1. Build `doublehand_mp/` from the committed PyInstaller specification, then add the licence texts with `tools/collect_licenses.py`.
2. Sign the release build with a Developer ID Application identity and hardened runtime.
3. Verify the executable and test the complete generated directory.
4. Compress the signed `doublehand_mp/` directory as `gesturecap-tracker-macos-arm64.zip`.
5. Submit that exact archive to Apple's notary service.
6. Generate and verify `gesturecap-tracker-macos-arm64.zip.sha256`.
7. Attach the accepted archive, its checksum and the FFmpeg source archive to a GitHub Release.
8. Keep standalone ZIP and checksum assets outside Git history.

The unpacked tracker is approximately 180 MB (217 MB for `v0.1.0`). The release archive is smaller because it is compressed.

The current packaged tracker is built for macOS Apple Silicon (`arm64`). Intel macOS and Windows require separate builds and release assets.

Developers who want to run from Python source can use the repository's Python environment. See [Build Tracker on macOS](docs/build-tracker.md) for the PyInstaller workflow.

---

## Main Files

```text
max/GestureCap_Tracker_Test.maxpat       Main Max/MSP demonstration patch
dist/doublehand_mp/                      Packaged local MediaPipe tracker
max/mediapipe_handdraw.js                Landmark visualizer
max/gesture_mapper_ui_multimode_extended.js
                                         Gesture routing matrix
max/custom.dial.v9.js                    Custom parameter dial
max/run_mediapipe.js                     Tracker launcher (patch, Max Project, standalone)
```

---

## macOS Standalone Deployment

For a standalone application, the tracker can be embedded at:

```text
YourApp.app
└── Contents
    └── Resources
        └── tracker
            └── doublehand_mp/
                ├── doublehand_mp
                └── _internal/
```

Camera access may require `NSCameraUsageDescription`, a camera entitlement, application signing, and a TCC permission reset during development. Embedding the already signed tracker does not sign or notarize the surrounding Max standalone application: the complete `.app` and its final distribution archive must follow their own Developer ID signing and notarization workflow.

See [macOS Camera Permissions](docs/macos-camera-permissions.md) for the complete workflow.

---

## Credits

GestureCap OSC builds on two earlier Google Summer of Code projects of the [INCF](https://www.incf.org/) organization:

- [GestureCap](https://github.com/m2b3/gesturecap) (2024), by **Louis Martinez**: the original hand-gesture-to-sound pipeline, released under the GPL-3.0.
- [GestureCap 2025](https://github.com/m2b3/gesturecap2025) (2025), by **Deepansh Goel**, with webcam input by **Shiv Patil**: the latency work and multiprocessing pipeline from which this repository is forked.

This repository, by **Mikaël Molliex**, includes work developed as part of Google Summer of Code 2026. It extends the pipeline with local OSC integration, Max/MSP routing, a packaged tracker, embedded visualization, and custom parameter interfaces.

---

## Visual Assets

Interface icons are sourced from [Iconoir](https://iconoir.com/).

---

## License

GestureCap OSC is free software, released under the [GNU General Public License, version 3 or later](LICENSE). It derives from GPL-3.0 code (GestureCap, 2024), and the packaged tracker embeds a GPL build of FFmpeg through OpenCV.

Releases up to `v0.1.0` were published under the MIT license.

Third-party components keep their own licenses: see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).