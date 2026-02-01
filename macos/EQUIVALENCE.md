# Linux to macOS Equivalence Table

This document maps every Linux-specific component from the original Ubuntu/Debian implementation to its macOS equivalent.

## Package Management

| Component | Linux (Ubuntu/Debian) | macOS (Homebrew) |
|-----------|----------------------|------------------|
| Package manager | `apt` / `apt-get` | `brew` |
| Install command | `sudo apt install -y <pkg>` | `brew install <pkg>` |
| Update packages | `sudo apt update` | `brew update` |
| Upgrade packages | `sudo apt upgrade` | `brew upgrade` |
| Search packages | `apt search <pkg>` | `brew search <pkg>` |
| Package info | `apt show <pkg>` | `brew info <pkg>` |
| Remove package | `sudo apt remove <pkg>` | `brew uninstall <pkg>` |

## File System Paths

### Application Directories

| Purpose | Linux | macOS |
|---------|-------|-------|
| User app data | `~/.local/share/` | `~/Library/Application Support/` |
| Desktop entries | `~/.local/share/applications/` | N/A (use .app bundles or CLI) |
| Application install | `~/.local/share/laravel-bulk-installer/` | `~/Library/Application Support/laravel-bulk-installer/` |

### Web Server Directories

| Purpose | Linux | macOS (ARM64) | macOS (Intel) |
|---------|-------|---------------|---------------|
| WWW root | `/var/www/` | `/opt/homebrew/var/www/` | `/usr/local/var/www/` |
| Document root | `/var/www/html/` | `/opt/homebrew/var/www/html/` | `/usr/local/var/www/html/` |
| Apache config | `/etc/apache2/` | `/opt/homebrew/etc/httpd/` | `/usr/local/etc/httpd/` |
| Sites available | `/etc/apache2/sites-available/` | `/opt/homebrew/etc/httpd/sites-available/` | `/usr/local/etc/httpd/sites-available/` |
| Sites enabled | `/etc/apache2/sites-enabled/` | `/opt/homebrew/etc/httpd/sites-enabled/` | `/usr/local/etc/httpd/sites-enabled/` |
| Apache logs | `/var/log/apache2/` | `/opt/homebrew/var/log/httpd/` | `/usr/local/var/log/httpd/` |

### PHP Paths

| Purpose | Linux | macOS (ARM64) | macOS (Intel) |
|---------|-------|---------------|---------------|
| PHP binary | `/usr/bin/php{ver}` | `/opt/homebrew/opt/php@{ver}/bin/php` | `/usr/local/opt/php@{ver}/bin/php` |
| PHP-FPM binary | `/usr/sbin/php-fpm{ver}` | `/opt/homebrew/opt/php@{ver}/sbin/php-fpm` | `/usr/local/opt/php@{ver}/sbin/php-fpm` |
| PHP-FPM socket | `/var/run/php/php{ver}-fpm.sock` | `/opt/homebrew/var/run/php@{ver}-fpm.sock` | `/usr/local/var/run/php@{ver}-fpm.sock` |
| PHP config | `/etc/php/{ver}/` | `/opt/homebrew/etc/php/{ver}/` | `/usr/local/etc/php/{ver}/` |

### System Paths

| Purpose | Linux | macOS |
|---------|-------|-------|
| Hosts file | `/etc/hosts` | `/etc/hosts` |
| User home | `$HOME` or `~` | `$HOME` or `~` |
| Temp directory | `/tmp/` | `/tmp/` |

## Service Management

| Action | Linux (systemd) | macOS (launchd/Homebrew) |
|--------|-----------------|--------------------------|
| Start service | `sudo systemctl start <svc>` | `brew services start <svc>` |
| Stop service | `sudo systemctl stop <svc>` | `brew services stop <svc>` |
| Restart service | `sudo systemctl restart <svc>` | `brew services restart <svc>` |
| Reload service | `sudo systemctl reload <svc>` | `brew services restart <svc>` or `apachectl graceful` |
| Enable on boot | `sudo systemctl enable <svc>` | `brew services start <svc>` (auto-enables) |
| Disable on boot | `sudo systemctl disable <svc>` | `brew services stop <svc>` |
| Service status | `systemctl status <svc>` | `brew services list` |
| Service unit files | `/etc/systemd/system/` | `~/Library/LaunchAgents/` (user) |
| System service files | `/lib/systemd/system/` | `/Library/LaunchDaemons/` (system) |

## Apache Commands

| Action | Linux | macOS |
|--------|-------|-------|
| Enable site | `sudo a2ensite <site>.conf` | `ln -sf sites-available/<site>.conf sites-enabled/` |
| Disable site | `sudo a2dissite <site>.conf` | `rm sites-enabled/<site>.conf` |
| Enable module | `sudo a2enmod <mod>` | Edit `httpd.conf` to uncomment LoadModule |
| Config test | `apachectl configtest` | `apachectl configtest` |
| Graceful reload | `sudo systemctl reload apache2` | `apachectl graceful` |
| Binary | `apache2` | `httpd` |

## User/Group Management

| Purpose | Linux | macOS |
|---------|-------|-------|
| Web server user | `www-data` | `_www` |
| Web server group | `www-data` | `_www` |
| Standard user group | `<username>` | `staff` |
| Get current user | `$(whoami)` | `$(whoami)` |
| Get login name | `os.getlogin()` | `os.getlogin()` |

## PHP Extension Installation

