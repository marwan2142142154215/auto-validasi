"""
Build script for creating standalone executable

Usage:
    python build_exe.py

Requirements:
    pip install pyinstaller
"""

import os
import sys
import subprocess
import shutil


def build_executable():
    """Build standalone executable using PyInstaller"""
    
    # Get current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    main_file = os.path.join(current_dir, "main.py")
    
    if not os.path.exists(main_file):
        print(f"Error: main.py not found in {current_dir}")
        return False
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",          # Single executable
        "--windowed",         # No console window (use --console if needed)
        "--name=AutoIDValidator",
        "--icon=",            # Add icon if available
        "--collect-all=playwright",
        "--collect-all=google",
        "--collect-all=requests",
        f"--paths={current_dir}",
        f"--additional-hooks-dir={current_dir}",
        "--hidden-import=playwright.sync_api",
        "--hidden-import=google.auth",
        "--hidden-import=google.oauth2.service_account",
        "--hidden-import=googleapiclient.discovery",
        "--hidden-import=googleapiclient.errors",
        "--hidden-import=requests",
        "--hidden-import=requests.api",
        "--hidden-import=requests.models",
        "--hidden-import=urllib3",
        "--hidden-import=urllib3.util",
        "--hidden-import=urllib3.packages.six",
        "--hidden-import=http",
        "--hidden-import=http.client",
        "--hidden-import=email",
        "--hidden-import=email.mime",
        "--hidden-import=email.mime.multipart",
        "--hidden-import=email.mime.text",
        "--hidden-import=email.mime.image",
        "--hidden-import=email.mime.base",
        "--hidden-import=xml",
        "--hidden-import=xml.etree",
        "--hidden-import=xml.etree.ElementTree",
        "--hidden-import=xml.etree.ElementInclude",
        "--hidden-import=xml.parsers",
        "--hidden-import=xml.parsers.expat",
        f"--distpath={os.path.join(current_dir, 'dist')}",
        f"--workpath={os.path.join(current_dir, 'build')}",
        "--clean",
        "--noupx",
        main_file
    ]
    
    print("=" * 60)
    print("Building AutoID Validator Executable")
    print("=" * 60)
    print(f"Command: {' '.join(cmd[:5])} ... (truncated)")
    print()
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, check=True)
        print()
        print("=" * 60)
        print("✅ Build successful!")
        print("=" * 60)
        print(f"Executable location: {os.path.join(current_dir, 'dist', 'AutoIDValidator.exe')}")
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed with error code: {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ PyInstaller not found.")
        print("   Install with: pip install pyinstaller")
        return False


def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    
    deps = [
        "playwright",
        "requests",
        "google-auth",
        "google-auth-oauthlib",
        "google-api-python-client",
        "pyinstaller"
    ]
    
    for dep in deps:
        print(f"  Installing {dep}...")
        subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
    
    # Install playwright browsers
    print("\nInstalling Playwright browsers...")
    subprocess.run([sys.executable, "-m", "playwright", "install"], check=True)
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)


def create_env_file():
    """Create .env.example file"""
    env_content = """# AutoID Validator - Environment Configuration
# Copy this file to .env and fill in your values

# Google Sheets Configuration
GOOGLE_SHEET_ID=1MWrSw4S0FhCu3jrFbaQVxirtcXgJaTtAyB1I_oyXzyo
GOOGLE_SHEET_GID=2136909409
GOOGLE_SERVICE_ACCOUNT_JSON=path/to/service-account.json

# Telegram Configuration
TELEGRAM_BOT_TOKEN=8454399356:AAE37qFZs0U-7OITIwrkLaJSAnZjFEVLYAo
TELEGRAM_CHAT_ID=8585992120

# CIMB OCTO Credentials (Bank Validation)
CIMB_USERNAME=linda0207
CIMB_PASSWORD=@Aa778899

# BCA Credentials (E-Wallet Validation)
BCA_USERNAME=NIPUTUAY3610
BCA_PASSWORD=788888

# Browser Settings
HEADLESS=0
SLOW_MO_MS=100
TIMEOUT_MS=30000
POLL_INTERVAL_SEC=2
MAX_ROWS_PER_RUN=0
"""
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_file = os.path.join(current_dir, ".env.example")
    
    with open(env_file, "w") as f:
        f.write(env_content)
    
    print(f"✅ Created .env.example file")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Build script for AutoID Validator")
    parser.add_argument("--install-deps", action="store_true", help="Install dependencies")
    parser.add_argument("--build", action="store_true", help="Build executable")
    parser.add_argument("--all", action="store_true", help="Install deps and build")
    
    args = parser.parse_args()
    
    if args.install_deps or args.all:
        install_dependencies()
    
    if args.build or args.all:
        create_env_file()
        build_executable()
    
    if not any([args.install_deps, args.build, args.all]):
        parser.print_help()
