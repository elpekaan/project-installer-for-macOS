#!/bin/bash
# Laravel Bulk Installer - Uninstall Script for macOS
# This script completely removes the Laravel Bulk Installer and all its components.
# Run with: sudo ./uninstall.sh [--keep-projects]

set -e

echo "=== Laravel Bulk Installer Uninstaller ==="
echo "Date: $(date)"
echo ""

# Parse arguments
KEEP_PROJECTS=false
for arg in "$@"; do
    case $arg in
        --keep-projects)
            KEEP_PROJECTS=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --keep-projects    Keep installed Laravel projects in www directory"
            echo "  --help, -h         Show this help message"
            echo ""
            exit 0
            ;;
    esac
done

# Detect architecture for Homebrew prefix
ARCH=$(uname -m)
if [ "$ARCH" = "arm64" ]; then
    HOMEBREW_PREFIX="/opt/homebrew"
else
    HOMEBREW_PREFIX="/usr/local"
fi

APP_SUPPORT="$HOME/Library/Application Support/laravel-bulk-installer"
LAUNCH_AGENTS="$HOME/Library/LaunchAgents"

echo "Architecture: $ARCH"
echo "Homebrew prefix: $HOMEBREW_PREFIX"
echo "Keep projects: $KEEP_PROJECTS"
echo ""

# Confirm uninstallation
read -p "This will remove Laravel Bulk Installer. Continue? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Uninstallation cancelled."
    exit 0
fi

echo ""
echo "Starting uninstallation..."
echo ""

# Stop services
stop_services() {
    echo "[1/7] Stopping services..."

    # Unload launchd agents
    launchctl unload "$LAUNCH_AGENTS/com.laravel.installer.httpd.plist" 2>/dev/null || true
    launchctl unload "$LAUNCH_AGENTS/com.laravel.installer.php-fpm.plist" 2>/dev/null || true

    # Stop brew services (if user wants to keep them running, they can restart)
    # Note: We don't stop httpd/php as user may want to keep them for other purposes

    echo "    Services stopped"
}

# Remove launchd plists
remove_launchd() {
    echo "[2/7] Removing launchd plists..."

    rm -f "$LAUNCH_AGENTS/com.laravel.installer.httpd.plist"
    rm -f "$LAUNCH_AGENTS/com.laravel.installer.php-fpm.plist"

    echo "    launchd plists removed"
}

# Remove Application Support files
remove_app_support() {
    echo "[3/7] Removing application files..."

    if [ -d "$APP_SUPPORT" ]; then
        rm -rf "$APP_SUPPORT"
        echo "    Removed: $APP_SUPPORT"
    else
        echo "    Application Support directory not found (already removed?)"
    fi
}

# Remove CLI symlink
remove_cli_symlink() {
    echo "[4/7] Removing CLI symlink..."

    SYMLINK_PATH="$HOMEBREW_PREFIX/bin/laravel-installer"

    if [ -L "$SYMLINK_PATH" ]; then
        sudo rm -f "$SYMLINK_PATH"
        echo "    Removed: $SYMLINK_PATH"
    else
        echo "    CLI symlink not found"
    fi
}

# Remove Apache site configurations
remove_apache_configs() {
    echo "[5/7] Removing Apache configurations..."

    SITES_AVAILABLE="$HOMEBREW_PREFIX/etc/httpd/sites-available"
    SITES_ENABLED="$HOMEBREW_PREFIX/etc/httpd/sites-enabled"

    # Get list of Laravel project configs
    if [ -d "$SITES_ENABLED" ]; then
        for conf in "$SITES_ENABLED"/*.conf; do
            if [ -f "$conf" ]; then
                CONF_NAME=$(basename "$conf")
                echo "    Removing site: $CONF_NAME"
                sudo rm -f "$SITES_ENABLED/$CONF_NAME"
                sudo rm -f "$SITES_AVAILABLE/$CONF_NAME"
            fi
        done
    fi

    # Remove the include line from httpd.conf (optional, leave it as it won't hurt)
    echo "    Site configurations removed"
}

# Remove hosts entries
remove_hosts_entries() {
    echo "[6/7] Cleaning /etc/hosts entries..."

    # Backup hosts file first
    sudo cp /etc/hosts /etc/hosts.backup.$(date +%Y%m%d%H%M%S)

    # Remove lines ending with .test that we added
    sudo sed -i.bak '/\.test$/d' /etc/hosts 2>/dev/null || true

    echo "    Hosts entries cleaned (backup created)"
}

# Remove project files (optional)
remove_projects() {
    echo "[7/7] Handling project files..."

    WWW_ROOT="$HOMEBREW_PREFIX/var/www"
    WWW_HTML="$HOMEBREW_PREFIX/var/www/html"

    if [ "$KEEP_PROJECTS" = true ]; then
        echo "    Keeping project files at: $WWW_ROOT"
    else
        read -p "    Remove all projects in $WWW_ROOT? [y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if [ -d "$WWW_ROOT" ]; then
                sudo rm -rf "$WWW_ROOT"
                echo "    Removed: $WWW_ROOT"
            fi
        else
            echo "    Keeping project files"
        fi
    fi
}

# Clean up temp files
cleanup_temp() {
    echo ""
    echo "Cleaning up temporary files..."

    rm -f /tmp/laravel-installer-*.log 2>/dev/null || true
    rm -f /tmp/*.conf 2>/dev/null || true

    echo "    Temporary files cleaned"
}

# Print summary
print_summary() {
    echo ""
    echo "=== Uninstallation Complete ==="
    echo ""
    echo "The following were removed:"
    echo "  - Application files from ~/Library/Application Support/"
    echo "  - launchd plists from ~/Library/LaunchAgents/"
    echo "  - CLI symlink from $HOMEBREW_PREFIX/bin/"
    echo "  - Apache site configurations"
    echo "  - /etc/hosts entries (*.test domains)"
    echo ""
    echo "The following were NOT removed (you may want to keep them):"
    echo "  - Homebrew packages (httpd, php, composer)"
    echo "  - Python packages (customtkinter, packaging)"
    if [ "$KEEP_PROJECTS" = true ]; then
        echo "  - Project files in $HOMEBREW_PREFIX/var/www/"
    fi
    echo ""
    echo "To completely remove Homebrew packages, run:"
    echo "  brew uninstall httpd php composer"
    echo ""
}

# Main execution
stop_services
remove_launchd
remove_app_support
remove_cli_symlink
remove_apache_configs
remove_hosts_entries
remove_projects
cleanup_temp
print_summary

exit 0
