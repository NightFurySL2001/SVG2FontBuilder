# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

from kivy_deps import sdl2, glew
from kivymd import hooks_path as kivymd_hooks_path

a = Analysis(
    ['svgbuilder.py'],
    pathex=[],
    binaries=[],
    datas=[('*.kv', '.'), 
    ('aglfn.txt', '.'),
    ('locales', 'locales'),
    ('overrides/Roboto-*.ttf', 'kivymd/fonts'),
    ('overrides/SDL2.dll', '.'),
    ('S2F.png', '.'),
    ('LICENSE', '.'),],
    hiddenimports=[],
    hookspath=[kivymd_hooks_path],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='svgbuilder',
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
    icon="S2F.ico",
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
    strip=False,
    upx=True,
    upx_exclude=[],
    name='svgbuilder',
)
