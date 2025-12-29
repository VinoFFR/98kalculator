import os
import shutil
import subprocess
import sys
import time

def print_status(message, color="35"): 
    print(f"\033[1;{color}m[98kalculator Updater] {message}\033[0m")

def check_git_installed():
    try:
        subprocess.run(["git", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_git():
    print_status("Git is not installed. It is required for updates.", "31")
    print_status("Attempting to install git...", "33")
    
    package_managers = [
        ("apt-get", ["sudo", "apt-get", "update"], ["sudo", "apt-get", "install", "-y", "git"]),
        ("dnf", None, ["sudo", "dnf", "install", "-y", "git"]),
        ("pacman", None, ["sudo", "pacman", "-S", "--noconfirm", "git"]),
        ("zypper", None, ["sudo", "zypper", "install", "-y", "git"]),
        ("yum", None, ["sudo", "yum", "install", "-y", "git"]),
        ("apk", ["sudo", "apk", "update"], ["sudo", "apk", "add", "git"]),
    ]

    for pm, update_cmd, install_cmd in package_managers:
        if shutil.which(pm):
            print_status(f"Detected package manager: {pm}", "34")
            try:
                if update_cmd:
                    print_status(f"Updating package list with {pm}...", "33")
                    subprocess.run(update_cmd, check=False)
                
                print_status(f"Installing git with {pm}...", "33")
                subprocess.run(install_cmd, check=True)
                
                print_status("Git installed successfully!", "32")
                return True
            except subprocess.CalledProcessError:
                print_status(f"Failed to install git using {pm}.", "31")
                return False

    print_status("No supported package manager found or installation failed.", "31")
    print_status("Please install git manually and restart the updater.", "31")
    return False

def update_repo():
    print_status("Checking for updates from GitHub...", "34")
    try:
        if not os.path.exists(".git"):
            print_status("Not a git repository. Cannot update via git.", "31")
            return False

        result = subprocess.run(["git", "pull"], capture_output=True, text=True)
        
        if result.returncode != 0:
            print_status(f"Error pulling updates: {result.stderr}", "31")
            return False
            
        if "Already up to date" in result.stdout:
            print_status("Already up to date!", "32")
            return False # No update needed
        else:
            print_status("Updates downloaded successfully!", "32")
            print(result.stdout)
            return True # Updated
            
    except Exception as e:
        print_status(f"An unexpected error occurred: {e}", "31")
        return False

def reinstall_app():
    print_status("Reinstalling application with new updates...", "33")
    try:
        # Run install.py
        if os.path.exists("install.py"):
            subprocess.run([sys.executable, "install.py"], check=True)
            print_status("Update and Reinstall Complete!", "32")
        else:
            print_status("install.py not found! Cannot reinstall.", "31")
    except subprocess.CalledProcessError as e:
        print_status(f" installation failed: {e}", "31")

def main():
    print("\n" + "="*50)
    print_status("Starting Update Process")
    print("="*50 + "\n")

    if not check_git_installed():
        if not install_git():
            print_status("Cannot proceed without git.", "31")
            return

    updated = update_repo()
    
    if updated:
        reinstall_app()
    else:
        # Ask to force reinstall if user wants
        response = input("\nNo updates found. Force reinstall anyway? [y/N]: ").strip().lower()
        if response == 'y':
            reinstall_app()
    
    print("\n" + "="*50)
    print_status("Updater finished.")
    print("="*50 + "\n")
    
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
