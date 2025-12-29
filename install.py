import os
import shutil
import subprocess
import sys

def install_dependencies():
    print("Checking and installing dependencies...")

    try:
        import PyQt6
        print("PyQt6 is already installed.")
    except ImportError:
        print("PyQt6 not found, installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt6", "--break-system-packages"])
            print("PyQt6 installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install PyQt6: {e}")
            sys.exit(1)

    try:
        import PyInstaller
        print("PyInstaller is already installed.")
    except ImportError:
        print("PyInstaller not found, installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "PyInstaller", "--break-system-packages"])
            print("PyInstaller installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install PyInstaller: {e}")
            sys.exit(1)

def create_executable():
    print("Creating executable for 98kalculator...")
    app_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(app_dir, "src")
    main_script = os.path.join(src_dir, "main.py")

    try:
        subprocess.check_call(
            [
                sys.executable, "-m", "PyInstaller",
                "--onefile", "--windowed", "--name", "98kalculator",
                main_script, "--distpath", app_dir,
            ]
        )
        print("Executable created successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to create executable with PyInstaller: {e}")
        print("Please ensure PyInstaller is installed or install it manually.")
        sys.exit(1)

def create_desktop_file():
    print("Creating .desktop file...")
    app_dir = os.path.dirname(os.path.abspath(__file__))
    executable_path = os.path.join(app_dir, "98kalculator")
    desktop_file_path = os.path.expanduser("~/.local/share/applications/98kalculator.desktop")
    icon_path = os.path.join(app_dir, "icon.png")

    desktop_content = f"""[Desktop Entry]
Name=98kalculator
Comment=The best professional purple calculator
Exec={executable_path}
Icon={icon_path}
Terminal=false
Type=Application
Categories=Utility;Calculator;Science;
"""
    try:
        os.makedirs(os.path.dirname(desktop_file_path), exist_ok=True)
        with open(desktop_file_path, "w") as f:
            f.write(desktop_content)
        
        try:
            subprocess.run(["update-desktop-database", os.path.expanduser("~/.local/share/applications")], check=True)
        except FileNotFoundError:
            pass 
            
        print(".desktop file created successfully.")
    except Exception as e:
        print(f"Failed to create .desktop file: {e}")
        sys.exit(1)

def main():
    install_dependencies()
    create_executable()
    create_desktop_file()
    print("\nInstallation complete! Launch '98kalculator' from your application menu.")

if __name__ == "__main__":
    main()
