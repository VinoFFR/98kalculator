import os
import shutil
import subprocess
import sys

def remove_executable():
    print("Removing executable and build artifacts...")
    app_dir = os.path.dirname(os.path.abspath(__file__))
    
    targets = [
        os.path.join(app_dir, "98kalculator"), 
        os.path.join(app_dir, "wayland-calculator"),
        os.path.join(app_dir, "98kalculator.spec"),
        os.path.join(app_dir, "wayland-calculator.spec")
    ]
    
    dirs = [
        os.path.join(app_dir, "build"),
        os.path.join(app_dir, "dist")
    ]

    for t in targets:
        if os.path.exists(t):
            os.remove(t)
            print(f"Removed: {t}")
            
    for d in dirs:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"Removed directory: {d}")

def remove_desktop_file():
    print("Removing .desktop file...")
    desktop_files = [
        os.path.expanduser("~/.local/share/applications/98kalculator.desktop"),
        os.path.expanduser("~/.local/share/applications/wayland-calculator.desktop")
    ]
    
    removed = False
    for f in desktop_files:
        if os.path.exists(f):
            os.remove(f)
            print(f"Removed: {f}")
            removed = True
            
    if removed:
        try:
            subprocess.run(["update-desktop-database", os.path.expanduser("~/.local/share/applications")], check=True)
            print("Desktop database updated.")
        except Exception as e:
            print(f"Failed to update desktop database: {e}")
    else:
        print("No .desktop files found to remove.")

def uninstall_dependencies():
    print("Skipping dependency uninstallation (PyQt6, PyInstaller) to safeguard system.")

def main():
    print("Starting uninstallation process for 98kalculator...")
    remove_executable()
    remove_desktop_file()
    uninstall_dependencies()
    print("\nUninstallation complete.")

if __name__ == "__main__":
    main()
