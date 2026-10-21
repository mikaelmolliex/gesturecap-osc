# Quickstart

This guide gets you from a blank machine to streaming hand-landmark data over OSC in a few minutes.

---

## 1. Install uv

`uv` is a fast Python package manager. Run the one-liner for your OS:

**macOS / Linux**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell)**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After install, restart your terminal (or `source ~/.bashrc` / `source ~/.zshrc`) so the `uv` command is on your PATH.

---

## 2. Clone the repo

```bash
git clone https://github.com/mikaelmolliex/gesturecap-osc.git
cd gesturecap-osc
```

---

## 3. Install dependencies

```bash
uv sync
```

This creates a `.venv` folder and installs everything (MediaPipe, OpenCV, python-osc). No manual `pip` or virtual-env steps needed.

MediaPipe 0.10.14 also declares jax, matplotlib, sounddevice and a second OpenCV, which the hand tracker never uses. `pyproject.toml` leaves them out, and [utils/no_matplotlib.py](../utils/no_matplotlib.py) keeps MediaPipe from asking for matplotlib.

---

## 4. Hand model

The model file (`models/hand_landmarker.task`) is bundled with the repo, so you should already have it after cloning.

If it's missing for any reason, download it manually:

```bash
curl -L -o models/hand_landmarker.task \
  https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task
```

---

## 5. Set your OSC target

By default the script sends OSC to `127.0.0.1:11111` — the same machine, port 11111.  
If your audio software (Pure Data, Max/MSP, SuperCollider, etc.) listens on a different address or port, edit the two lines near the top of [doublehand_mp.py](../doublehand_mp.py):

```python
OSC_IP   = "127.0.0.1"   # ← change to your machine's IP if needed
OSC_PORT = 11111          # ← change to match your patch's inlet port
```

---

## 6. Run

```bash
uv run python doublehand_mp.py
```

The webcam opens and the tracker starts streaming. It has no window of its own: draw the hands in your patch (for Max, see `max/mediapipe_handdraw.js`).  
Press **`Ctrl+C`** in the terminal to quit cleanly.

---

## What gets sent

For every processed frame, each visible hand emits **one OSC message** containing 63 float values:

```text
/hand/left  <63 float arguments>
/hand/right <63 float arguments>
```

The payload contains X, Y, and Z for each of the 21 MediaPipe landmarks, in this order:

```text
wrist_x, wrist_y, wrist_z,
thumb_cmc_x, thumb_cmc_y, thumb_cmc_z,
thumb_mcp_x, thumb_mcp_y, thumb_mcp_z,
...
pinky_tip_x, pinky_tip_y, pinky_tip_z
```

The complete landmark order is:

```text
wrist,
thumb_cmc, thumb_mcp, thumb_ip, thumb_tip,
index_finger_mcp, index_finger_pip, index_finger_dip, index_finger_tip,
middle_finger_mcp, middle_finger_pip, middle_finger_dip, middle_finger_tip,
ring_finger_mcp, ring_finger_pip, ring_finger_dip, ring_finger_tip,
pinky_mcp, pinky_pip, pinky_dip, pinky_tip
```

With both hands visible, the tracker therefore sends up to two OSC messages per processed frame, carrying 126 float values in total.

---

## Mapping coordinates to sound (in your patch)

All values arrive as floats:

- **`x`** — horizontal position in the mirrored camera image, `0.0` at the left edge and `1.0` at the right edge
- **`y`** — vertical position after inversion, `0.0` at the bottom and `1.0` at the top
- **`z`** — inverted relative depth, approximately `0` at the wrist; values are not metric

In Max/MSP, first route `/hand/right` and `/hand/left`, then unpack the 63-value payload into X/Y/Z triplets. The included demonstration patch already performs this step.

A few starter mappings:

- map the right index-tip X value to frequency
- map its Y value to volume
- calculate the distance between thumb tip and index tip for a pinch gate
- use the left and right hand payloads as independent controllers

If you want to calculate derived gestures in Python, the relevant section is the main loop in `main()` in [doublehand_mp.py](../doublehand_mp.py), where the 63-value list is assembled and sent through `client.send_message(...)`.

