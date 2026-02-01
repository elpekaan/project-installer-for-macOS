#!/bin/bash
# Laravel Bulk Installer - One-Command macOS Build
#
# Usage:
#   ./build-macos.sh                    # Build unsigned package
#   ./build-macos.sh --version 2.1.0    # Build with specific version
#   ./build-macos.sh --sign "..."       # Build signed package
#
# This script must be run on macOS.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MACOS_DIR="$SCRIPT_DIR/macos"
BUILD_DIR="$MACOS_DIR/build"
VERSION="${VERSION:-2.0.0}"

# Parse arguments
ARGS=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --version)
            VERSION="$2"
            ARGS="$ARGS --version $2"
            shift 2
            ;;
        --sign)
            ARGS="$ARGS --sign \"$2\""
            shift 2
            ;;
        --help|-h)
            echo "Laravel Bulk Installer - macOS Build Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --version X.Y.Z    Set package version (default: 2.0.0)"
            echo "  --sign IDENTITY    Sign with Developer ID Installer"
            echo "  --help, -h         Show this help"
            echo ""
            echo "Examples:"
            echo "  $0"
            echo "  $0 --version 2.1.0"
            echo "  $0 --sign \"Developer ID Installer: Name (TEAMID)\""
            echo ""
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check if running on macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo "ERROR: This script must be run on macOS."
    echo "The .pkg package format is macOS-specific and requires"
    echo "pkgbuild and productbuild which are only available on macOS."
    exit 1
fi

echo "=== Laravel Bulk Installer - macOS Build ==="
echo ""
echo "Project: $SCRIPT_DIR"
echo "Version: $VERSION"
echo ""

# Ensure build script is executable
chmod +x "$BUILD_DIR/build.sh"

# Run the build
cd "$BUILD_DIR"
eval "./build.sh $ARGS"

# Show output location
echo ""
echo "Build artifacts located in:"
echo "  $BUILD_DIR/output/"
echo ""
ls -la "$BUILD_DIR/output/"*.pkg 2>/dev/null || echo "(no packages found)"
