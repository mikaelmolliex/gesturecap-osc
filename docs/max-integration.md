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

Draws the MediaPipe landmarks received by the Max patch, and the tracker's start-up steps (see [Universal launcher](#universal-launcher)).

Both hands are drawn in neutral greys by default. Each patch can set its own colours:

| Message | Effect |
| --- | --- |
| `lefthandcolor r g b a` | colour of the left hand |
| `righthandcolor r g b a` | colour of the right hand |

Values go from 0 to 1, like Max colours; values from 0 to 255 are also accepted. The alpha value is optional. For example, `lefthandcolor 0.882 0.588 0.008 1` gives the amber of the earlier version.

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

### Universal launcher

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

Its outlet sends `status <step>`. Connect it to the hand view (`mediapipe_handdraw.js`, the same inlet as the hand data), which then shows what is happening instead of a spinner:

| Status | Shown in the hand view |
| --- | --- |
| `starting`, `loading`, `model`, `camera` | The start-up steps, one line each: Starting the hand tracker, Loading MediaPipe, Loading the hand model, Opening the camera |
| `ready` | Camera ready. Show your hands to the camera. |
| `camera_permission` | Camera permission needed. Click Allow in the macOS dialog to let Max use the camera. |
| `stopped` | Camera off. Turn the camera on to start. |
| `not_found` | Tracker not found |
| `camera_denied` | Camera not available, with the System Settings path |
| `stopped_unexpectedly`, `error` | The tracker stopped / could not start: see the Max console |

When no hand has been seen for 1.5 seconds, the view reminds the user to show their hands.

**Camera permission.** The first time the tracker runs for a user, macOS asks whether Max (or the standalone application) may use the camera. The tracker keeps trying to open the camera for up to 60 seconds while the dialog is on screen, and the hand view asks the user to click Allow; tracking then starts by itself. If access is denied, the view shows where to allow it: System Settings > Privacy & Security > Camera.

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

In a standalone application, put the tracker inside the application bundle, where the project's organisation does not affect it:

```text
YourApp.app/
└── Contents/
    └── Resources/
        └── tracker/
            └── doublehand_mp/
                ├── doublehand_mp
                └── _internal/
```

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
