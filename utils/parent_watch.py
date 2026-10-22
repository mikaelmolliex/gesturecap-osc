"""
parent_watch.py

Stops the tracker when the program that started it is gone.

The tracker must never keep running (and keep the camera on) without the
application that launched it. When Max quits normally, its launcher stops
the tracker. But if Max crashes, or if the launcher is killed, nobody is
left to stop it. So the tracker watches every process above it (for Max:
the Node for Max script, then Max itself) and stops as soon as one of them
disappears.

Run from a terminal, the tracker likewise stops when the terminal closes.
"""

import os
import subprocess
import threading
import time


def _parent_of(pid):
    try:
        out = subprocess.run(
            ["ps", "-o", "ppid=", "-p", str(pid)],
            capture_output=True, text=True, timeout=2,
        ).stdout.strip()
        return int(out) if out else None
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def _ancestors():
    """PIDs above this process, nearest first, without launchd (PID 1)."""
    chain = []
    pid = os.getppid()
    while pid and pid > 1 and pid not in chain:
        chain.append(pid)
        pid = _parent_of(pid)
    return chain


def _exists(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True  # alive, but owned by another user
    return True


class ParentWatch:
    """Create it as early as possible: it records the parents at that moment."""

    def __init__(self):
        self.first_parent = os.getppid()
        self.ancestors = _ancestors() if os.name == "posix" else []

    def start(self, on_gone, interval=0.5):
        """Call on_gone() once, from a background thread, when a parent is gone."""
        if os.name != "posix":
            return None

        def loop():
            while True:
                # Our own parent: when it dies, we are handed over to another one
                if os.getppid() != self.first_parent:
                    on_gone(f"parent process {self.first_parent} is gone")
                    return
                for pid in self.ancestors:
                    if not _exists(pid):
                        on_gone(f"ancestor process {pid} is gone")
                        return
                time.sleep(interval)

        thread = threading.Thread(target=loop, name="parent-watch", daemon=True)
        thread.start()
        return thread
