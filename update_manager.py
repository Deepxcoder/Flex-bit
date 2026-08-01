import os
import sys
import json
import tempfile
import subprocess
import requests
from packaging.version import parse as parse_version

CURRENT_VERSION = "2.5.0"
DEFAULT_MANIFEST_URL = "https://raw.githubusercontent.com/deepxcoder/flexbit-ai/main/version.json"


class UpdateManager:
    def __init__(self, current_version=CURRENT_VERSION, manifest_url=DEFAULT_MANIFEST_URL):
        self.current_version = current_version
        self.manifest_url = manifest_url
        self.is_downloading = False

    def check_for_updates(self):
        """
        Fetches remote release manifest and compares versions.
        Returns dict with status, latest version, and changelog.
        """
        try:
            resp = requests.get(self.manifest_url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                latest = data.get("latest_version", self.current_version)

                if parse_version(latest) > parse_version(self.current_version):
                    return {
                        "status": "update_available",
                        "has_update": True,
                        "current_version": self.current_version,
                        "latest_version": latest,
                        "release_date": data.get("release_date", ""),
                        "changelog": data.get("changelog", []),
                        "download_url": data.get("download_url", ""),
                        "mandatory": data.get("mandatory", False),
                        "message": f"FlexBit AI v{latest} is available!"
                    }
                else:
                    return {
                        "status": "up_to_date",
                        "has_update": False,
                        "current_version": self.current_version,
                        "latest_version": latest,
                        "message": "FlexBit AI is up to date."
                    }
        except Exception as e:
            print(f"[UpdateManager] Check for updates failed (offline or network timeout): {e}")

        return {
            "status": "up_to_date",
            "has_update": False,
            "current_version": self.current_version,
            "message": "FlexBit AI is up to date (Offline Mode)."
        }

    def download_update(self, download_url, target_path=None, progress_callback=None):
        """
        Downloads update package file with streaming byte progress reports.
        """
        if not download_url:
            return False, "Invalid download URL."

        if not target_path:
            target_path = os.path.join(tempfile.gettempdir(), "flexbit_update_latest.zip")

        self.is_downloading = True
        try:
            resp = requests.get(download_url, stream=True, timeout=30)
            resp.raise_for_status()

            total_bytes = int(resp.headers.get("content-length", 0))
            downloaded = 0

            with open(target_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_bytes > 0:
                            pct = round((downloaded / total_bytes) * 100, 1)
                            progress_callback(downloaded, total_bytes, pct)

            return True, target_path
        except Exception as e:
            return False, str(e)
        finally:
            self.is_downloading = False

    def apply_update_and_restart(self, zip_path):
        """
        Launches detached batch installer script to replace app files and restart FlexBit_AI.exe.
        """
        if not os.path.exists(zip_path):
            return False, "Update package file not found."

        app_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.abspath(os.path.dirname(__file__))
        bat_script = os.path.join(tempfile.gettempdir(), "flexbit_autoupdater.bat")

        script_content = f"""@echo off
title FlexBit AI Auto-Updater
echo Updating FlexBit AI to latest release...
timeout /t 2 /nobreak > NUL
powershell -Command "Expand-Archive -Path '{zip_path}' -DestinationPath '{app_dir}' -Force"
if exist "{zip_path}" del "{zip_path}"
start "" "{os.path.join(app_dir, 'FlexBit_AI.exe')}"
del "%~f0"
"""
        try:
            with open(bat_script, "w") as f:
                f.write(script_content)

            subprocess.Popen(["cmd.exe", "/c", bat_script], creationflags=subprocess.CREATE_NEW_CONSOLE)
            sys.exit(0)
        except Exception as e:
            return False, f"Failed to launch update installer: {e}"
