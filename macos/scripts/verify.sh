#!/bin/bash
# Laravel Bulk Installer - Installation Verification Script
# Checks that all components are properly installed and configured.
#
# Usage: ./verify.sh

set -e

echo "=== Laravel Bulk Installer - Installation Verification ==="
echo ""

# Detect architecture
ARCH=$(uname -m)
if [ "$ARCH" = "arm64" ]; then
    HOMEBREW_PREFIX="/opt/homebrew"
    echo "Architecture: Apple Silicon (ARM64)"
else
    HOMEBREW_PREFIX="/usr/local"
    echo "Architecture: Intel (x86_64)"
fi
echo "Homebrew prefix: $HOMEBREW_PREFIX"
echo ""

ERRORS=0
WARNINGS=0

# Helper functions
check_ok() {
    echo "[OK] $1"
}

check_fail() {
    echo "[FAIL] $1"
    ERRORS=$((ERRORS + 1))
}

check_warn() {
    echo "[WARN] $1"
    WARNINGS=$((WARNINGS + 1))
}

echo "--- Checking Prerequisites ---"
echo ""

# Check Homebrew
if command -v brew &> /dev/null; then
    check_ok "Homebrew installed: $(brew --version | head -1)"
else
    check_fail "Homebrew not installed"
fi

# Check Python
if command -v python3 &> /dev/null; then
    check_ok "Python installed: $(python3 --version)"
else
    check_fail "Python 3 not installed"
fi

# Check tkinter
if python3 -c "import tkinter" 2>/dev/null; then
    check_ok "Python tkinter available"
else
    check_warn "Python tkinter not available (may need: brew install python-tk)"
fi

# Check customtkinter
if python3 -c "import customtkinter" 2>/dev/null; then
    check_ok "customtkinter package installed"
else
    check_warn "customtkinter not installed (will be auto-installed on first run)"
fi

echo ""
echo "--- Checking Application Files ---"
echo ""

APP_SUPPORT="$HOME/Library/Application Support/laravel-bulk-installer"

if [ -f "$APP_SUPPORT/app.py" ]; then
    check_ok "Application installed at $APP_SUPPORT/app.py"
else
    check_fail "Application not found at $APP_SUPPORT/app.py"
fi

if [ -f "$APP_SUPPORT/launch.command" ]; then
    check_ok "Launch script exists"
    if [ -x "$APP_SUPPORT/launch.command" ]; then
        check_ok "Launch script is executable"
    else
        check_warn "Launch script is not executable"
    fi
else
    check_warn "Launch script not found"
fi

# Check CLI symlink
CLI_PATH="$HOMEBREW_PREFIX/bin/laravel-installer"
if [ -L "$CLI_PATH" ]; then
    check_ok "CLI symlink exists: $CLI_PATH"
else
    check_warn "CLI symlink not found at $CLI_PATH"
fi

echo ""
echo "--- Checking Web Server Components ---"
echo ""

# Check Apache httpd
if command -v httpd &> /dev/null; then
    check_ok "Apache httpd installed: $(httpd -v 2>&1 | head -1)"
else
    if [ -f "$HOMEBREW_PREFIX/bin/httpd" ]; then
        check_ok "Apache httpd installed (Homebrew): $HOMEBREW_PREFIX/bin/httpd"
    else
        check_warn "Apache httpd not installed (will be installed on first use)"
    fi
fi

# Check Apache config directory
if [ -d "$HOMEBREW_PREFIX/etc/httpd" ]; then
    check_ok "Apache config directory exists"
else
    check_warn "Apache config directory not found"
fi

# Check sites-available directory
if [ -d "$HOMEBREW_PREFIX/etc/httpd/sites-available" ]; then
    check_ok "Sites-available directory exists"
else
    check_warn "Sites-available directory not found (will be created on first use)"
fi

# Check sites-enabled directory
if [ -d "$HOMEBREW_PREFIX/etc/httpd/sites-enabled" ]; then
    check_ok "Sites-enabled directory exists"
else
    check_warn "Sites-enabled directory not found (will be created on first use)"
fi

# Check httpd.conf for sites-enabled include
HTTPD_CONF="$HOMEBREW_PREFIX/etc/httpd/httpd.conf"
if [ -f "$HTTPD_CONF" ]; then
    if grep -q "sites-enabled" "$HTTPD_CONF"; then
        check_ok "Apache configured to include sites-enabled"
    else
        check_warn "Apache not configured to include sites-enabled (will be configured on first use)"
    fi
fi

echo ""
echo "--- Checking PHP ---"
echo ""

# Check PHP
if command -v php &> /dev/null; then
    check_ok "PHP installed: $(php -v | head -1)"
else
    if [ -f "$HOMEBREW_PREFIX/opt/php/bin/php" ]; then
        check_ok "PHP installed (Homebrew): $($HOMEBREW_PREFIX/opt/php/bin/php -v | head -1)"
    else
        check_warn "PHP not installed (will be installed on first use)"
    fi
fi

# List installed PHP versions
echo ""
echo "Installed PHP versions:"
for dir in "$HOMEBREW_PREFIX/opt/php@"*; do
    if [ -d "$dir" ]; then
        ver=$(basename "$dir" | sed 's/php@//')
        php_bin="$dir/bin/php"
        if [ -x "$php_bin" ]; then
            echo "  - PHP $ver: $php_bin"
        fi
    fi
done 2>/dev/null || echo "  (none found)"

# Check Composer
if command -v composer &> /dev/null; then
    check_ok "Composer installed: $(composer --version 2>/dev/null | head -1)"
else
    check_warn "Composer not installed (will be installed on first use)"
fi

echo ""
echo "--- Checking Git ---"
echo ""

if command -v git &> /dev/null; then
    check_ok "Git installed: $(git --version)"
else
    check_fail "Git not installed"
fi

echo ""
echo "--- Checking Web Directories ---"
echo ""

WWW_ROOT="$HOMEBREW_PREFIX/var/www"
WWW_HTML="$HOMEBREW_PREFIX/var/www/html"

if [ -d "$WWW_ROOT" ]; then
    check_ok "Web root exists: $WWW_ROOT"
    PROJECTS=$(ls -1 "$WWW_ROOT" 2>/dev/null | grep -v "^html$" | wc -l | tr -d ' ')
    echo "     Found $PROJECTS project(s)"
else
    check_warn "Web root not found (will be created on first use)"
fi

if [ -d "$WWW_HTML" ]; then
    check_ok "HTML directory exists: $WWW_HTML"
else
    check_warn "HTML directory not found (will be created on first use)"
fi

echo ""
echo "--- Checking Services ---"
echo ""

# Check if httpd is running
if brew services list 2>/dev/null | grep -q "httpd.*started"; then
    check_ok "Apache httpd service is running"
else
    check_warn "Apache httpd service is not running"
fi

# Check if php is running
if brew services list 2>/dev/null | grep -q "php.*started"; then
    check_ok "PHP service is running"
else
    check_warn "PHP service is not running"
fi

echo ""
echo "=== Verification Summary ==="
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "All checks passed! Installation is complete."
elif [ $ERRORS -eq 0 ]; then
    echo "Installation is functional with $WARNINGS warning(s)."
    echo "Warnings indicate optional components that will be installed on first use."
else
    echo "Found $ERRORS error(s) and $WARNINGS warning(s)."
    echo "Please fix the errors before using the application."
fi

echo ""
echo "To launch the installer, run:"
echo "  laravel-installer"
echo ""

exit $ERRORS
