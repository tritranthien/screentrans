# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\Admin\\Desktop\\screentrans\\screentrans\\src\\main.py'],
    pathex=['C:\\Users\\Admin\\Desktop\\screentrans\\screentrans\\src'],
    binaries=[],
    datas=[('C:\\Users\\Admin\\Desktop\\screentrans\\screentrans\\config.json', '.'), ('C:\\Users\\Admin\\Desktop\\screentrans\\screentrans\\src', 'src')],
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
    [],
    exclude_binaries=True,
    name='ScreenTranslator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='NONE',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ScreenTranslator',
)
