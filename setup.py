import os
import subprocess
import sys


def ensure_pip():
    """
    Makes sure the Python package manager Pip is installed.
    """
    try:
        subprocess.check_call([sys.executable, "-m", "ensurepip"])
        print("Pip is installed or upgraded successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to install or upgrade pip. {e}")


def install_dependencies():
    """
    Installs the required dependencies.
    """
    try:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", f"{dir_path}/requirements.txt"])
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to install dependencies. {e}")


if __name__ == "__main__":
    ensure_pip()
    install_dependencies()
