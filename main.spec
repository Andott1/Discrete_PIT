# -*- mode: python ; coding: utf-8 -*-

import os
import glob
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Function to collect all assets correctly
def collect_all_assets():
    assets = []
    asset_base = 'Assets'  # Base directory for assets
    
    # Check if the Assets directory exists
    if not os.path.exists(asset_base):
        print(f"WARNING: Assets directory not found at {os.path.abspath(asset_base)}")
        return []
    
    # Add the .qrc file itself (if it exists)
    qrc_file = 'Assets.qrc'
    if os.path.exists(qrc_file):
        print(f"Adding .qrc file: {qrc_file}")
        assets.append((qrc_file, 'resources.qrc'))

    # Define the folders to include
    asset_folders = [
        'App Screenshots',
        'Fonts',
        'Icons',
        'Screens',
    ]
    
    # Process each folder
    for folder in asset_folders:
        folder_path = os.path.join(asset_base, folder)
        if os.path.exists(folder_path):
            print(f"Processing folder: {folder_path}")
            # Walk through all files in this folder
            for root, _, files in os.walk(folder_path):
                for file in files:
                    # Get the full path to the file
                    file_path = os.path.join(root, file)
                    # Get the destination path - preserve the folder structure
                    dest_path = os.path.join('Assets', os.path.relpath(file_path, asset_base))
                    # Add to the assets list
                    assets.append((file_path, dest_path))
                    print(f"Adding asset: {file_path} -> {dest_path}")
        else:
            print(f"Folder not found: {folder_path}")
    
    print(f"Total assets collected: {len(assets)}")
    return assets

# Collect all assets
datas = collect_all_assets()

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,  # Add collected assets
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

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Let\'s Play Lotto v1.0.0 – Portable',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for a windowed application
    icon='Assets/Icons/app_icon.ico',
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)