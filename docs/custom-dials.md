# Custom JSUI Dials

The custom dial is a reusable Max/MSP `jsui` controller and visualizer for continuous normalized input.

The current implementation is:

```text
custom.dial.js
```

It is designed for a compact interface of approximately `124 × 112 px` and can be duplicated for up to 12 destination parameters.

---

## Signal Flow

```text
Raw input 0–1
    ↓
Near / Far calibration
    ↓
Invert
    ↓
Exponent curve
    ↓
Playable range
    ↓
Normalized output 0–1
    ↓
Unit conversion and triggers
```

The outer input LEDs represent raw controller input. The output arc and pointer represent the processed value.

Routing to MIDI, OSC, audio, or destination parameters remains in Max/MSP.

---

## Main Messages

### Input

```text
input 0.5
setinput 0.5
```

`input` processes and outputs the value. `setinput` updates the dial without sending its normal output.

### Calibration

```text
calibrationon
calibrationoff
setnear 0.1
setfar 0.9
```

Near maps to normalized `0`; Far maps to normalized `1`.

### Mapping

```text
invert 0
invert 1
exponent 1.0
rangemin 0.2
rangemax 0.8
```

Playable range messages accept normalized or percentage-style values. For example, `rangemin 0.2` and `rangemin 20` both represent 20%.

Exponent behavior:

```text
below 1.0  → logarithmic-like response
1.0        → linear response
above 1.0  → exponential response
```

### Units

```text
unit normalized
unit percent
unit hz
unit decibel
unit semitone
unit cents
```

Optional conversion limits can be supplied with:

```text
displayrange minimum maximum
```

### Input LEDs

```text
inputleds always
inputleds activity
inputleds hidden
```

### Output Display

```text
outputdisplay always
outputdisplay activity
outputdisplay hidden
```

### Triggers

```text
triggerenable 1
triggerlow 0.01
triggerhigh 0.99
hysteresis 0.04
```

### Manual Control

```text
sensitivity 160
reset
```

Sensitivity affects mouse dragging only. Sensor smoothing should happen elsewhere in the Max patch.

---

## Outlets

The current `custom.dial.js` design uses five outlets:

| Outlet | Output |
| --- | --- |
| 1 | normalized output from `0` to `1` |
| 2 | converted numerical value |
| 3 | unit symbol |
| 4 | MIN trigger bang |
| 5 | MAX trigger bang |

Max outlets are numbered here as they appear to the user. Internally, JavaScript indexes them from `0` to `4`.

---

## Mouse Interaction

Dragging the dial simulates raw input and follows the same processing path as MediaPipe, gamepad, or mouse data.

Holding Shift enables finer manual adjustment. The `sensitivity` message controls only this manual drag behavior.

---

## Preset Storage

The dial exposes its current normalized output value to Max `pattrstorage` through `getvalueof()` and `setvalueof()`.

Mapping parameters such as Near/Far, Range, Invert, Exponent, units, and triggers should continue to be stored by their corresponding Max controls.

Avoid feeding the dial output directly back into its input, as this can create a Max feedback loop.
