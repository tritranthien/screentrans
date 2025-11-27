# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\t480\\Desktop\\person\\screentrans\\src\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\t480\\Desktop\\person\\screentrans\\config.json', '.'), ('C:\\Users\\t480\\Desktop\\person\\screentrans\\src', 'src')],
    hiddenimports=['PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets', 'PIL', 'PIL.Image', 'cv2', 'numpy', 'pytesseract', 'deep_translator', 'google.generativeai', 'mss', 'multiprocessing', 'queue'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'scipy', 'pandas'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ScreenTranslator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='NONE',
)
