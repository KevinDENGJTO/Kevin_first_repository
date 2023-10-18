# -*- mode: python ; coding: utf-8 -*-

SETUP_DIR = 'C:\\Users\\石佳星\\PycharmProjects\\坦克大战游戏\\'

a = Analysis(
    ['坦克大战-01.py'],
    pathex=['C:\\Users\\石佳星\\PycharmProjects\\坦克大战游戏\\'],
    binaries=[],
    datas=[(SETUP_DIR+'image','image'),(SETUP_DIR+'music','music')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='坦克大战-01',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
