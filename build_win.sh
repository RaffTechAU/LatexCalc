#!/bin/bash

# Exit on error
set -e

echo "Starting Windows executable build process..."

# Check if Wine is installed
if ! command -v wine &> /dev/null; then
    echo "Wine is not installed. Please install it first."
    echo "On Fedora: sudo dnf install wine"
    exit 1
fi

convert_version() {
  version=$1
  IFS='.' read -ra parts <<< "$version"
  parts+=("0")
  echo "(${parts[0]}, ${parts[1]}, ${parts[2]}, ${parts[3]})"
}

# Create build directory
VERSION="1.0.2"
BUILD_DIR="build"
echo "Creating build directory..."
mkdir -p "$BUILD_DIR"

# Set up Wine environment
WINE_PREFIX="$HOME/.wine-pyinstaller"
echo "Setting up Wine environment..."
rm -rf "$WINE_PREFIX" 2>/dev/null || true
WINEPREFIX="$WINE_PREFIX" wineboot --init

# Download and install Python for Windows
echo "Downloading Python for Windows..."
PYTHON_URL="https://www.python.org/ftp/python/3.11.4/python-3.11.4-amd64.exe"
PYTHON_INSTALLER="$WINE_PREFIX/python-installer.exe"
curl -L "$PYTHON_URL" -o "$PYTHON_INSTALLER"

echo "Installing Python in Wine environment..."
WINEPREFIX="$WINE_PREFIX" wine "$PYTHON_INSTALLER" /quiet InstallAllUsers=1 PrependPath=1

# Install PyInstaller in Wine Python
echo "Installing PyInstaller in Wine Python..."
WINEPREFIX="$WINE_PREFIX" wine python -m pip install --upgrade pip
WINEPREFIX="$WINE_PREFIX" wine python -m pip install pyinstaller PyQt6 matplotlib latex2sympy2_extended[antlr4_13_2]

# Create PyInstaller spec file
echo "Creating PyInstaller spec file..."
cat > LatexCalc.spec << EOF
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['LatexCalc.py'],
    pathex=[],
    binaries=[],
    datas=[('cropped-logo.ico', '.')],
    hiddenimports=['PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets', 'PyQt6.sip', 'matplotlib', 'latex2sympy2_extended'],
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
    name='LatexCalc_$VERSION.exe',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='x86_64',
    codesign_identity=None,
    entitlements_file=None,
    icon='cropped-logo.ico',
    uac_admin=False,
    version='file_version_info.txt'
)
EOF

# Create version info file for Windows
echo "Creating version info file..."
cat > file_version_info.txt << EOF
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=$(convert_version $VERSION),
    prodvers=$(convert_version $VERSION),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [StringStruct(u'CompanyName', u'RaffTechAU'),
           StringStruct(u'FileDescription', u'LaTeX Calculator'),
           StringStruct(u'FileVersion', u'$VERSION'),
           StringStruct(u'InternalName', u'LatexCalc'),
           StringStruct(u'LegalCopyright', u''),
           StringStruct(u'OriginalFilename', u'LatexCalc.exe'),
           StringStruct(u'ProductName', u'LaTeX Calculator'),
           StringStruct(u'ProductVersion', u'$VERSION')])
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
EOF

# Build with PyInstaller using Wine
echo "Building with PyInstaller using Wine..."
WINEPREFIX="$WINE_PREFIX" wine pyinstaller LatexCalc.spec --distpath "$BUILD_DIR" --workpath "$BUILD_DIR/temp"

echo "Build complete! The Windows executable is in the $BUILD_DIR directory." 

echo "Cleaning up..."
rm -f "file_version_info.txt"
rm -f "LatexCalc.spec"
rm -rf "$BUILD_DIR/temp"