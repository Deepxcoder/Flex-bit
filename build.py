"""
FlexBit AI - Automated PyInstaller Packaging & Release Script
Cleans cache artifacts, packages FlexBit AI into a standalone Windows executable distribution,
updates FlexBit_AI_v2.5_Windows directory, and creates FlexBit_AI_v2.5_Windows.zip.
"""

import os
import sys
import shutil
import zipfile
import subprocess

APP_NAME = "FlexBit_AI"
VERSION = "v2.5"
OUTPUT_ZIP_NAME = f"FlexBit_AI_{VERSION}_Windows.zip"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, "dist")
BUILD_DIR = os.path.join(BASE_DIR, "build")
TARGET_APP_DIR = os.path.join(DIST_DIR, APP_NAME)
RELEASE_FOLDER = os.path.join(BASE_DIR, f"{APP_NAME}_{VERSION}_Windows")


import stat


def force_remove_readonly(func, path, exc_info):
    """Error handler for shutil.rmtree to clear read-only permissions on Windows."""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception as e:
        print(f"[Build Warning] Force remove failed for {path}: {e}")


def force_remove_tree(folder):
    """Safely removes a directory tree ignoring read-only file locks."""
    if os.path.exists(folder):
        try:
            shutil.rmtree(folder, onexc=force_remove_readonly)
            print(f"[Build Cleaned] {folder}")
        except TypeError:
            # Fallback for Python versions where onexc is onerror
            shutil.rmtree(folder, onerror=force_remove_readonly)
            print(f"[Build Cleaned] {folder}")


def kill_running_instances():
    """Kills any running FlexBit_AI.exe processes to unlock files on Windows."""
    try:
        subprocess.run(["taskkill", "/F", "/IM", "FlexBit_AI.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def clean_build_artifacts():
    """Removes old build, dist, pycache, and cached build outputs."""
    kill_running_instances()
    print("[Build] Cleaning build caches and previous outputs...")
    folders_to_clean = [BUILD_DIR, DIST_DIR, RELEASE_FOLDER]

    for root, dirs, files in os.walk(BASE_DIR):
        for d in dirs:
            if d == "__pycache__":
                try: shutil.rmtree(os.path.join(root, d), onexc=force_remove_readonly)
                except Exception: pass

    for folder in folders_to_clean:
        force_remove_tree(folder)


def run_pyinstaller():
    print(f"[Build] Starting PyInstaller clean build for {APP_NAME}...")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onedir",
        "--windowed",
        f"--name={APP_NAME}",
        "--add-data",
        f"{os.path.join(BASE_DIR, 'index.html')};.",
        "main.py"
    ]

    print(f"[Build] Command: {' '.join(cmd)}")
    res = subprocess.run(cmd, cwd=BASE_DIR)

    if res.returncode != 0:
        print("[Build Error] PyInstaller failed with non-zero exit code.")
        sys.exit(1)

    print("[Build] PyInstaller executable built successfully.")


def prepare_dist_folder():
    """Ensures models, assets, index.html exist in dist and release package."""
    print("[Build] Preparing release directory structure...")

    models_dir = os.path.join(TARGET_APP_DIR, "models")
    os.makedirs(models_dir, exist_ok=True)

    # Copy index.html to target directory
    html_src = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(html_src):
        shutil.copy(html_src, os.path.join(TARGET_APP_DIR, "index.html"))

    # Copy README if exists
    readme_src = os.path.join(BASE_DIR, "README.md")
    if os.path.exists(readme_src):
        shutil.copy(readme_src, os.path.join(TARGET_APP_DIR, "README.md"))

    # Create a placeholder in models directory
    with open(os.path.join(models_dir, "PUT_GGUF_MODELS_HERE.txt"), "w") as f:
        f.write("Moondream 2 GGUF models will be automatically downloaded here on first launch if missing.\n")

    # Mirror to RELEASE_FOLDER
    kill_running_instances()
    force_remove_tree(RELEASE_FOLDER)
    shutil.copytree(TARGET_APP_DIR, RELEASE_FOLDER, dirs_exist_ok=True)
    print(f"[Build] Updated standalone directory: {RELEASE_FOLDER}")


def create_release_zip():
    """Zips the output folder into FlexBit_AI_v2.5_Windows.zip."""
    zip_path = os.path.join(BASE_DIR, OUTPUT_ZIP_NAME)
    print(f"[Build] Creating ZIP archive: {OUTPUT_ZIP_NAME}...")

    if os.path.exists(zip_path):
        os.remove(zip_path)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(TARGET_APP_DIR):
            for file in files:
                abs_p = os.path.join(root, file)
                rel_p = os.path.relpath(abs_p, DIST_DIR)
                zipf.write(abs_p, rel_p)

    print(f"[Build Success] Standalone Windows Release Package created: {zip_path}")


if __name__ == "__main__":
    clean_build_artifacts()
    run_pyinstaller()
    prepare_dist_folder()
    create_release_zip()
