#!/bin/bash

# Exit on error
set -e

echo "Starting AppImage build process..."

# Check if ImageMagick is installed
if ! command -v convert &> /dev/null; then
    echo "ImageMagick is not installed. Please install it first."
    echo "On Fedora: sudo dnf install ImageMagick"
    exit 1
fi

# Create build directory
VERSION="1.0.1"
BUILD_DIR="build"
APP_DIR="$BUILD_DIR/temp"
echo "Creating build directory structure..."
mkdir -p "$APP_DIR"

# Create Python virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install PyQt6 PyQt6-Qt6 PyQt6-WebEngine
pip install pyinstaller

# Create PyInstaller spec file
echo "Creating PyInstaller spec file..."
cat > LatexCalc.spec << EOF
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['LatexCalc.py'],
    pathex=[],
    binaries=[],
    datas=[('cropped-logo.ico', '.')],
    hiddenimports=['PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets', 'PyQt6.sip'],
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
    name='LatexCalc',
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
)
EOF

# Build with PyInstaller
echo "Building with PyInstaller..."
pyinstaller LatexCalc.spec --distpath "$BUILD_DIR" --workpath "$BUILD_DIR/temp"

# Create the AppDir structure
echo "Creating AppDir structure..."
mkdir -p "$APP_DIR/usr/bin"
mkdir -p "$APP_DIR/usr/share/applications"
mkdir -p "$APP_DIR/usr/share/icons/hicolor/16x16/apps"
mkdir -p "$APP_DIR/usr/share/icons/hicolor/32x32/apps"
mkdir -p "$APP_DIR/usr/share/icons/hicolor/64x64/apps"
mkdir -p "$APP_DIR/usr/share/icons/hicolor/128x128/apps"
mkdir -p "$APP_DIR/usr/share/icons/hicolor/256x256/apps"

# Copy the PyInstaller build
echo "Copying PyInstaller build..."
cp $BUILD_DIR/LatexCalc "$APP_DIR/usr/bin/"

# Convert ICO to PNG for AppImage
echo "Converting icon to PNG format..."
mkdir -p "$APP_DIR/usr/share/icons/hicolor/256x256/apps"

# Convert to different sizes
convert cropped-logo.ico -resize 256x256 "$APP_DIR/usr/share/icons/hicolor/256x256/apps/latexcalc.png"

# Copy the 256x256 version as the main icon
cp "$APP_DIR/usr/share/icons/hicolor/256x256/apps/latexcalc.png" "$APP_DIR/.DirIcon"
cp "$APP_DIR/usr/share/icons/hicolor/256x256/apps/latexcalc.png" "$APP_DIR/latexcalc.png"

# Create desktop entry
echo "Creating desktop entry..."
cat > "$APP_DIR/latexcalc.desktop" << EOF
[Desktop Entry]
Type=Application
Name=LatexCalc
Comment=LaTeX Calculator
Exec=LatexCalc
Icon=latexcalc
Terminal=false
Categories=Education;Science;Math;
StartupWMClass=latexcalc
X-Window-Icon=latexcalc
X-Window-Icon-Pixmap=latexcalc
MimeType=application/x-latexcalc;
EOF

# Copy desktop entry to standard location
cp "$APP_DIR/latexcalc.desktop" "$APP_DIR/usr/share/applications/"

# Create AppRun script
echo "Creating AppRun script..."
cat > "$APP_DIR/AppRun" << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
export XDG_DATA_DIRS="${HERE}/usr/share:${XDG_DATA_DIRS:-/usr/local/share:/usr/share}"
export QT_QPA_PLATFORM_PLUGIN_PATH="${HERE}/usr/lib/qt6/plugins"
export RESOURCE_NAME="latexcalc"
export XCURSOR_PATH="${HERE}/usr/share/icons:${XCURSOR_PATH:-/usr/share/icons}"
export QT_STYLE_OVERRIDE="Fusion"
exec "${HERE}/usr/bin/LatexCalc" "$@"
EOF
chmod +x "$APP_DIR/AppRun"

# Download and extract appimagetool
echo "Downloading appimagetool..."
APPIMAGETOOL_URL="https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
APPIMAGETOOL="$BUILD_DIR/appimagetool.AppImage"
curl -L "$APPIMAGETOOL_URL" -o "$APPIMAGETOOL"
chmod +x "$APPIMAGETOOL"

# Create AppImage
echo "Creating AppImage..."
"$APPIMAGETOOL" "$APP_DIR" "$BUILD_DIR/LatexCalc_$VERSION.AppImage"

echo "Build complete! The AppImage is in the $BUILD_DIR directory."

echo "Cleaning up..."
rm -rf "$APP_DIR"
rm -f "LatexCalc.spec"
rm -rf "venv"
rm -r "$APPIMAGETOOL"
rm -r "$BUILD_DIR/LatexCalc"