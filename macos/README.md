# Laravel Bulk Project Installer - macOS

A Python-based GUI tool to automate the setup of multiple Laravel projects on macOS. This application handles cloning, environment setup, PHP management, Apache VirtualHosts, symlinking, and Composer dependencies automatically.

Ported from Linux (Ubuntu/Debian) to macOS with full functional equivalence.

---

## Features

- **Bulk Installation**: Add multiple Laravel projects and install them all with a single click
- **Auto Git Clone/Pull**: Automatically clone or pull the latest version of each project
- **Environment Setup**: Copy `.env.example` to `.env` and generate `APP_KEY` automatically
- **Smart PHP Detection**: Read required PHP version from `composer.json` and switch PHP accordingly
- **Homebrew Integration**: Automatic PHP and dependency management via Homebrew
- **Apache VirtualHost**: Auto-generate and configure VirtualHosts for each project
- **Symlink Management**: Create symlinks from project `public` folder to web root
- **Hosts File Update**: Add projects to `/etc/hosts` automatically
- **Permission Handling**: Set proper file permissions and ownership
- **Multi-Architecture**: Supports both Apple Silicon (ARM64) and Intel (x86_64) Macs
- **Security Hardened**: Input sanitization, path traversal protection, safe shell commands

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

## Prerequisites Setup

Before using the installer, ensure your macOS is ready:

### 1. Install Xcode Command Line Tools

```bash
xcode-select --install
```

