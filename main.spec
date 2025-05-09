# -*- mode: python ; coding: utf-8 -*-

import os
import sys
import glob
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.building.build_main import BUNDLE

block_cipher = None

# Function to collect all assets correctly
def collect_all_assets():
    assets = []
    asset_base = 'Assets'
    
    if not os.path.exists(asset_base):
        print(f"WARNING: Assets directory not found at {os.path.abspath(asset_base)}")
        return []

    qrc_file = 'Assets.qrc'
    if os.path.exists(qrc_file):
        print(f"Adding .qrc file: {qrc_file}")
        assets.append((qrc_file, 'resources.qrc'))

    asset_folders = [
        'App Screenshots',
        'Fonts',
        'Icons',
        'Screens',
    ]
    
    for folder in asset_folders:
        folder_path = os.path.join(asset_base, folder)
        if os.path.exists(folder_path):
            print(f"Processing folder: {folder_path}")
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    dest_path = os.path.join('Assets', os.path.relpath(file_path, asset_base))
                    assets.append((file_path, dest_path))
                    print(f"Adding asset: {file_path} -> {dest_path}")
        else:
            print(f"Folder not found: {folder_path}")
    
    print(f"Total assets collected: {len(assets)}")
    return assets

# Shared
datas = collect_all_assets()

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Platform-specific builds
if sys.platform == 'win32':
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name="Let's Play Lotto v1.0.0b – Portable",
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        icon='Assets/Icons/app_icon.ico',
    )
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name="LetsPlayLotto"
    )

elif sys.platform == 'darwin':
    # macOS executable creation
    mac_exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name="LetsPlayLotto",
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        icon='Assets/Icons/app_icon.icns',  # Ensure this is the correct path to your .icns file
    )

    # Create the macOS app bundle
    app = BUNDLE(
        mac_exe,
        name='LetsPlayLotto.app',
        icon='Assets/Icons/app_icon.icns',  # Ensure this path is correct
        bundle_identifier='com.cs223.lotto',
    )

    # Collect the final app bundle
    coll = COLLECT(
        app,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='LetsPlayLotto'
    )