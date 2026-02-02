#!/usr/bin/env python3
"""
Laravel Bulk Project Installer - macOS Version
Ported from Linux (Ubuntu/Debian) to macOS with full equivalence.
All paths, commands, and service management adapted for macOS + Homebrew.
Supports both ARM64 (Apple Silicon) and x86_64 (Intel).
"""
import os
import sys
import subprocess
import shutil
import json
import re
import threading
import queue
import time
import platform

# --- Dependency Check & Auto-Install ---
REQUIRED_PACKAGES = ["customtkinter", "packaging"]

def check_and_install_dependencies():
    """Checks for required packages and installs them if missing using standard tkinter."""
    missing = []
    for pkg in REQUIRED_PACKAGES:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)

    if not missing:
        return

    import tkinter as tk
    from tkinter import messagebox

    root = tk.Tk()
    root.title("Setup Required")
    root.geometry("400x180")

    # Simple Style
    root.configure(bg="#2b2b2b")
    fg_color = "#ffffff"

    lbl = tk.Label(root, text=f"Wait! We need to setup some engines first.\n\nMissing: {', '.join(missing)}",
                   justify="center", bg="#2b2b2b", fg=fg_color, font=("Arial", 11))
    lbl.pack(pady=20)

    def install():
        btn_install.config(state="disabled", text="Setting up engines...")
        root.update()
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
            messagebox.showinfo("Ready", "Engines are ready! Restarting app...")
            root.destroy()
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {e}")
            btn_install.config(state="normal", text="Try Again")

    btn_install = tk.Button(root, text="Autofix & Start", command=install,
                            bg="#3b8ed0", fg="white", font=("Arial", 12, "bold"), padx=20, pady=5, borderwidth=0)
    btn_install.pack(pady=10)

    root.mainloop()
    sys.exit()

check_and_install_dependencies()

# --- Imports after dependency check ---
import customtkinter as ctk
from tkinter import messagebox
from packaging import version

# --- THEME CONSTANTS ---
COLOR_BG = "#1e1e1e"        # Main Background
COLOR_SIDEBAR = "#252526"   # Sidebar Background
COLOR_CARD = "#2d2d2d"      # Card/Content Background
COLOR_PRIMARY = "#3b8ed0"   # Action Blue
COLOR_SUCCESS = "#10b981"   # Success Green
COLOR_DANGER = "#ef4444"    # Error Red
COLOR_TEXT = "#e1e1e1"      # Main Text
COLOR_TEXT_DIM = "#a1a1a1"  # Secondary Text

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- macOS PATH CONSTANTS ---
def get_homebrew_prefix():
    """Detect Homebrew prefix for ARM64 vs x86_64."""
    arch = platform.machine()
    if arch == "arm64":
        return "/opt/homebrew"
    else:
        return "/usr/local"

HOMEBREW_PREFIX = get_homebrew_prefix()

# macOS Paths (equivalents to Linux paths)
PATHS = {
    # Application directories
    "app_support": os.path.join(os.path.expanduser("~"), "Library", "Application Support"),
    "install_dir": os.path.join(os.path.expanduser("~"), "Library", "Application Support", "laravel-bulk-installer"),

    # Web server paths (Homebrew Apache)
    "www_root": os.path.join(HOMEBREW_PREFIX, "var", "www"),
    "www_html": os.path.join(HOMEBREW_PREFIX, "var", "www", "html"),
    "apache_conf": os.path.join(HOMEBREW_PREFIX, "etc", "httpd"),
    "apache_sites": os.path.join(HOMEBREW_PREFIX, "etc", "httpd", "sites-available"),
    "apache_sites_enabled": os.path.join(HOMEBREW_PREFIX, "etc", "httpd", "sites-enabled"),
    "apache_log": os.path.join(HOMEBREW_PREFIX, "var", "log", "httpd"),

    # PHP paths (Homebrew)
    "php_base": os.path.join(HOMEBREW_PREFIX, "opt"),
    "php_run": os.path.join(HOMEBREW_PREFIX, "var", "run"),

    # System paths
    "hosts": "/etc/hosts",
    "launchd_agents": os.path.join(os.path.expanduser("~"), "Library", "LaunchAgents"),
}

