# Laravel Bulk Project Installer - macOS

A Python-based GUI tool to automate the setup of multiple Laravel projects on macOS. This application handles cloning, environment setup, PHP management, Apache VirtualHosts, symlinking, and Composer dependencies automatically.

Ported from Linux (Ubuntu/Debian) to macOS with full functional equivalence.

---

## Features

- Add multiple Laravel projects with project name and Git repository URL
- Automatically clone or pull the latest version of each project
- Copy `.env.example` to `.env` if `.env` does not exist
- Detect required PHP version from `composer.json` and switch PHP accordingly
- Automatic PHP management via Homebrew
- Create symlinks from project `public` folder to web root
- Add projects to `/etc/hosts`
- Configure Apache VirtualHosts for each project
- Set proper file permissions and ownership
- Bulk setup all added projects with a single click
- Supports both Apple Silicon (ARM64) and Intel (x86_64) Macs

---

## Requirements

- **macOS 10.15 Catalina or later**
- **Homebrew** - Package manager for macOS
- **Python 3.x** with tkinter (installed via Homebrew if missing)
- **Admin privileges** for system modifications

### Automatic Dependencies

The following are installed automatically during setup:

- Apache httpd (via Homebrew)
- PHP (via Homebrew, multiple versions supported)
- Composer (via Homebrew)
- Git (via Xcode Command Line Tools or Homebrew)

---

## Installation

### Option 1: Package Installer (Recommended)

1. Download `LaravelInstaller-X.Y.Z.pkg` from releases
2. Double-click to run the installer
3. Follow the installation wizard

### Option 2: Manual Installation

1. Install Homebrew if not already installed:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Clone this repository:
   ```bash
   git clone <your-repo-url> ~/laravel-bulk-installer
   cd ~/laravel-bulk-installer/macos
   ```

3. Run the application:
   ```bash
   python3 app.py
   ```

4. On first run, choose "Install to System" to set up the CLI command.

### Option 3: Build from Source

```bash
cd macos/build
make build
sudo installer -pkg output/LaravelInstaller-2.0.0.pkg -target /
```

---

## Usage

### Launch the Application

**From Terminal:**
```bash
laravel-installer
```

**Or run directly:**
```bash
python3 ~/Library/Application\ Support/laravel-bulk-installer/app.py
```

**Or double-click:**
```
~/Library/Application Support/laravel-bulk-installer/launch.command
```

### Adding Projects

1. Enter the project name (e.g., `my-laravel-app`)
2. Enter the Git repository URL
3. Click **Add to Queue**
4. Repeat for additional projects
5. Click **START INSTALLATION**
6. Enter your admin password when prompted

### Accessing Projects

After installation, access your projects at:
```
http://projectname.test
```

---

## Directory Structure

### Application Files

| Location | Purpose |
|----------|---------|
| `~/Library/Application Support/laravel-bulk-installer/` | Application files |
| `~/Library/LaunchAgents/` | launchd service plists |

### Web Server (Homebrew)

**Apple Silicon (ARM64):**

| Location | Purpose |
|----------|---------|
| `/opt/homebrew/var/www/` | Project source files |
| `/opt/homebrew/var/www/html/` | Public symlinks |
| `/opt/homebrew/etc/httpd/` | Apache configuration |
| `/opt/homebrew/etc/httpd/sites-available/` | VirtualHost configs |
| `/opt/homebrew/etc/httpd/sites-enabled/` | Enabled sites |
| `/opt/homebrew/var/log/httpd/` | Apache logs |
| `/opt/homebrew/opt/php@X.Y/` | PHP versions |

**Intel (x86_64):**

| Location | Purpose |
|----------|---------|
| `/usr/local/var/www/` | Project source files |
| `/usr/local/var/www/html/` | Public symlinks |
| `/usr/local/etc/httpd/` | Apache configuration |
| `/usr/local/etc/httpd/sites-available/` | VirtualHost configs |
| `/usr/local/etc/httpd/sites-enabled/` | Enabled sites |
| `/usr/local/var/log/httpd/` | Apache logs |
| `/usr/local/opt/php@X.Y/` | PHP versions |

---

## What Happens During Setup

1. **Git clone or pull** - Ensures you have the latest project files
2. **Copy `.env`** - If `.env` is missing, copies `.env.example`
3. **PHP version detection** - Reads `composer.json` and ensures correct PHP version
4. **Composer install** - Installs all PHP dependencies
5. **Symlink public folder** - Links project/public to web root
6. **Hosts update** - Adds `127.0.0.1 <project>.test` to `/etc/hosts`
7. **Permissions** - Sets `775` permissions with appropriate ownership
8. **Apache VirtualHost** - Creates `.conf`, enables site, and reloads Apache

---

## Uninstallation

### Using the Uninstall Script

```bash
# Keep project files
~/Library/Application\ Support/laravel-bulk-installer/scripts/uninstall.sh --keep-projects

# Remove everything
~/Library/Application\ Support/laravel-bulk-installer/scripts/uninstall.sh
```

### Manual Uninstallation

```bash
# Stop services
brew services stop httpd
brew services stop php

# Remove application
rm -rf ~/Library/Application\ Support/laravel-bulk-installer

# Remove CLI symlink
sudo rm /opt/homebrew/bin/laravel-installer  # ARM64
# or
sudo rm /usr/local/bin/laravel-installer     # Intel

# Remove launchd plists
rm ~/Library/LaunchAgents/com.laravel.installer.*.plist

# Clean /etc/hosts (remove .test entries)
sudo sed -i.bak '/\.test$/d' /etc/hosts
```

---

## Troubleshooting

### Homebrew Not Found

Install Homebrew first:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Apache Not Starting

Check Apache configuration:
```bash
apachectl configtest
brew services restart httpd
```

View logs:
```bash
tail -f /opt/homebrew/var/log/httpd/error_log   # ARM64
tail -f /usr/local/var/log/httpd/error_log      # Intel
```

### PHP Version Issues

List installed PHP versions:
```bash
brew list | grep php
```

Install a specific version:
```bash
brew install php@8.2
```

Link a version:
```bash
brew link php@8.2
```

### Permission Denied

Ensure web directory permissions:
```bash
sudo chown -R $(whoami):staff /opt/homebrew/var/www
sudo chmod -R 775 /opt/homebrew/var/www
```

### .test Domain Not Resolving

Verify `/etc/hosts` entry:
```bash
cat /etc/hosts | grep .test
```

Flush DNS cache:
```bash
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
```

---

## Building the Package

### Prerequisites

- Xcode Command Line Tools: `xcode-select --install`
- For signed packages: Apple Developer ID Installer certificate

### Build Commands

```bash
cd macos/build

# Build unsigned package
make build

# Build with specific version
make build VERSION=2.1.0

# Build signed package
make build-signed SIGN_IDENTITY="Developer ID Installer: Your Name (TEAMID)"

# Create DMG
make dmg

# Clean build artifacts
make clean
```

### One-Command Build

```bash
./build.sh --version 2.0.0
```

---

## Tips

- Ensure SSH keys are properly configured for private repositories
- Install PHP versions beforehand if you know what's needed: `brew install php@8.1 php@8.2`
- Projects are cloned to `$HOMEBREW_PREFIX/var/www/`
- VirtualHost configs use `.test` TLD for local development

---

## License

MIT License - See LICENSE file for details.
