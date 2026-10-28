# GestureCap OSC v0.2.0 — Faster, Safer Tracker Start

GestureCap OSC runs MediaPipe hand tracking locally on the Mac, sends the landmarks to Max over OSC (`127.0.0.1:11111`), and routes them through a gesture matrix and 12 custom dials. Camera images never leave the computer.

## Requirements

- Mac with Apple silicon (M1 or later), macOS 14 Sonoma or later
- Max 9 (tested with 9.1.2)
- A camera

## Downloads

| File | For |
| --- | --- |
| `gesturecap-osc-v0.2.0-macos-arm64-complete.zip` | Max users: the whole project with the signed tracker in place. Unzip, open `max/GestureCap_Tracker_Test.maxpat`, turn the camera on. |
| `gesturecap-tracker-macos-arm64.zip` | The signed and notarized tracker alone, to embed in your own patch, Max Project or standalone |
| `*.sha256` | Checksums of both archives |
| `ffmpeg-7.1.1.tar.xz.asc` | FFmpeg's signature of its source archive |
| `ffmpeg-7.1.1.tar.xz` | Source code of the FFmpeg build embedded in the tracker (GPL) |

## What changed since v0.1.0

- **Faster start.** One tracker process instead of three, and no matplotlib. In our tests on a MacBook Pro M1 Max, the first hand arrived 1.1 seconds after launch instead of 33 seconds; memory went from about 600 MB to about 330 MB. The very first launch on a computer stays slower (about 30 seconds) while macOS checks the new files.
- **One launcher** (`max/run_mediapipe.js`) for a regular patch, a Max Project and a standalone application. It finds the tracker by itself and shows in the Max console where it looked.
- **The tracker never runs without Max.** Turning the camera off, closing the patch or quitting Max stops it; if Max crashes or is force-quit, the tracker stops by itself within about a second.
- **Clear messages in the hand view** instead of a spinner: the start-up steps, then "Camera ready. Show your hands to the camera." The camera permission is handled: the tracker waits up to 60 seconds for the macOS dialog, and explains what to do if access is denied or the camera is taken by another app or user session (tracking then resumes by itself).
- **No separate OpenCV window**: the hands are drawn in Max only. Hand colours can be set with `lefthandcolor` and `righthandcolor`.
- **Smaller tracker**: 181 MB and 138 files (was 217 MB and 370 files).
- **License: GPL-3.0-or-later.** GestureCap OSC derives from GestureCap (GPL-3.0) and its packaged tracker embeds a GPL build of FFmpeg. Each tracker now carries `LICENSE`, `THIRD_PARTY_NOTICES.md` and the licence texts of its components. v0.1.0 remains MIT.

## Tested

On a MacBook Pro M1 Max (macOS 26.2, Max 9.1.2): the demo patch with the hand view, matrix and dials; start and stop; quitting and force-quitting Max; a new user account with a fresh download (camera permission allowed, denied, unanswered; switching user sessions).

On another Mac (Apple M1), the signed tracker downloaded as a file: no macOS warning, camera permission, then tracking.

Not tested yet: Max standalone applications, other Apple-silicon models than M1 and M1 Max.

## Credits

Built on GestureCap (Louis Martinez, Google Summer of Code 2024) and GestureCap 2025 (Deepansh Goel, Shiv Patil, Google Summer of Code 2025), INCF.
