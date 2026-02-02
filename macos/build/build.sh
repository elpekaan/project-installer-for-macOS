#!/bin/bash
# Laravel Bulk Installer - macOS Package Build Script
# This script builds the macOS installer package using pkgbuild and productbuild.
# Supports both ARM64 (Apple Silicon) and x86_64 (Intel) architectures.
#
# Usage: ./build.sh [--version X.Y.Z] [--sign "Developer ID Installer: ..."]
#
# Output: Creates LaravelInstaller-X.Y.Z.pkg in the build/output directory

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VERSION="${VERSION:-2.0.0}"
IDENTIFIER="com.laravel.bulk-installer"
SIGN_IDENTITY=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --version)
            VERSION="$2"
            shift 2
            ;;
        --sign)
            SIGN_IDENTITY="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --version X.Y.Z    Set package version (default: 2.0.0)"
            echo "  --sign IDENTITY    Sign package with Developer ID Installer"
            echo "  --help, -h         Show this help message"
            echo ""
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "=== Laravel Bulk Installer Package Builder ==="
echo "Version: $VERSION"
echo "Identifier: $IDENTIFIER"
echo "Project root: $PROJECT_ROOT"
echo ""

# Create build directories
BUILD_DIR="$SCRIPT_DIR/output"
PAYLOAD_DIR="$SCRIPT_DIR/payload"
SCRIPTS_DIR="$SCRIPT_DIR/pkg-scripts"
RESOURCES_DIR="$SCRIPT_DIR/pkg-resources"

rm -rf "$BUILD_DIR" "$PAYLOAD_DIR" "$SCRIPTS_DIR"
mkdir -p "$BUILD_DIR" "$PAYLOAD_DIR" "$SCRIPTS_DIR" "$RESOURCES_DIR"

echo "[1/6] Preparing payload..."

# Create payload structure (goes to ~/Library/Application Support/laravel-bulk-installer)
INSTALL_LOCATION="Library/Application Support/laravel-bulk-installer"
PAYLOAD_APP="$PAYLOAD_DIR/$INSTALL_LOCATION"
mkdir -p "$PAYLOAD_APP"
mkdir -p "$PAYLOAD_APP/launchd"

# Copy application files
cp "$PROJECT_ROOT/app.py" "$PAYLOAD_APP/"
cp -r "$PROJECT_ROOT/launchd/"* "$PAYLOAD_APP/launchd/"

# Copy scripts directory (uninstall, verify, configure)
mkdir -p "$PAYLOAD_APP/scripts"
cp "$PROJECT_ROOT/scripts/uninstall.sh" "$PAYLOAD_APP/scripts/"
cp "$PROJECT_ROOT/scripts/verify.sh" "$PAYLOAD_APP/scripts/"
cp "$PROJECT_ROOT/scripts/configure-apache.sh" "$PAYLOAD_APP/scripts/"
chmod +x "$PAYLOAD_APP/scripts/"*.sh

# Create launch.command
cat > "$PAYLOAD_APP/launch.command" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
python3 app.py
EOF
chmod +x "$PAYLOAD_APP/launch.command"

# Copy requirements.txt
cat > "$PAYLOAD_APP/requirements.txt" << 'EOF'
customtkinter
packaging
EOF

echo "[2/6] Preparing scripts..."

# Copy pre/post install scripts
cp "$PROJECT_ROOT/scripts/preinstall" "$SCRIPTS_DIR/"
cp "$PROJECT_ROOT/scripts/postinstall" "$SCRIPTS_DIR/"
chmod +x "$SCRIPTS_DIR/preinstall"
chmod +x "$SCRIPTS_DIR/postinstall"

echo "[3/6] Creating distribution resources..."

