"""
collect_licenses.py

Copies the licence texts into a packaged tracker, so that they travel with
every release (see THIRD_PARTY_NOTICES.md).

Run it with the Python of the build environment, after PyInstaller and
before signing and compressing the tracker:

    .venv/bin/python tools/collect_licenses.py /path/to/dist/doublehand_mp

It adds to that folder:
    LICENSE                    GestureCap OSC's licence (GPL-3.0-or-later)
    THIRD_PARTY_NOTICES.md     what the tracker embeds, and under which licence
    licenses/<component>/      the licence files of each embedded component
"""

import shutil
import sys
from importlib import metadata
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Python distributions bundled in the tracker → folder name in licenses/
PACKAGES = {
    "mediapipe": "mediapipe",
    "opencv-python-headless": "opencv",
    "numpy": "numpy",
    "protobuf": "protobuf",
    "absl-py": "absl-py",
    "attrs": "attrs",
    "flatbuffers": "flatbuffers",
    "python-osc": "python-osc",
    "pyinstaller": "pyinstaller",
}

LICENSE_WORDS = ("license", "licence", "copying", "notice")

# Apache-2.0 components that ship no licence file of their own
APACHE_WITHOUT_FILE = {
    "flatbuffers": "FlatBuffers 25.12.19 is licensed under the Apache License 2.0 "
                   "(https://github.com/google/flatbuffers). Its wheel contains no "
                   "licence file; the Apache License 2.0 text follows.\n\n",
    "hand-landmarker-model": "The MediaPipe hand landmarker model (models/hand_landmarker.task) "
                             "is licensed under the Apache License 2.0, as stated on its model card: "
                             "https://storage.googleapis.com/mediapipe-assets/"
                             "Model%20Card%20Hand%20Tracking%20(Lite_Full)%20with%20Fairness%20Oct%202021.pdf\n"
                             "The Apache License 2.0 text follows.\n\n",
}


def licence_files(dist):
    for file in dist.files or []:
        if file.name.lower().startswith(LICENSE_WORDS):
            yield file


def unique_name(file, out):
    # Two licence files with the same name (in different folders) both survive
    name = file.name
    if (out / name).exists():
        name = "-".join(file.parts[-3:-1] + (file.name,)).replace(".dist-info", "")
    return name


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)

    target = Path(sys.argv[1]).resolve()
    if not (target / "doublehand_mp").exists():
        sys.exit(f"Not a packaged tracker folder: {target}")

    licenses = target / "licenses"
    if licenses.exists():
        shutil.rmtree(licenses)
    licenses.mkdir()

    shutil.copy2(REPO / "LICENSE", target / "LICENSE")
    shutil.copy2(REPO / "THIRD_PARTY_NOTICES.md", target / "THIRD_PARTY_NOTICES.md")

    # The Python runtime
    python_licence = Path(sys.base_prefix) / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "LICENSE.txt"
    (licenses / "python").mkdir()
    shutil.copy2(python_licence, licenses / "python" / "LICENSE.txt")

    # Python packages
    for package, folder in PACKAGES.items():
        dist = metadata.distribution(package)
        out = licenses / folder
        out.mkdir()
        files = list(licence_files(dist))
        copied = set()
        for file in files:
            text = Path(dist.locate_file(file)).read_bytes()
            if text in copied:
                continue  # the same licence shipped twice in one package
            copied.add(text)
            shutil.copy2(dist.locate_file(file), out / unique_name(file, out))
        if not files and dist.metadata.get("License"):
            # e.g. python-osc: the licence text is in its metadata
            (out / "LICENSE.txt").write_text(dist.metadata["License"] + "\n")

    # Apache-2.0 components without a licence file: note + Apache text
    apache_text = (licenses / "absl-py" / "LICENSE").read_text()
    for folder, note in APACHE_WITHOUT_FILE.items():
        out = licenses / folder
        out.mkdir(exist_ok=True)
        (out / "LICENSE.txt").write_text(note + apache_text)

    missing = [p.name for p in sorted(licenses.iterdir()) if not any(p.iterdir())]
    if missing:
        sys.exit(f"No licence text found for: {', '.join(missing)}")

    count = sum(1 for _ in licenses.rglob("*") if _.is_file())
    print(f"Licences copied into {target}: LICENSE, THIRD_PARTY_NOTICES.md and {count} files in licenses/")


if __name__ == "__main__":
    main()
