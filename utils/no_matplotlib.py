"""
no_matplotlib.py

Keeps `import mediapipe` from loading matplotlib.

MediaPipe 0.10.14 imports `matplotlib.pyplot` in its old drawing tools
(mediapipe/python/solutions/drawing_utils.py), only for plot_landmarks(),
which this tracker never calls. Loading matplotlib costs several seconds,
and in the packaged tracker it rebuilds its font cache at every launch.

Import this module before mediapipe: it registers an empty placeholder for
matplotlib, so matplotlib is neither loaded nor needed in the build.
"""

import sys
import types


def _unavailable(name):
    raise AttributeError(
        f"matplotlib is not included in the GestureCap tracker (asked for '{name}')."
    )


if "matplotlib" not in sys.modules:
    _matplotlib = types.ModuleType("matplotlib")
    _pyplot = types.ModuleType("matplotlib.pyplot")
    _matplotlib.__getattr__ = _unavailable
    _pyplot.__getattr__ = _unavailable
    _matplotlib.pyplot = _pyplot
    sys.modules["matplotlib"] = _matplotlib
    sys.modules["matplotlib.pyplot"] = _pyplot