# macOS web user (equivalent to www-data on Linux)
WEB_USER = "_www"
WEB_GROUP = "staff"


class InstallManager:
    """Handles system installation logic for macOS"""
    APP_NAME = "laravel-bulk-installer"

    INSTALL_DIR = PATHS["install_dir"]

    @staticmethod
    def is_installed():
        """Check if running from installed location."""
        current_script = os.path.realpath(os.path.abspath(__file__))
        install_dir_real = os.path.realpath(InstallManager.INSTALL_DIR)
        return current_script.startswith(install_dir_real)

    @staticmethod
    def install_system():
        """Install application to macOS Application Support directory."""
        try:
            # 1. Validate install path before any destructive operations
            install_dir = InstallManager.INSTALL_DIR
            expected_prefix = os.path.join(os.path.expanduser("~"), "Library", "Application Support")
            if not os.path.realpath(install_dir).startswith(os.path.realpath(expected_prefix)):
                raise Exception(f"Invalid install directory: {install_dir}")

            # 2. Clean previous install
            if os.path.exists(install_dir):
                shutil.rmtree(install_dir)
            os.makedirs(install_dir, exist_ok=True)

            # 3. Copy application file
            current_script = os.path.realpath(os.path.abspath(__file__))
            target_script = os.path.join(install_dir, "app.py")

            shutil.copy2(current_script, target_script)
            os.chmod(target_script, 0o755)

            # 4. Download Icon
            icon_path = os.path.join(install_dir, "laravel-icon.png")
            try:
                import urllib.request
                icon_url = "https://raw.githubusercontent.com/laravel/art/master/logomark/5%20SVG/2%20CMYK/1%20Full%20Color/laravel-logomark-cmyk-red.svg"
                urllib.request.urlretrieve(icon_url, icon_path)
            except Exception as e:
                print(f"Failed to download icon: {e}")
                icon_path = None

            # 5. Create launch script for easy access
            launch_script = os.path.join(install_dir, "launch.command")
            with open(launch_script, "w") as f:
                f.write(f'''#!/bin/bash
cd "$(dirname "$0")"
{sys.executable} "{target_script}"
''')
            os.chmod(launch_script, 0o755)

            # 5. Create symlink in /usr/local/bin for CLI access
            cli_link = os.path.join(HOMEBREW_PREFIX, "bin", "laravel-installer")
            try:
                if os.path.islink(cli_link):
                    os.unlink(cli_link)
                os.symlink(launch_script, cli_link)
            except PermissionError:
                pass  # Non-fatal, user may not have write access

            return True

        except Exception as e:
            raise Exception(f"Installation Step Failed: {str(e)}")


class SidebarButton(ctk.CTkButton):
    """Custom styled sidebar button"""
    def __init__(self, master, text, command, **kwargs):
        super().__init__(master, text=text, command=command,
                         fg_color="transparent", hover_color="#333333",
                         anchor="w", height=40, font=("SF Pro Display", 13), **kwargs)


class ProjectInstallerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Check Installation Status First
        if not InstallManager.is_installed():
            self.offer_installation()

        self.title("Laravel Bulk Project Installer")
        self.geometry("1000x800")
        self.configure(fg_color=COLOR_BG)

        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # State
        self.projects = []
        self.log_queue = queue.Queue()
        self.interaction_queue = queue.Queue()
        self.is_running = False

        self.setup_ui()

        # Start loops
        self.after(100, self.process_queues)

    def offer_installation(self):
        """Shows a dialog asking to install to system."""
        dialog = ctk.CTk()
        dialog.title("Welcome")
        dialog.geometry("500x300")
        dialog.configure(fg_color=COLOR_BG)

        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame, text="Laravel Bulk Installer", font=("SF Pro Display", 24, "bold")).pack(pady=10)
        ctk.CTkLabel(frame, text="Would you like to install this tool to your system?\nThis will install to ~/Library/Application Support.",
                     font=("SF Pro Display", 14), text_color=COLOR_TEXT_DIM).pack(pady=20)

        def do_install():
            try:
                InstallManager.install_system()
                messagebox.showinfo("Success", "Installation complete!\nYou can run 'laravel-installer' from Terminal\nor use the launch.command file.")
                dialog.destroy()
                sys.exit()
            except Exception as e:
                messagebox.showerror("Error", f"Install failed: {e}")

        def do_try():
            dialog.destroy()

        btn_box = ctk.CTkFrame(frame, fg_color="transparent")
        btn_box.pack(pady=20)

        ctk.CTkButton(btn_box, text="Run Once (Try)", fg_color="transparent", border_width=1, command=do_try).pack(side="left", padx=10)
        ctk.CTkButton(btn_box, text="Install to System", fg_color=COLOR_PRIMARY, command=do_install).pack(side="left", padx=10)

        dialog.mainloop()

    def setup_ui(self):
        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=COLOR_SIDEBAR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(self.sidebar, text="INSTALLER", font=("SF Pro Display", 20, "bold"), text_color=COLOR_PRIMARY).pack(pady=(30, 10), padx=20, anchor="w")

        ctk.CTkLabel(self.sidebar, text="MENU", font=("SF Pro Display", 11, "bold"), text_color=COLOR_TEXT_DIM).pack(pady=(20, 5), padx=20, anchor="w")

        SidebarButton(self.sidebar, text="Dashboard / Queue", command=self.show_dashboard).pack(fill="x", padx=10, pady=2)
        SidebarButton(self.sidebar, text="Installation Logs", command=self.show_logs).pack(fill="x", padx=10, pady=2)

        # Bottom Version
        ctk.CTkLabel(self.sidebar, text="v2.0.0-macos", font=("SF Pro Display", 10), text_color=COLOR_TEXT_DIM).pack(side="bottom", pady=20)

        # --- Content Area ---
        self.content_area = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Frames
        self.frame_dashboard = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.frame_logs = ctk.CTkFrame(self.content_area, fg_color="transparent")

        self.build_dashboard()
        self.build_logs()

        self.show_dashboard()

    def build_dashboard(self):
        # Card 1: Add Project
        card_add = ctk.CTkFrame(self.frame_dashboard, fg_color=COLOR_CARD, corner_radius=15)
        card_add.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(card_add, text="Add New Project", font=("SF Pro Display", 16, "bold")).pack(anchor="w", padx=20, pady=(20, 15))

        grid = ctk.CTkFrame(card_add, fg_color="transparent")
        grid.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(grid, text="Project Name", font=("SF Pro Display", 12, "bold")).grid(row=0, column=0, sticky="w", padx=5)
        self.entry_name = ctk.CTkEntry(grid, placeholder_text="e.g. ecommerce-api", width=250, border_width=0, fg_color="#3E3E3E", height=35)
        self.entry_name.grid(row=1, column=0, padx=5, pady=(5, 0))

        ctk.CTkLabel(grid, text="Git Repository URL", font=("SF Pro Display", 12, "bold")).grid(row=0, column=1, sticky="w", padx=15)
        self.entry_repo = ctk.CTkEntry(grid, placeholder_text="git@github.com...", width=350, border_width=0, fg_color="#3E3E3E", height=35)
        self.entry_repo.grid(row=1, column=1, padx=15, pady=(5, 0))

        ctk.CTkButton(grid, text="+ Add to Queue", fg_color=COLOR_PRIMARY, height=35, font=("SF Pro Display", 13, "bold"), command=self.add_project).grid(row=1, column=2, padx=15, pady=(5, 0), sticky="s")

        # Card 2: Queue
        card_queue = ctk.CTkFrame(self.frame_dashboard, fg_color=COLOR_CARD, corner_radius=15)
        card_queue.pack(fill="both", expand=True)

        header = ctk.CTkFrame(card_queue, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(header, text="Installation Queue", font=("SF Pro Display", 16, "bold")).pack(side="left")

        self.lbl_count = ctk.CTkLabel(header, text="0 Projects", font=("SF Pro Display", 13), text_color=COLOR_TEXT_DIM)
        self.lbl_count.pack(side="left", padx=10)

        self.queue_container = ctk.CTkScrollableFrame(card_queue, fg_color="transparent", height=300)
        self.queue_container.pack(fill="both", expand=True, padx=10, pady=(0, 20))

        # Action Bar
        action_bar = ctk.CTkFrame(self.frame_dashboard, fg_color="transparent")
        action_bar.pack(fill="x", pady=20)

        self.btn_run = ctk.CTkButton(action_bar, text="START INSTALLATION", font=("SF Pro Display", 14, "bold"),
                                     height=50, fg_color=COLOR_SUCCESS, hover_color="#059669", command=self.start_thread)
        self.btn_run.pack(fill="x")

    def build_logs(self):
        self.log_textbox = ctk.CTkTextbox(self.frame_logs, font=("SF Mono", 12), fg_color="#111111", text_color="#eeeeee", corner_radius=10)
        self.log_textbox.pack(fill="both", expand=True)
        self.log_textbox.tag_config("error", foreground="#ef4444")
        self.log_textbox.tag_config("success", foreground="#10b981")
        self.log_textbox.tag_config("cmd", foreground="#3b8ed0")

    def show_dashboard(self):
        self.frame_logs.pack_forget()
        self.frame_dashboard.pack(fill="both", expand=True)

    def show_logs(self):
        self.frame_dashboard.pack_forget()
        self.frame_logs.pack(fill="both", expand=True)

    def log(self, msg, level="info"):
        self.log_queue.put((msg, level))

    def process_queues(self):
        # Log consumer
        try:
            while True:
                msg, level = self.log_queue.get_nowait()
                self.log_textbox.configure(state="normal")
                ts = time.strftime('%H:%M:%S')
                self.log_textbox.insert("end", f"[{ts}] {msg}\n", level)
                self.log_textbox.see("end")
                self.log_textbox.configure(state="disabled")
        except queue.Empty:
            pass

        # Interaction consumer
        try:
            while True:
                atype, payload, event, result = self.interaction_queue.get_nowait()
                if atype == "ask_password":
                    result['val'] = ctk.CTkInputDialog(text="Enter Admin Password:", title="Auth").get_input()
                elif atype == "ask_dep":
                    result['val'] = messagebox.askyesno("Dependency Missing", f"Install '{payload}' via Homebrew automatically?")
                elif atype == "ask_php":
                    self.popup_php_select(payload, result)
                event.set()
        except queue.Empty:
            pass

        self.after(100, self.process_queues)

    def popup_php_select(self, versions, result_ref):
        top = ctk.CTkToplevel(self)
        top.title("Select PHP")
        top.geometry("300x400")
        top.grab_set()

        ctk.CTkLabel(top, text="Installation failed.\nSelect a PHP version to retry:", font=("SF Pro Display", 13)).pack(pady=20)

        selection = ctk.StringVar()

        def pick(v):
            selection.set(v)
            top.destroy()

        for v in versions:
            ctk.CTkButton(top, text=f"PHP {v}", command=lambda x=v: pick(x), fg_color=COLOR_CARD, border_width=1, border_color="#555").pack(pady=5, padx=20, fill="x")

        # Add cancel button
        ctk.CTkButton(top, text="Cancel", command=top.destroy, fg_color=COLOR_DANGER).pack(pady=10, padx=20, fill="x")

        self.wait_window(top)
        # Return None if no selection was made (empty string)
        selected = selection.get()
        result_ref['val'] = selected if selected else None

    def sanitize_project_name(self, name):
        """Sanitize project name to prevent shell injection and path traversal."""
        # Only allow alphanumeric, hyphen, underscore
        sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', name)
        # Prevent empty names or names starting with hyphen
        if not sanitized or sanitized.startswith('-'):
            return None
        # Limit length
        return sanitized[:64]

    def add_project(self):
        name = self.entry_name.get().strip()
        repo = self.entry_repo.get().strip()

        if not name or not repo: return

        # Sanitize project name for security
        sanitized_name = self.sanitize_project_name(name)
        if not sanitized_name:
            messagebox.showerror("Invalid Name", "Project name can only contain letters, numbers, hyphens, and underscores.")
            return

        # Check for duplicate project names
        if any(p['name'] == sanitized_name for p in self.projects):
            messagebox.showerror("Duplicate", f"Project '{sanitized_name}' is already in the queue.")
            return

        self.projects.append({'name': sanitized_name, 'repo': repo})
        self.refresh_queue_ui()
        self.entry_name.delete(0, "end")
        self.entry_repo.delete(0, "end")

    def refresh_queue_ui(self):
        # Clear
        for widget in self.queue_container.winfo_children(): widget.destroy()

        self.lbl_count.configure(text=f"{len(self.projects)} Projects")

        for idx, p in enumerate(self.projects):
            row = ctk.CTkFrame(self.queue_container, fg_color="#333", height=50)
            row.pack(fill="x", pady=2)

            ctk.CTkLabel(row, text=p['name'], font=("SF Pro Display", 13, "bold")).pack(side="left", padx=15)
            ctk.CTkLabel(row, text=p['repo'], font=("SF Pro Display", 12), text_color="#aaa").pack(side="left", padx=5)

            ctk.CTkButton(row, text="Remove", width=60, height=25, fg_color=COLOR_DANGER,
                          command=lambda i=idx: self.remove_project(i)).pack(side="right", padx=10, pady=10)

    def remove_project(self, idx):
        self.projects.pop(idx)
        self.refresh_queue_ui()

    def start_thread(self):
        if not self.projects or self.is_running: return
        self.is_running = True
        self.btn_run.configure(state="disabled", text="Running...")
        self.show_logs()
        # Use daemon=True so thread doesn't prevent app exit
        threading.Thread(target=self.run_install, daemon=True).start()

    # --- Worker Thread ---
    def request(self, atype, payload=None):
        evt = threading.Event()
        res = {}
        self.interaction_queue.put((atype, payload, evt, res))
        evt.wait()
        return res.get('val')

    def run_install(self):
        self.log("--- Starting Bulk Installation (macOS) ---", "info")
        pwd = self.request("ask_password")
        if not pwd:
            self.log("Cancelled: Password required.", "error")
            self.reset_state()
            return

        # Ensure directories exist
        self.ensure_directories(pwd)

        for proj in self.projects:
            try:
                self.install_project(proj, pwd)
            except Exception as e:
                self.log(f"FAILED {proj['name']}: {e}", "error")

        self.log("All operations finished.", "success")
        # Use after() to safely call GUI from worker thread
        self.after(0, lambda: messagebox.showinfo("Done", "Queue completed."))
        self.after(0, self.reset_state)

    def reset_state(self):
        self.is_running = False
        self.btn_run.configure(state="normal", text="START INSTALLATION")

    def ensure_directories(self, pwd):
        """Ensure all required directories exist for macOS."""
        dirs = [
            PATHS["www_root"],
            PATHS["www_html"],
            PATHS["apache_sites"],
            PATHS["apache_sites_enabled"],
            PATHS["apache_log"],
        ]
        for d in dirs:
            if not os.path.exists(d):
                self.cmd(["sudo", "-S", "mkdir", "-p", d], pwd)

    def cmd(self, args, pwd=None, check=True):
        cmd_str = " ".join(args)
        self.log(f"EXEC: {cmd_str}", "cmd")

        proc = subprocess.run(
            args,
            input=(pwd+"\n").encode() if pwd else None,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        if proc.stdout:
            for l in proc.stdout.decode(errors='replace').split("\n"):
                if l.strip(): self.log(f"  {l}")

        if proc.returncode != 0:
            err = proc.stderr.decode(errors='replace').strip()
            self.log(f"  ERR: {err}", "error")

            # Heuristics for macOS
            if "command not found" in err or "not found" in err:
                pkg = args[0]
                # Map common tools to Homebrew packages
                brew_pkg = self.get_brew_package(pkg)
                if self.request("ask_dep", brew_pkg):
                    self.log(f"Auto-installing {brew_pkg} via Homebrew...", "info")
                    self.cmd(["brew", "install", brew_pkg], None, check=True)
                    return self.cmd(args, pwd, check)  # Retry

            if check: raise Exception(err)

        return proc

    def get_brew_package(self, cmd):
        """Map command names to Homebrew package names."""
        mapping = {
            "git": "git",
            "composer": "composer",
            "php": "php",
            "httpd": "httpd",
            "apachectl": "httpd",
        }
        return mapping.get(cmd, cmd)

    def install_project(self, p, pwd):
        self.log(f"Installing {p['name']}...", "info")
        path = os.path.join(PATHS["www_root"], p['name'])
        html = os.path.join(PATHS["www_html"], p['name'])

        # Git
        if not os.path.exists(path):
            self.cmd(["git", "clone", p['repo'], path])
        else:
            self.cmd(["git", "-C", path, "pull"])

        # Env
        if os.path.exists(f"{path}/.env.example") and not os.path.exists(f"{path}/.env"):
            shutil.copy(f"{path}/.env.example", f"{path}/.env")

        # PHP Detect
        php_ver = "8.2"
        if os.path.exists(f"{path}/composer.json"):
            try:
                with open(f"{path}/composer.json") as f:
                    parsed = json.load(f)
                    req = parsed.get("require", {}).get("php", "")
                    m = re.search(r"(\d+\.\d+)", req)
                    if m: php_ver = m.group(1)
            except (json.JSONDecodeError, KeyError) as e:
                self.log(f"Warning: Could not parse composer.json: {e}", "error")
                self.log(f"Using default PHP version: {php_ver}", "info")

        self.log(f"PHP Required: {php_ver}", "info")

        # Extensions via Homebrew (macOS: extensions bundled with php@version)
        # On macOS with Homebrew, most extensions are bundled or available as separate packages
        php_formula = f"php@{php_ver}"
        self.log(f"Ensuring {php_formula} is installed...", "info")
        self.cmd(["brew", "install", php_formula], None, check=False)

        # Additional extensions if needed (installed separately on macOS)
        exts_to_check = ["gd", "zip", "pdo_mysql"]
        for ext in exts_to_check:
            ext_formula = f"php@{php_ver}"  # Extensions bundled in Homebrew PHP
            # Most extensions are included; pecl for extras if needed
            pass

        # Composer
        php_bin = self.get_php_binary(php_ver)
        comp_bin = shutil.which("composer") or os.path.join(HOMEBREW_PREFIX, "bin", "composer")

        try:
            self.cmd([php_bin, comp_bin, "install", "-d", path], None, check=True)
        except Exception:
            # Retry logic
            bins = self.get_php_versions()
            sel = self.request("ask_php", sorted(list(set(bins))))
            if sel:
                alt_php = self.get_php_binary(sel)
                self.cmd([alt_php, comp_bin, "install", "-d", path], None)

        # Symlink & Perms
        if os.path.islink(html) or os.path.exists(html):
            self.cmd(["sudo", "-S", "rm", "-rf", html], pwd)
        self.cmd(["sudo", "-S", "ln", "-s", f"{path}/public", html], pwd)
        self.cmd(["sudo", "-S", "chmod", "-R", "775", path], pwd)
        # macOS: Use current user and staff group (standard macOS approach)
        try:
            current_user = os.getlogin()
        except OSError:
            # Fallback if no controlling terminal
            current_user = os.environ.get('USER', os.environ.get('LOGNAME', 'nobody'))
        self.cmd(["sudo", "-S", "chown", "-R", f"{current_user}:{WEB_GROUP}", path], pwd)

        # VHost
        vhost = self.get_vhost_template(p['name'], html, php_ver)
        tmp = f"/tmp/{p['name']}.conf"
        with open(tmp, "w") as f: f.write(vhost)

        sites_available = os.path.join(PATHS["apache_sites"], f"{p['name']}.conf")
        sites_enabled = os.path.join(PATHS["apache_sites_enabled"], f"{p['name']}.conf")

        self.cmd(["sudo", "-S", "mv", tmp, sites_available], pwd)

        # Create symlink to enable site (macOS equivalent to a2ensite)
        if not os.path.exists(sites_enabled):
            self.cmd(["sudo", "-S", "ln", "-sf", sites_available, sites_enabled], pwd)

        # Reload Apache via brew services or apachectl
        self.reload_apache(pwd)

        # Hosts - using safer method with tee
        hosts_entry = f"127.0.0.1 {p['name']}.test"
        self.update_hosts_file(p['name'], hosts_entry, pwd)

        self.log(f"Completed: {p['name']}", "success")

    def update_hosts_file(self, project_name, hosts_entry, pwd):
        """Safely update /etc/hosts file without shell injection risk."""
        # Check if entry already exists
        try:
            with open("/etc/hosts", "r") as f:
                if f"{project_name}.test" in f.read():
                    self.log(f"Hosts entry already exists for {project_name}.test", "info")
                    return
        except PermissionError:
            pass  # Will need sudo to read, continue with write attempt

        # Write entry to temp file, then use tee to append (no shell interpolation)
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.hosts', delete=False) as tmp:
            tmp.write(f"{hosts_entry}\n")
            tmp_path = tmp.name

        try:
            # Use tee -a to append safely (no shell needed, tee reads from stdin)
            proc = subprocess.run(
                ["sudo", "-S", "tee", "-a", "/etc/hosts"],
                input=(pwd + "\n" + hosts_entry + "\n").encode(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )
            if proc.returncode == 0:
                self.log(f"Added hosts entry: {hosts_entry}", "info")
            else:
                self.log(f"Failed to add hosts entry: {proc.stderr.decode(errors='replace')}", "error")
        finally:
            os.unlink(tmp_path)

    def get_php_binary(self, version):
        """Get PHP binary path for a specific version on macOS (Homebrew)."""
        # Try versioned formula first
        versioned_path = os.path.join(HOMEBREW_PREFIX, "opt", f"php@{version}", "bin", "php")
        if os.path.exists(versioned_path):
            return versioned_path

        # Try unversioned (current default)
        default_path = os.path.join(HOMEBREW_PREFIX, "opt", "php", "bin", "php")
        if os.path.exists(default_path):
            return default_path

        # Fallback to system or shutil.which
        php_which = shutil.which("php")
        if php_which:
            return php_which

        return f"{HOMEBREW_PREFIX}/opt/php@{version}/bin/php"

    def get_php_versions(self):
        """Get available PHP versions installed via Homebrew."""
        versions = []
        php_opt_base = os.path.join(HOMEBREW_PREFIX, "opt")

        if os.path.exists(php_opt_base):
            for item in os.listdir(php_opt_base):
                m = re.match(r"php@(\d+\.\d+)", item)
                if m:
                    versions.append(m.group(1))
                elif item == "php":
                    # Get version of default php
                    php_bin = os.path.join(php_opt_base, "php", "bin", "php")
                    if os.path.exists(php_bin):
                        try:
                            result = subprocess.run([php_bin, "-v"], capture_output=True, text=True)
                            m = re.search(r"PHP (\d+\.\d+)", result.stdout)
                            if m:
                                versions.append(m.group(1))
                        except Exception:
                            pass

        return versions if versions else ["8.2"]

    def reload_apache(self, pwd):
        """Reload Apache on macOS using brew services or apachectl."""
        # Try brew services first
        try:
            self.cmd(["brew", "services", "restart", "httpd"], None, check=False)
        except Exception:
            pass

        # Also try apachectl for good measure
        apachectl = os.path.join(HOMEBREW_PREFIX, "bin", "apachectl")
        if os.path.exists(apachectl):
            self.cmd(["sudo", "-S", apachectl, "graceful"], pwd, check=False)
        else:
            self.cmd(["sudo", "-S", "apachectl", "graceful"], pwd, check=False)

    def get_vhost_template(self, name, root, php):
        """Generate Apache VirtualHost config for macOS."""
        # PHP-FPM socket path on macOS (Homebrew)
        php_fpm_socket = os.path.join(PATHS["php_run"], f"php{php}-fpm.sock")
        # Alternative socket location
        alt_socket = os.path.join(HOMEBREW_PREFIX, "var", "run", f"php@{php}-fpm.sock")

        log_dir = PATHS["apache_log"]

        return f"""<VirtualHost *:80>
    ServerName {name}.test
    DocumentRoot {root}
    <Directory {root}>
        AllowOverride All
        Require all granted
    </Directory>
    ErrorLog {log_dir}/{name}-error.log
    CustomLog {log_dir}/{name}-access.log combined
    <FilesMatch \\.php$>
        SetHandler "proxy:unix:{alt_socket}|fcgi://localhost/"
    </FilesMatch>
</VirtualHost>"""


if __name__ == "__main__":
    app = ProjectInstallerApp()
    app.mainloop()
