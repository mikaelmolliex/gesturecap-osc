"""
doublehand_mp.py

Single-process doublehand OSC mapping.

Camera thread: reads frames from the webcam and keeps only the latest one.
Main thread: detects both hands and streams their landmarks over OSC.

For each detected hand, one OSC message is sent per frame, carrying the
63 floats of the 21 MediaPipe joints (x, y, z for each joint, in the
MediaPipe joint order):

    /hand/left    <x0> <y0> <z0> <x1> <y1> <z1> ... <x20> <y20> <z20>
    /hand/right   ...

x is normalized to [0, 1] (image space), y to [0, 1] with 0 at the bottom,
z is depth relative to the wrist (larger = closer to the camera).

Everything runs locally: frames never leave this process, and only the
landmark values are sent, to 127.0.0.1.
"""

import signal
import sys
import threading
import time

# Show each line at once when Max reads our output through a pipe
sys.stdout.reconfigure(line_buffering=True)

print(f"MAIN START {time.perf_counter():.3f}", flush=True)

# Record who started us before the slow imports (see utils/parent_watch.py)
from utils.parent_watch import ParentWatch
parent_watch = ParentWatch()

import cv2

from pythonosc import udp_client

from video.webcam_input import WebcamInput
from utils.hand_pose_detector import HandPoseDetector


# ── Config ────────────────────────────────────────────────────────────────────
FRAME_WIDTH  = 640
FRAME_HEIGHT = 480

OSC_IP   = "127.0.0.1"
OSC_PORT = 11111

# On a first launch, macOS asks the user to allow the camera: keep trying to
# open it for this long instead of failing while the dialog is on screen
CAMERA_WAIT_S = 60


# ==================================================
# MIKAEL MODIFICATION
# Camera mirroring (for Max UI testing)
# Set FLIP to True to enable
# ==================================================

FLIP = True


# ── Camera thread ─────────────────────────────────────────────────────────────
class LatestFrame:
    """Holds the most recent camera frame; older frames are dropped."""

    def __init__(self):
        self._cond = threading.Condition()
        self._frame = None
        self._count = 0
        self.stopped = False
        self.error = None

    def put(self, frame):
        with self._cond:
            self._frame = frame
            self._count += 1
            self._cond.notify()

    def stop(self, error=None):
        with self._cond:
            self.stopped = True
            if error is not None and self.error is None:
                self.error = error
            self._cond.notify_all()

    def wait_newer(self, last_count, timeout=1.0):
        """Return (frame, count) once a frame newer than last_count exists."""
        with self._cond:
            self._cond.wait_for(
                lambda: self._count > last_count or self.stopped, timeout
            )
            if self._count > last_count:
                return self._frame, self._count
            return None, last_count


def open_camera(latest):
    """Open the webcam, waiting up to CAMERA_WAIT_S for the user's permission."""
    deadline = time.monotonic() + CAMERA_WAIT_S
    announced = False
    while not latest.stopped:
        try:
            return WebcamInput(width=FRAME_WIDTH, height=FRAME_HEIGHT)
        except RuntimeError as error:
            if time.monotonic() >= deadline:
                latest.stop(error)
                return None
            if not announced:
                print("WAITING FOR CAMERA: allow camera access if macOS asks.", flush=True)
                announced = True
            time.sleep(1.0)
    return None


def camera_loop(latest):
    cam = open_camera(latest)
    if cam is None:
        return

    try:
        while not latest.stopped:
            result = cam.read_frame()
            if result is None:
                latest.stop(RuntimeError("Camera stopped sending frames."))
                break

            frame = result[0]
            if frame.shape[:2] != (FRAME_HEIGHT, FRAME_WIDTH):
                frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
            latest.put(frame)
    finally:
        cam.cleanup()


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    latest = LatestFrame()

    # Max stops the tracker with SIGTERM: leave the loop and release the camera
    def request_stop(signum, _frame):
        latest.stop()

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)

    # Never run without the application that started us (e.g. if Max crashes)
    def parent_gone(reason):
        print(f"Stopping: {reason}.", flush=True)
        latest.stop()

    parent_watch.start(parent_gone)

    # The camera opens while the detector loads
    camera = threading.Thread(target=camera_loop, args=(latest,), daemon=True)
    camera.start()

    client = udp_client.SimpleUDPClient(OSC_IP, OSC_PORT)

    print("CREATING HANDPOSEDETECTOR", flush=True)
    t0 = time.perf_counter()
    detector = HandPoseDetector(n_hands=2, device="cpu")
    print(
        f"HANDPOSEDETECTOR READY IN {(time.perf_counter() - t0) * 1000:.0f} ms",
        flush=True,
    )

    print("Streaming hand landmarks over OSC — press Ctrl+C to stop.", flush=True)

    last_count = 0
    ready_announced = False
    while not latest.stopped:
        frame, last_count = latest.wait_newer(last_count)
        if frame is None:
            continue

        # ==================================================
        # MIKAEL MODIFICATION
        # Apply horizontal flip if enabled
        # Set FLIP = True to mirror the camera (like webcam apps)
        if FLIP:
            frame = cv2.flip(frame, 1)

        hands = detector.detect_hand_pose(frame)

        # The launcher waits for this line to tell the user to show their hands
        if not ready_announced:
            print("TRACKER READY: camera on, show your hands.", flush=True)
            ready_announced = True

        for hand in hands:
            raw_label = hand.get("label", "").lower()

            # ==================================================
            # MIKAEL MODIFICATION
            # Adjust hand labels when camera is mirrored (FLIP)
            # This ensures OSC output matches user perspective
            # ==================================================
            if FLIP:
                label = "right" if raw_label == "left" else "left"
            else:
                label = raw_label

            if label not in ("left", "right"):
                continue

            values = []

            # ==================================================
            # MIKAEL MODIFICATION
            for lm in hand["landmarks"].landmark:
                # horizontal axis
                x = lm.x

                # vertical axis
                y = 1 - lm.y
                # 0 = bottom, 1 = top

                # depth
                z = -lm.z  # invert depth for more intuitive positive range

                values.extend([x, y, z])

            client.send_message(f"/hand/{label}", values)

    camera.join(timeout=2.0)

    if latest.error is not None:
        print(f"ERROR: {latest.error}", flush=True)
        print("MAIN EXIT", flush=True)
        return 1

    print("MAIN EXIT", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