# Create welcome.html
cat > "$RESOURCES_DIR/welcome.html" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; padding: 20px; }
        h1 { color: #FF2D20; }
        .highlight { background: #f5f5f5; padding: 10px; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Laravel Bulk Project Installer</h1>
    <p>Welcome to the Laravel Bulk Project Installer for macOS.</p>
    <p>This tool helps you set up multiple Laravel projects automatically with a single click.</p>
    <div class="highlight">
        <strong>Features:</strong>
        <ul>
            <li>Clone multiple Laravel projects from Git</li>
            <li>Automatic PHP version detection</li>
            <li>Composer dependency installation</li>
            <li>Apache VirtualHost configuration</li>
            <li>Automatic /etc/hosts management</li>
        </ul>
    </div>
</body>
</html>
EOF

# Create readme.html
cat > "$RESOURCES_DIR/readme.html" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; padding: 20px; }
        h2 { color: #333; }
        code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; }
        .prereq { background: #fff3cd; padding: 15px; border-radius: 5px; margin: 10px 0; }
    </style>
</head>
<body>
    <h2>Prerequisites</h2>
    <div class="prereq">
        <strong>Required before installation:</strong>
        <ul>
            <li><strong>Homebrew</strong> - Package manager for macOS</li>
            <li><strong>Python 3</strong> - Will be installed if missing</li>
        </ul>
        <p>Install Homebrew: <code>/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"</code></p>
    </div>

    <h2>What Gets Installed</h2>
    <ul>
        <li>Application files in <code>~/Library/Application Support/laravel-bulk-installer/</code></li>
        <li>CLI command <code>laravel-installer</code></li>
        <li>Apache httpd (via Homebrew)</li>
        <li>PHP (via Homebrew)</li>
        <li>Composer (via Homebrew)</li>
    </ul>

    <h2>After Installation</h2>
    <p>Run the installer using one of these methods:</p>
    <ul>
        <li>Terminal: <code>laravel-installer</code></li>
        <li>Double-click: <code>~/Library/Application Support/laravel-bulk-installer/launch.command</code></li>
    </ul>
</body>
</html>
EOF

# Create license.html (MIT License)
cat > "$RESOURCES_DIR/license.html" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, monospace; padding: 20px; font-size: 12px; }
    </style>
</head>
<body>
<pre>
MIT License

Copyright (c) 2024 Laravel Bulk Installer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
</pre>
</body>
</html>
EOF

# Create conclusion.html
cat > "$RESOURCES_DIR/conclusion.html" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; padding: 20px; }
        h1 { color: #10b981; }
        code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; }
        .box { background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>Installation Complete!</h1>
    <p>Laravel Bulk Installer has been successfully installed on your Mac.</p>

    <div class="box">
        <strong>To launch the installer:</strong>
        <ul>
            <li>Open Terminal and run: <code>laravel-installer</code></li>
        </ul>
    </div>

    <p>Your Laravel projects will be installed to:</p>
    <ul>
        <li><strong>ARM64 Macs:</strong> <code>/opt/homebrew/var/www/</code></li>
        <li><strong>Intel Macs:</strong> <code>/usr/local/var/www/</code></li>
    </ul>

    <p>Access your projects at: <code>http://projectname.test</code></p>
</body>
</html>
EOF

echo "[4/6] Building component package..."

# Build the component package
COMPONENT_PKG="$BUILD_DIR/LaravelInstallerComponent.pkg"

pkgbuild \
    --root "$PAYLOAD_DIR" \
    --identifier "$IDENTIFIER" \
    --version "$VERSION" \
    --install-location "$HOME" \
    --scripts "$SCRIPTS_DIR" \
    "$COMPONENT_PKG"

echo "[5/6] Creating distribution XML..."

# Create distribution.xml
cat > "$BUILD_DIR/distribution.xml" << EOF
<?xml version="1.0" encoding="utf-8"?>
<installer-gui-script minSpecVersion="2">
    <title>Laravel Bulk Installer</title>
    <organization>com.laravel</organization>
    <domains enable_localSystem="false" enable_currentUserHome="true"/>
    <options customize="never" require-scripts="true" hostArchitectures="arm64,x86_64"/>

    <welcome file="welcome.html"/>
    <readme file="readme.html"/>
    <license file="license.html"/>
    <conclusion file="conclusion.html"/>

    <choices-outline>
        <line choice="default">
            <line choice="$IDENTIFIER"/>
        </line>
    </choices-outline>

    <choice id="default"/>

    <choice id="$IDENTIFIER" visible="false">
        <pkg-ref id="$IDENTIFIER"/>
    </choice>

    <pkg-ref id="$IDENTIFIER" version="$VERSION" onConclusion="none">LaravelInstallerComponent.pkg</pkg-ref>

    <installation-check script="installationCheck()"/>
    <script>
    function installationCheck() {
        if(system.compareVersions(system.version.ProductVersion, '10.15') &lt; 0) {
            my.result.message = 'This installer requires macOS 10.15 Catalina or later.';
            my.result.type = 'Fatal';
            return false;
        }
        return true;
    }
    </script>
</installer-gui-script>
EOF

echo "[6/6] Building final product package..."

# Build the final product package
FINAL_PKG="$BUILD_DIR/LaravelInstaller-$VERSION.pkg"

if [ -n "$SIGN_IDENTITY" ]; then
    echo "Signing package with: $SIGN_IDENTITY"
    productbuild \
        --distribution "$BUILD_DIR/distribution.xml" \
        --package-path "$BUILD_DIR" \
        --resources "$RESOURCES_DIR" \
        --sign "$SIGN_IDENTITY" \
        "$FINAL_PKG"
else
    productbuild \
        --distribution "$BUILD_DIR/distribution.xml" \
        --package-path "$BUILD_DIR" \
        --resources "$RESOURCES_DIR" \
        "$FINAL_PKG"
fi

# Clean up intermediate files
rm -f "$COMPONENT_PKG"
rm -f "$BUILD_DIR/distribution.xml"

echo ""
echo "=== Build Complete ==="
echo ""
echo "Package created: $FINAL_PKG"
echo "Size: $(du -h "$FINAL_PKG" | cut -f1)"
echo ""

if [ -z "$SIGN_IDENTITY" ]; then
    echo "NOTE: Package is unsigned. For distribution, sign with:"
    echo "  $0 --sign \"Developer ID Installer: Your Name (TEAMID)\""
    echo ""
fi

echo "To install, double-click the .pkg file or run:"
echo "  sudo installer -pkg \"$FINAL_PKG\" -target /"
echo ""