| Action | Linux | macOS |
|--------|-------|-------|
| Install extension | `sudo apt install php{ver}-{ext}` | Bundled in `brew install php@{ver}` |
| Common extensions | `php{ver}-curl`, `php{ver}-gd`, etc. | Included by default |
| PECL extensions | `sudo pecl install <ext>` | `pecl install <ext>` |
| Enable extension | Edit `/etc/php/{ver}/mods-available/` | Edit `php.ini` or use `--with-*` |

## GUI/Desktop Integration

| Feature | Linux | macOS |
|---------|-------|-------|
| Desktop entry | `.desktop` file | `.app` bundle or direct script |
| Entry location | `~/.local/share/applications/` | `/Applications/` or `~/Applications/` |
| Update database | `update-desktop-database` | Not needed |
| File manager integration | XDG Desktop specification | Finder/LaunchServices |
| CLI symlink location | `/usr/local/bin/` | `/opt/homebrew/bin/` (ARM64) or `/usr/local/bin/` (Intel) |

## Font References

| Context | Linux | macOS |
|---------|-------|-------|
| System UI font | `Segoe UI` (fallback) | `SF Pro Display` |
| Monospace font | `Consolas` | `SF Mono` |

## Privilege Escalation

| Action | Linux | macOS |
|--------|-------|-------|
| Run as root | `sudo <cmd>` | `sudo <cmd>` |
| Password via stdin | `sudo -S` | `sudo -S` |
| Passwordless sudo | Edit `/etc/sudoers` | Edit `/etc/sudoers` |
| GUI password prompt | `pkexec` or `gksudo` | `osascript` or built-in dialogs |

## Environment Variables

| Variable | Linux | macOS (ARM64) | macOS (Intel) |
|----------|-------|---------------|---------------|
| Homebrew prefix | N/A | `/opt/homebrew` | `/usr/local` |
| PATH includes | `/usr/local/bin` | `/opt/homebrew/bin:/opt/homebrew/sbin` | `/usr/local/bin:/usr/local/sbin` |
| Python packages | `~/.local/lib/python*/` | `~/Library/Python/*/lib/` |

## VirtualHost Configuration

### Linux Template
```apache
<VirtualHost *:80>
    ServerName project.test
    DocumentRoot /var/www/html/project
    <Directory /var/www/html/project>
        AllowOverride All
        Require all granted
    </Directory>
    ErrorLog ${APACHE_LOG_DIR}/project-error.log
    CustomLog ${APACHE_LOG_DIR}/project-access.log combined
    <FilesMatch \.php$>
        SetHandler "proxy:unix:/var/run/php/php8.2-fpm.sock|fcgi://localhost/"
    </FilesMatch>
</VirtualHost>
```

### macOS Template (ARM64)
```apache
<VirtualHost *:80>
    ServerName project.test
    DocumentRoot /opt/homebrew/var/www/html/project
    <Directory /opt/homebrew/var/www/html/project>
        AllowOverride All
        Require all granted
    </Directory>
    ErrorLog /opt/homebrew/var/log/httpd/project-error.log
    CustomLog /opt/homebrew/var/log/httpd/project-access.log combined
    <FilesMatch \.php$>
        SetHandler "proxy:unix:/opt/homebrew/var/run/php@8.2-fpm.sock|fcgi://localhost/"
    </FilesMatch>
</VirtualHost>
```

## Package Equivalence

| Package | Linux (apt) | macOS (Homebrew) |
|---------|-------------|------------------|
| Apache | `apache2` | `httpd` |
| PHP 8.2 | `php8.2` | `php@8.2` |
| PHP-FPM | `php8.2-fpm` | `php@8.2` (includes FPM) |
| PHP extensions | `php8.2-{curl,gd,mbstring,zip,pdo,mysql}` | Included in `php@8.2` |
| Composer | `composer` | `composer` |
| Git | `git` | `git` (or Xcode CLT) |
| Python 3 | `python3` | `python3` |
| Python tkinter | `python3-tk` | `python-tk@3.x` |

## Installer Package Formats

| Aspect | Linux | macOS |
|--------|-------|-------|
| Package format | `.deb` (Debian/Ubuntu) | `.pkg` |
| Build tool | `dpkg-deb` | `pkgbuild` + `productbuild` |
| Installation | `sudo dpkg -i` or `sudo apt install` | `sudo installer -pkg` or double-click |
| Repository | apt repository | N/A (or Homebrew Cask) |
| Code signing | GPG signatures | Developer ID Installer certificate |

## Commands Comparison Summary

| Operation | Linux Command | macOS Command |
|-----------|---------------|---------------|
| Install Apache | `sudo apt install apache2` | `brew install httpd` |
| Start Apache | `sudo systemctl start apache2` | `brew services start httpd` |
| Install PHP 8.2 | `sudo apt install php8.2 php8.2-fpm` | `brew install php@8.2` |
| Start PHP-FPM | `sudo systemctl start php8.2-fpm` | `brew services start php` |
| Enable site | `sudo a2ensite project.conf` | `ln -sf .../sites-available/project.conf .../sites-enabled/` |
| Reload Apache | `sudo systemctl reload apache2` | `apachectl graceful` |
| Install Composer | `sudo apt install composer` | `brew install composer` |
| Create symlink | `sudo ln -s /var/www/project/public /var/www/html/project` | `sudo ln -s /opt/homebrew/var/www/project/public /opt/homebrew/var/www/html/project` |
| Set ownership | `sudo chown -R www-data:user /var/www/project` | `sudo chown -R user:staff /opt/homebrew/var/www/project` |
| Update hosts | `echo '127.0.0.1 p.test' >> /etc/hosts` | `echo '127.0.0.1 p.test' >> /etc/hosts` |
