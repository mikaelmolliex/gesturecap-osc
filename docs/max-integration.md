# Max/MSP Integration

The main demonstration patch is:

```text
max/GestureCap_Tracker_Test.maxpat
```

It connects the MediaPipe tracker, OSC reception, hand visualization, gesture routing matrix, and custom parameter dials.

---

## JSUI Components

### Hand Landmark Visualizer

```text
mediapipe_handdraw.js
```

Draws the MediaPipe landmarks received by the Max patch.

### Gesture Routing Matrix

```text
gesture_mapper_ui_multimode_extended.js
```

Selects active sources and maps controller axes to the 12 destination parameters.

### Custom Parameter Dial

```text
custom.dial.v9.js
```

Displays raw input and processes calibration, inversion, exponent, playable range, units, and triggers.

---

## Tracker Launchers

### Universal launcher (recommended)

```text
max/run_mediapipe.js
```

One launcher for a regular patch, a Max Project and a standalone application. Load it with `[node.script run_mediapipe.js @autostart 1]`.

It finds the tracker by itself, in this order:

1. the path given with the `trackerpath <path>` message, if any;
2. from the launcher's folder, going up at most four folders: `tracker/doublehand_mp/doublehand_mp`, then `dist/doublehand_mp/doublehand_mp`;
3. inside a standalone: `YourApp.app/Contents/Resources/tracker/doublehand_mp/doublehand_mp`.

The Max console shows the path it found, or every place it searched.

| Message | Effect |
| --- | --- |
| `camera_on` | starts the tracker |
| `camera_off` | stops the tracker (forced after 3 seconds if needed) |
| `where` | prints the tracker path in the Max console |
| `trackerpath <path>` | sets the tracker path by hand; `trackerpath` alone returns to the automatic search |

Its outlet sends `status starting`, `status running`, `status stopped`, `status not_found` or `status error`.

**The tracker never runs without Max.** `camera_off` stops it, closing the patch or quitting Max stops it, and if Max crashes or is force-quit, the tracker notices that Max is gone and stops by itself within about a second, releasing the camera ([utils/parent_watch.py](../utils/parent_watch.py)).

**Keep the tracker outside a Max Project folder.** A Max Project moves every file inside its folder into its own subfolders (`code/`, `data/`, `other/`…), which breaks the tracker. Place `tracker/` beside the project:

```text
MyWork/
├── MyProject/
│   ├── MyProject.maxproj
│   ├── code/run_mediapipe.js
│   └── patchers/
└── tracker/
    └── doublehand_mp/
        ├── doublehand_mp
        └── _internal/
```

In a standalone application, put the tracker in `Contents/Resources/tracker/` (see below): it is not affected by the project's organisation.

### Earlier launchers

The three earlier launcher scripts are kept for now:

| Script | Context |
| --- | --- |
| `run_mediapipe_maxmsp.js` | regular Max patch |
| `run_mediapipe_maxmsp_project.js` | Max Project |
| `run_mediapipe_standalone.js` | Max standalone application |

Use the launcher that matches the environment containing the patch. The routing and interface logic remains the same in all three contexts.

The tracker is distributed separately through the [latest GitHub Release](https://github.com/mikaelmolliex/gesturecap-osc/releases/latest). The current macOS Apple Silicon asset is signed with a Developer ID and notarized by Apple. Keep the complete `doublehand_mp/` directory, including `_internal/`.

### Regular Max patch

```text
gesturecap-osc/
├── dist/
│   └── doublehand_mp/
│       ├── doublehand_mp
│       └── _internal/
└── max/
    └── run_mediapipe_maxmsp.js
```

The launcher expects `dist/doublehand_mp/doublehand_mp` relative to the repository root.

### Max Project

`run_mediapipe_maxmsp_project.js` resolves a `tracker/doublehand_mp/` directory relative to the project launcher. Confirm the resolved location after reorganizing a Max Project.

### Max standalone

The expected bundle structure is:

```text
YourApp.app/
└── Contents/
    └── Resources/
        └── tracker/
            └── doublehand_mp/
                ├── doublehand_mp
                └── _internal/
```

The provided `run_mediapipe_standalone.js` currently contains `DriftMap.app` as an example application name. Replace it with the actual standalone name or change `TRACKER_PATH` to match the final bundle.

Embedding the signed tracker is not sufficient for public distribution. The surrounding `.app` must be signed with its required entitlements, and the final ZIP, DMG, or installer must be notarized separately. See [macOS Camera Permissions](macos-camera-permissions.md).

---

## Data Flow

```text
Tracker
  ↓ OSC — 127.0.0.1:11111
GestureCap_Tracker_Test.maxpat
  ├── mediapipe_handdraw.js
  ├── gesture_mapper_ui_multimode_extended.js
  └── custom.dial.v9.js × 12
```

The JSUI components handle visualization, mapping, and parameter control. OSC reception and real-time routing remain in Max/MSP.
