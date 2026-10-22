# Third-Party Notices

GestureCap OSC is free software, released under the [GNU General Public License, version 3 or later](LICENSE) (GPL-3.0-or-later). It builds on earlier free software and, in its packaged tracker, embeds third-party software. Those components keep their own copyright notices and licences; the GPL does not replace them.

This file accompanies every release of the packaged tracker. The full licence texts are copied into the `licenses/` folder of each packaged tracker by [`tools/collect_licenses.py`](tools/collect_licenses.py).

Licences were checked on 22 October 2026 in the official packages (PyPI distributions and their licence files), in the official repositories, and, for FFmpeg, in the build options recorded in the binary itself. This is a careful inventory, not legal advice.

---

## 1. Projects this one is based on

| Project | Authors | Licence | What comes from it |
| --- | --- | --- | --- |
| [GestureCap](https://github.com/m2b3/gesturecap), Google Summer of Code 2024, INCF | Louis Martinez | GPL-3.0 | the original pipeline; the landmark conversion in `utils/hand_pose_detector.py`; the video input classes in `video/` |
| [GestureCap 2025](https://github.com/m2b3/gesturecap2025), Google Summer of Code 2025, INCF | Deepansh Goel; Shiv Patil (webcam input) | no licence file published | the repository this one is forked from: the multiprocessing pipeline (since replaced), `video/webcam_input.py`, the project layout |

GestureCap OSC itself (Google Summer of Code 2026 and later work) is by Mikaël Molliex. Releases up to `v0.1.0` were published under the MIT licence; from the next release on, the project is GPL-3.0-or-later, as required by the code it derives from and by the FFmpeg build it embeds (see below).

---

## 2. What the packaged tracker embeds

Packaged tracker for macOS on Apple silicon (`doublehand_mp/`), built with PyInstaller from `requirements.txt`.

| Component | Version | Licence | Use |
| --- | --- | --- | --- |
| [Python](https://www.python.org/) (CPython, [python-build-standalone](https://github.com/astral-sh/python-build-standalone) build 20230726) | 3.10.12 | PSF-2.0 | the embedded Python runtime |
| [PyInstaller](https://pyinstaller.org/) bootloader | 6.21.0 | GPL-2.0-or-later with the bootloader exception | starts the packaged program |
| [MediaPipe](https://github.com/google-ai-edge/mediapipe) | 0.10.14 | Apache-2.0 | hand landmark detection |
| Hand landmarker model (`models/hand_landmarker.task`) | float16 | Apache-2.0 (stated on its [model card](https://storage.googleapis.com/mediapipe-assets/Model%20Card%20Hand%20Tracking%20(Lite_Full)%20with%20Fairness%20Oct%202021.pdf)) | the trained hand model |
| [OpenCV](https://opencv.org/), as [opencv-python-headless](https://github.com/opencv/opencv-python) | 4.13.0.92 | Apache-2.0 (OpenCV); MIT (packaging scripts) | camera capture and image processing |
| [FFmpeg](https://ffmpeg.org/), inside OpenCV | 7.1.1 | **GPL-3.0-or-later as built** | OpenCV's video back end (not used for the camera) |
| [x264](https://www.videolan.org/developers/x264.html), [x265](https://www.videolan.org/developers/x265.html), [Rubber Band](https://breakfastquay.com/rubberband/), [vid.stab](https://github.com/georgmartius/vid.stab), libpostproc, inside OpenCV | bundled | GPL-2.0-or-later | FFmpeg dependencies |
| About 80 further libraries inside OpenCV (codecs, image formats, fonts, TLS, Tesseract, Leptonica…) | bundled | LGPL, BSD, MIT, Apache-2.0 and others | FFmpeg and OpenCV dependencies; listed with their licences in `licenses/opencv/LICENSE-3RD-PARTY.txt` |
| [NumPy](https://numpy.org/) | 2.2.6 | BSD-3-Clause | numerical arrays |
| [protobuf](https://github.com/protocolbuffers/protobuf) | 4.25.9 | BSD-3-Clause | MediaPipe data structures |
| [absl-py](https://github.com/abseil/abseil-py) | 2.4.0 | Apache-2.0 | MediaPipe dependency |
| [attrs](https://www.attrs.org/) | 26.1.0 | MIT | MediaPipe dependency |
| [FlatBuffers](https://github.com/google/flatbuffers) | 25.12.19 | Apache-2.0 | MediaPipe dependency |
| [python-osc](https://github.com/attwad/python-osc) | 1.10.2 | Unlicense (public domain) | sends the OSC messages |

The Python runtime also contains, statically linked, the libraries that python-build-standalone includes in its builds (among them OpenSSL, SQLite, liblzma, bzip2, zlib, mpdecimal and expat), each under its own licence; see the [python-build-standalone](https://github.com/astral-sh/python-build-standalone) project.

### FFmpeg is GPL in this build

OpenCV's own notice describes FFmpeg as LGPL-2.1. The macOS binary shipped in `opencv-python-headless` 4.13.0.92, however, records that it was configured with `--enable-gpl --enable-version3` and with x264, x265, Rubber Band and vid.stab. That build of FFmpeg is therefore GPL-3.0-or-later, and so is the packaged tracker as a whole.

### Corresponding source

- GestureCap OSC: this repository, at the tag of each release.
- OpenCV and its bundled libraries: [opencv-python 4.13.0.92](https://github.com/opencv/opencv-python/tree/92), which builds them.
- FFmpeg 7.1.1: [ffmpeg.org/releases](https://ffmpeg.org/releases/ffmpeg-7.1.1.tar.xz). The release of the packaged tracker also attaches this source archive.
- Each other component: its official repository, linked in the table above, at the version listed.

---

## 3. Other assets in this repository

| Asset | Licence | Use |
| --- | --- | --- |
| [Iconoir](https://iconoir.com/) icons (`max/*.svg`) | MIT | interface icons of the Max patch |
