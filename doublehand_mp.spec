# -*- mode: python ; coding: utf-8 -*-

import os


# Release builds must use a Developer ID identity supplied locally.
# The identity is intentionally not stored in the repository.
codesign_identity = os.environ.get('GESTURECAP_CODESIGN_IDENTITY')

# Test builds stay unsigned (ad-hoc) until the tracker is known to work and
# to be portable. They must be asked for explicitly and are never released.
unsigned_test_build = os.environ.get('GESTURECAP_UNSIGNED_TEST_BUILD') == '1'

if not codesign_identity and not unsigned_test_build:
    raise RuntimeError(
        'GESTURECAP_CODESIGN_IDENTITY must be set for a signed release build '
        '(or GESTURECAP_UNSIGNED_TEST_BUILD=1 for a local test build).'
    )

# Packages MediaPipe 0.10.14 declares but the tracker never uses.
# matplotlib is replaced by utils/no_matplotlib.py.
EXCLUDES = [
    'matplotlib',
    'jax',
    'jaxlib',
    'scipy',
    'sounddevice',
    'PIL',
    'tkinter',
]


a = Analysis(
    ['doublehand_mp.py'],
    pathex=[],
    binaries=[],
    datas=[('models', 'models')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=EXCLUDES,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='doublehand_mp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=codesign_identity,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='doublehand_mp',
)