### 2. Install Homebrew

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**For Apple Silicon Macs**, add Homebrew to PATH:
```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

### 3. Install Apache and PHP

```bash
brew install httpd php composer
brew services start httpd
brew services start php
```

### 4. Configure Apache for Sites

Add the following to your Apache config (`/opt/homebrew/etc/httpd/httpd.conf`):

```apache
# At the end of the file, add:
IncludeOptional /opt/homebrew/etc/httpd/sites-enabled/*.conf
```

Create the sites directories:
```bash
mkdir -p /opt/homebrew/etc/httpd/sites-available
mkdir -p /opt/homebrew/etc/httpd/sites-enabled
```

### 5. Configure SSH Keys (For Private Repositories)

If you'll be cloning private repositories via SSH:

```bash
# Generate SSH key if you don't have one
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copy public key to clipboard
pbcopy < ~/.ssh/id_ed25519.pub

# Add this key to your GitHub/GitLab account
```

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

### Step 1: Launch the Application

Choose one of the following methods:

**Method A - Terminal Command (Recommended):**
```bash
laravel-installer
```

**Method B - Direct Python Execution:**
```bash
python3 ~/Library/Application\ Support/laravel-bulk-installer/app.py
```

**Method C - Double-Click:**
```
Open Finder → Navigate to:
~/Library/Application Support/laravel-bulk-installer/
Double-click "launch.command"
```

---

### Step 2: First Run - Installation Dialog

On first run, you'll see a welcome dialog with two options:

| Option | Description |
|--------|-------------|
| **Run Once (Try)** | Run the app without installing to system |
| **Install to System** | Install to `~/Library/Application Support` and create CLI command |

**Recommendation:** Click **"Install to System"** for easy future access.

---

### Step 3: Add Projects to Queue

The main window has two sections: **Add New Project** and **Installation Queue**.

#### 3.1 Enter Project Details

| Field | Description | Example |
|-------|-------------|---------|
| **Project Name** | A unique name for your project (letters, numbers, hyphens only) | `ecommerce-api` |
| **Git Repository URL** | The Git clone URL (HTTPS or SSH) | `git@github.com:user/repo.git` |

#### 3.2 Click "Add to Queue"

The project will appear in the **Installation Queue** below.

#### 3.3 Repeat for Multiple Projects

Add as many projects as needed. Each will be processed sequentially.

**Example Queue:**
```
┌─────────────────────────────────────────────────────────┐
│ Installation Queue                          3 Projects  │
├─────────────────────────────────────────────────────────┤
│ ecommerce-api    git@github.com:user/ecommerce.git  [X] │
│ blog-backend     git@github.com:user/blog.git       [X] │
│ admin-panel      https://github.com/user/admin.git  [X] │
└─────────────────────────────────────────────────────────┘
```

---

### Step 4: Start Installation

1. Click the green **"START INSTALLATION"** button
2. Enter your **macOS admin password** when prompted
3. The app switches to **Installation Logs** view automatically

---

### Step 5: Monitor Progress

The log window shows real-time progress for each project:

```
[14:32:01] --- Starting Bulk Installation (macOS) ---
[14:32:02] Installing ecommerce-api...
[14:32:03] EXEC: git clone git@github.com:user/ecommerce.git /opt/homebrew/var/www/ecommerce-api
[14:32:15] PHP Required: 8.2
[14:32:16] Ensuring php@8.2 is installed...
[14:32:20] EXEC: /opt/homebrew/opt/php@8.2/bin/php /opt/homebrew/bin/composer install -d /opt/homebrew/var/www/ecommerce-api
[14:33:45] Generating Laravel APP_KEY...
[14:33:46] Added hosts entry: 127.0.0.1 ecommerce-api.test
[14:33:47] Completed: ecommerce-api
```

**Log Color Codes:**
- 🔵 **Blue**: Commands being executed
- ⚪ **White**: Normal output
- 🟢 **Green**: Success messages
- 🔴 **Red**: Errors or warnings

---

### Step 6: Handle PHP Version Issues (If Needed)

If Composer fails due to PHP version mismatch, a dialog appears:

```
┌─────────────────────────────────┐
│ Select PHP                      │
├─────────────────────────────────┤
│ Installation failed.            │
│ Select a PHP version to retry:  │
│                                 │
│ [    PHP 8.1    ]               │
│ [    PHP 8.2    ]               │
│ [    PHP 8.3    ]               │
│                                 │
│ [    Cancel     ]               │
└─────────────────────────────────┘
```

Select the appropriate PHP version to retry installation.

---

### Step 7: Installation Complete

When all projects are installed, you'll see:
- A success dialog: **"Queue completed."**
- Green log message: **"All operations finished."**

---

### Step 8: Access Your Projects

Each project is now accessible in your browser:

| Project Name | URL |
|--------------|-----|
| `ecommerce-api` | http://ecommerce-api.test |
| `blog-backend` | http://blog-backend.test |
| `admin-panel` | http://admin-panel.test |

**Note:** The `.test` domain is automatically configured in `/etc/hosts`.

---

## Quick Reference

### Keyboard Shortcuts

| Action | How |
|--------|-----|
| Switch to Dashboard | Click "Dashboard / Queue" in sidebar |
| Switch to Logs | Click "Installation Logs" in sidebar |
| Remove project from queue | Click red "Remove" button next to project |

### Project Locations

| Item | Location |
|------|----------|
| Project Source Code | `/opt/homebrew/var/www/<project-name>/` |
| Public Symlink | `/opt/homebrew/var/www/html/<project-name>/` |
| Apache VirtualHost | `/opt/homebrew/etc/httpd/sites-enabled/<project-name>.conf` |
| Error Logs | `/opt/homebrew/var/log/httpd/<project-name>-error.log` |

*Note: Intel Macs use `/usr/local/` instead of `/opt/homebrew/`*

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

For each project in the queue, the installer performs these steps automatically:

### Step-by-Step Installation Process

| Step | Action | Details |
|------|--------|---------|
| 1 | **Git Clone/Pull** | Clones the repository to `/opt/homebrew/var/www/<name>/` or pulls latest if exists |
| 2 | **Environment Setup** | Copies `.env.example` → `.env` if `.env` doesn't exist |
| 3 | **PHP Detection** | Reads `require.php` from `composer.json` to determine PHP version |
| 4 | **PHP Installation** | Installs required PHP version via Homebrew if not present |
| 5 | **Composer Install** | Runs `composer install` with detected PHP version |
| 6 | **Public Directory Check** | Verifies `public/` directory exists (creates if missing) |
| 7 | **APP_KEY Generation** | Runs `php artisan key:generate --force` for Laravel apps |
| 8 | **Symlink Creation** | Links `<project>/public/` → `/opt/homebrew/var/www/html/<name>/` |
| 9 | **Permissions** | Sets `775` permissions, owner: `<user>:staff` |
| 10 | **VirtualHost Config** | Creates Apache config at `sites-available/<name>.conf` |
| 11 | **Enable Site** | Symlinks config to `sites-enabled/` |
| 12 | **Hosts Entry** | Adds `127.0.0.1 <name>.test` to `/etc/hosts` |
| 13 | **Apache Reload** | Restarts Apache via `brew services restart httpd` |

### Generated VirtualHost Example

For a project named `ecommerce-api` with PHP 8.2:

```apache
<VirtualHost *:80>
    ServerName ecommerce-api.test
    DocumentRoot /opt/homebrew/var/www/html/ecommerce-api
    <Directory /opt/homebrew/var/www/html/ecommerce-api>
        AllowOverride All
        Require all granted
    </Directory>
    ErrorLog /opt/homebrew/var/log/httpd/ecommerce-api-error.log
    CustomLog /opt/homebrew/var/log/httpd/ecommerce-api-access.log combined
    <FilesMatch \.php$>
        SetHandler "proxy:unix:/opt/homebrew/var/run/php@8.2-fpm.sock|fcgi://localhost/"
    </FilesMatch>
</VirtualHost>
```

---

## Uninstallation

### Using the Uninstall Script

```bash
# Keep project files
"$HOME/Library/Application Support/laravel-bulk-installer/scripts/uninstall.sh" --keep-projects

# Remove everything
"$HOME/Library/Application Support/laravel-bulk-installer/scripts/uninstall.sh"
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
