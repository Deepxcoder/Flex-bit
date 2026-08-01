"""
FlexBit AI — PyWebView + HTML5 + Tailwind CSS Desktop Application
Main Entry Point & Python-to-JavaScript Bridge API Controller.
Provides Live Previews, Multi-Phase Batch Processing, Interactive Navigation,
Dynamic Duration Estimation, and Session Undo Vault API.
"""

import os
import sys
import shutil
import time
import json
import threading
from datetime import datetime
from pathlib import Path

# PyWebView Imports
import webview

# FlexBit Core Engines
from config import ConfigManager
from history import HistoryManager
from ai_engine import VisionModelEngine, check_models_exist, scan_server_models, check_server_health
from update_manager import UpdateManager

IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif', '.tiff', '.heic'}
DOC_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt', '.csv', '.xlsx', '.md'}
MEDIA_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.mp3', '.wav', '.flac', '.aac'}
ALL_SUPPORTED_EXTENSIONS = IMAGE_EXTENSIONS | DOC_EXTENSIONS | MEDIA_EXTENSIONS


def get_resource_path(relative_path):
    """Resolves resource path for both script execution and PyInstaller bundling."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


class FlexBitAPI:
    """Python API class exposed to JavaScript inside PyWebView."""
    def __init__(self):
        self.cfg_mgr = ConfigManager()
        self.history_mgr = HistoryManager()
        self.update_mgr = UpdateManager()
        self._ai_engine_inst = None
        self.window = None
        self._is_processing = False
        self._cancel_requested = False

        # Background async warmup so startup is 100% instant
        threading.Thread(target=self._async_warmup, daemon=True).start()

    def _async_warmup(self):
        try:
            from ai_engine import preload_model_async
            preload_model_async()
        except Exception as e:
            print(f"[API Init Warning]: {e}")

    @property
    def ai_engine(self):
        if self._ai_engine_inst is None:
            from ai_engine import VisionModelEngine
            self._ai_engine_inst = VisionModelEngine(
                provider=self.cfg_mgr.get("model_provider", "embedded"),
                server_url=self.cfg_mgr.get("server_url", "http://localhost:1234/v1"),
                selected_model=self.cfg_mgr.get("selected_model", ""),
                local_gguf_path=self.cfg_mgr.get("local_gguf_path", ""),
                n_threads=self.cfg_mgr.get("n_threads", 4)
            )
        return self._ai_engine_inst

    def set_window(self, window):
        self.window = window

    def search_media_semantic(self, query="", directory=""):
        """Performs natural language semantic search across files in workspace directory."""
        if isinstance(query, dict):
            directory = query.get("directory", directory)
            query = query.get("query", "")

        if not query or not str(query).strip():
            return {"status": "error", "message": "Search query cannot be empty."}
        
        query_str = str(query).strip()
        
        if not directory or not os.path.exists(directory):
            directory = os.path.expanduser("~")

        try:
            from ai_engine import semantic_search_files
            results = semantic_search_files(query_str, directory)
            return {"status": "success", "total_matches": len(results), "items": results}
        except Exception as e:
            print(f"[API] Semantic Search Error: {e}")
            return {"status": "error", "message": str(e)}

    def _get_unique_path(self, target_path):
        """Ensures target_path does not overwrite an existing file by appending _1, _2, etc."""
        if not os.path.exists(target_path):
            return target_path
        dirname, basename = os.path.split(target_path)
        name, ext = os.path.splitext(basename)
        counter = 1
        while True:
            new_path = os.path.join(dirname, f"{name}_{counter}{ext}")
            if not os.path.exists(new_path):
                return new_path
            counter += 1

    def open_in_explorer(self, target_path=""):
        """Opens target file or directory in Windows File Explorer."""
        if not target_path or not os.path.exists(target_path):
            return {"status": "error", "message": "Path does not exist."}
        try:
            norm_p = os.path.normpath(target_path)
            if os.path.isfile(norm_p):
                import subprocess
                subprocess.Popen(['explorer', '/select,', norm_p])
            else:
                os.startfile(norm_p)
            return {"status": "success", "message": "Opened in File Explorer."}
        except Exception as e:
            print(f"[API] Error opening in explorer: {e}")
            return {"status": "error", "message": str(e)}

    def cancel_active_task(self):
        """Signals the active batch worker thread to stop immediately."""
        if self._is_processing:
            self._cancel_requested = True
            return {"status": "success", "message": "Cancellation request sent to active task."}
        return {"status": "info", "message": "No active task is running."}

    def check_for_updates(self):
        """Checks GitHub release manifest for updates."""
        return self.update_mgr.check_for_updates()

    def download_and_apply_update(self, download_url=None):
        """Downloads update package and restarts application."""
        if not download_url:
            check_res = self.update_mgr.check_for_updates()
            if not check_res.get("has_update"):
                return {"status": "info", "message": "FlexBit AI is already up to date."}
            download_url = check_res.get("download_url")

        def _update_worker():
            def _progress_cb(downloaded, total, pct):
                self._emit_progress("Downloading Update", 1, 1, "FlexBit AI Update Package", "", pct, f"{round(downloaded/1024/1024, 1)}MB / {round(total/1024/1024, 1)}MB")

            success, res_path = self.update_mgr.download_update(download_url, progress_callback=_progress_cb)
            if success:
                self._emit_progress("Applying Update", 1, 1, "Relaunching FlexBit AI...", "", 100.0, "Update package verified.")
                self.update_mgr.apply_update_and_restart(res_path)
            else:
                self._emit_progress("Update Error", 0, 1, "Failed to download update", "", 0.0, str(res_path))

        threading.Thread(target=_update_worker, daemon=True).start()
        return {"status": "started", "message": "Downloading update in background..."}

    def _emit_progress(self, phase, current_idx, total_count, file_name, new_name="", percentage=0.0, details=""):
        """Evaluates JS callback window.onBatchProgress with live telemetry."""
        if self.window:
            payload = json.dumps({
                "phase": phase,
                "current_idx": current_idx,
                "total_count": total_count,
                "file_name": file_name,
                "new_name": new_name,
                "percentage": round(percentage, 1),
                "details": details
            })
            try:
                self.window.evaluate_js(f"if(window.onBatchProgress) window.onBatchProgress({payload});")
            except Exception as e:
                print(f"[Progress Emission Error]: {e}")

    def select_directory(self):
        """Opens native directory picker dialog and returns path to JS with Tkinter fallback."""
        folder = ""
        if self.window:
            try:
                result = self.window.create_file_dialog(webview.FOLDER_DIALOG)
                if result and len(result) > 0 and result[0]:
                    folder = result[0]
            except Exception as e:
                print(f"[API] PyWebView dialog error: {e}")

        if not folder:
            try:
                import tkinter as tk
                from tkinter import filedialog
                root = tk.Tk()
                root.withdraw()
                root.attributes('-topmost', True)
                try:
                    folder = filedialog.askdirectory(title="Select Media Workspace Directory")
                finally:
                    root.destroy()
            except Exception as e:
                print(f"[API] Tkinter dialog fallback error: {e}")

        return folder or ""

    def select_files(self):
        """Opens native file picker dialog allowing users to select individual media/document files."""
        files = []
        if self.window:
            try:
                result = self.window.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=True)
                if result and len(result) > 0:
                    files = list(result)
            except Exception as e:
                print(f"[API] PyWebView file dialog error: {e}")

        if not files:
            try:
                import tkinter as tk
                from tkinter import filedialog
                root = tk.Tk()
                root.withdraw()
                root.attributes('-topmost', True)
                try:
                    result = filedialog.askopenfilenames(title="Select Media or Document Files")
                    if result:
                        files = list(result)
                finally:
                    root.destroy()
            except Exception as e:
                print(f"[API] Tkinter file dialog fallback error: {e}")

        return files

    def get_config(self):
        """Returns current configuration dictionary to JS."""
        return self.cfg_mgr.config

    def save_config(self, new_config):
        """Saves configuration from JS and updates engine."""
        self.cfg_mgr.save_config(new_config)
        self.ai_engine.update_config(
            provider=new_config.get("model_provider", "embedded"),
            server_url=new_config.get("server_url", "http://localhost:1234/v1"),
            selected_model=new_config.get("selected_model", ""),
            local_gguf_path=new_config.get("local_gguf_path", ""),
            n_threads=new_config.get("n_threads", 4)
        )
        return {"status": "success", "message": "Settings saved successfully!"}

    def reset_account(self):
        """Resets user config to initial fresh app state."""
        cfg = self.cfg_mgr.reset_config()
        self.ai_engine.update_config(
            provider=cfg.get("model_provider", "embedded"),
            server_url=cfg.get("server_url", "http://localhost:1234/v1"),
            selected_model=cfg.get("selected_model", ""),
            local_gguf_path=cfg.get("local_gguf_path", ""),
            n_threads=cfg.get("n_threads", 4)
        )
        return {"status": "success", "message": "Account profile reset to default!", "config": cfg}

    def scan_models(self, provider, server_url):
        """Scans local LM Studio or Ollama server for vision models."""
        models = scan_server_models(provider, server_url)
        return {"models": models}

    def get_directory_preview(self, config):
        """
        Scans active directory and returns real live file previews and dynamically calculated expected duration.
        """
        target_dir = config.get("directory", "")
        personality = config.get("personality", "natural")
        pattern = config.get("pattern", "vibrant")
        language = config.get("language", "English")

        if not target_dir or not os.path.exists(target_dir):
            return {
                "status": "error",
                "message": "Invalid or missing directory.",
                "items": [],
                "total_files": 0,
                "expected_duration_str": "0s"
            }

        try:
            entries = [f for f in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, f)) and os.path.splitext(f)[1].lower() in ALL_SUPPORTED_EXTENSIONS]
            if not entries:
                entries = [f for f in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, f))]
        except Exception as e:
            return {"status": "error", "message": str(e), "items": [], "total_files": 0, "expected_duration_str": "0s"}

        # Calculate estimated duration based on AI provider speed
        provider = self.ai_engine.provider
        if provider == "embedded":
            per_file_sec = 2.2
        elif provider in ["lm_studio", "ollama"]:
            per_file_sec = 1.2
        else:
            per_file_sec = 0.08

        total_files = len(entries)
        est_duration = max(1, int(total_files * per_file_sec))
        duration_str = f"{est_duration}s" if est_duration < 60 else f"{est_duration // 60}m {est_duration % 60}s"

        preview_items = []
        max_preview = config.get("max_items", 500)
        for idx, fname in enumerate(entries[:max_preview]):
            fpath = os.path.join(target_dir, fname)
            ext = os.path.splitext(fname)[1].lower()
            is_img = ext in IMAGE_EXTENSIONS
            fsize = 0
            try:
                fsize = os.path.getsize(fpath)
            except Exception:
                pass

            if is_img:
                desc = self.ai_engine._heuristic_vision_analyzer(fpath, language)
                ext_str = ext or ".png"
                try:
                    mtime = os.path.getmtime(fpath)
                except Exception:
                    mtime = time.time()
                f_date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
                date_pat = f"{f_date}_{idx+1:03d}"
                pat_u = pattern.upper()
                p_str = personality.lower()
                emoji_p = "🎮" if "gamer" in p_str else ("🍿" if "movie" in p_str else ("🎵" if "music" in p_str else ("🌌" if "poetic" in p_str else "🖼️")))

                if "VIBRANT" in pat_u or "BOTH" in pat_u:
                    predicted_name = f"{emoji_p} {date_pat}_{desc}{ext_str}".strip()
                elif "TIMESTAMPS" in pat_u or "PATTERN ONLY" in pat_u:
                    predicted_name = f"{date_pat}_{desc}{ext_str}"
                elif "ORG" in pat_u or "COUNTER" in pat_u:
                    predicted_name = f"{idx+1:03d}_{desc}{ext_str}"
                else:
                    predicted_name = f"{desc}{ext_str}"
            else:
                predicted_name = fname

            preview_items.append({
                "original_name": fname,
                "predicted_name": predicted_name,
                "original_path": fpath,
                "is_image": is_img,
                "size": fsize,
                "ext": ext
            })

        return {
            "status": "success",
            "directory": target_dir,
            "total_files": total_files,
            "expected_duration_str": duration_str,
            "items": preview_items
        }

    def get_directory_contents(self, target_dir=""):
        """
        Lists files and subdirectories for interactive double-click navigation.
        """
        if not target_dir:
            target_dir = os.path.expanduser("~")

        if not os.path.exists(target_dir):
            return {"status": "error", "message": "Directory does not exist."}

        try:
            items = []
            parent_dir = os.path.dirname(target_dir) if target_dir != os.path.dirname(target_dir) else ""

            for name in os.listdir(target_dir):
                full_p = os.path.join(target_dir, name)
                is_d = os.path.isdir(full_p)
                size_b = 0
                ext = ""
                if not is_d:
                    try: size_b = os.path.getsize(full_p)
                    except Exception: pass
                    ext = os.path.splitext(name)[1].lower()

                items.append({
                    "name": name,
                    "path": full_p,
                    "is_dir": is_d,
                    "size": size_b,
                    "ext": ext
                })

            # Sort: directories first, then files alphabetically
            items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))

            return {
                "status": "success",
                "current_dir": target_dir,
                "parent_dir": parent_dir,
                "items": items
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def start_renaming(self, config):
        """Executes AI Batch Renaming on target directory with multi-phase live progress reporting."""
        if self._is_processing:
            return {"status": "error", "message": "Another task is currently running."}

        def _worker():
            self._is_processing = True
            self._cancel_requested = False
            target_dir = config.get("directory", "")
            personality = config.get("personality", "natural")
            pattern = config.get("pattern", "vibrant")
            language = config.get("language", "English")

            if not target_dir or not os.path.exists(target_dir):
                self._emit_progress("Error", 0, 0, "", "", 0, "Invalid target directory.")
                self._is_processing = False
                return

            try:
                entries = [f for f in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, f))]
            except Exception as e:
                self._emit_progress("Error", 0, 0, "", "", 0, f"Could not read directory: {e}")
                self._is_processing = False
                return

            selected_files = config.get("selected_files", [])
            if selected_files and isinstance(selected_files, list) and len(selected_files) > 0:
                sel_set = set(selected_files)
                entries = [f for f in entries if f in sel_set or os.path.join(target_dir, f) in sel_set]

            total_count = len(entries)
            if total_count == 0:
                self._emit_progress("Completion Phase", 0, 0, "", "", 100, "No files found in directory.")
                self._is_processing = False
                return

            # Phase 1: Counting Phase
            self._emit_progress("Counting Phase", 0, total_count, "Indexing files...", "", 5.0, f"Indexed {total_count} asset(s)")
            time.sleep(0.4)

            # Phase 2: Analyzing Phase
            cheat_mode = config.get("cheat_mode", "")
            ops_log = []
            for idx, fname in enumerate(entries):
                if self._cancel_requested:
                    self._emit_progress("Cancelled Phase", idx, total_count, fname, "", (idx / total_count) * 100, "Task cancelled by user.")
                    self._is_processing = False
                    return

                fpath = os.path.join(target_dir, fname)
                pct = 5.0 + ((idx + 1) / total_count) * 85.0

                try:
                    ext = os.path.splitext(fname)[1].lower()
                    if cheat_mode == "deeplovesbushu":
                        new_name = f"deeplovebushu-{idx + 1}{ext or '.jpg'}"
                    elif cheat_mode == "romanticdesire":
                        romantic_words = ["Passionate_Glow", "Seductive_Gaze", "Intimate_Moment", "Midnight_Desire", "Sensual_Whisper", "Velvet_Touch"]
                        word = romantic_words[idx % len(romantic_words)]
                        new_name = f"Romantic_Desire_{idx + 1:03d}_{word}{ext or '.jpg'}"
                    elif ext in IMAGE_EXTENSIONS:
                        new_name = self.ai_engine.generate_filename(
                            fpath,
                            persona=personality,
                            language=language,
                            pattern=pattern,
                            counter_idx=idx + 1
                        )
                    else:
                        new_name = fname

                    target_p = os.path.join(target_dir, new_name)
                    if target_p != fpath and os.path.exists(fpath):
                        target_p = self._get_unique_path(target_p)
                        new_name = os.path.basename(target_p)

                    self._emit_progress(
                        "Analyzing Phase",
                        idx + 1,
                        total_count,
                        fname,
                        new_name,
                        pct,
                        f"Renaming item {idx + 1} of {total_count}"
                    )

                    if target_p != fpath and os.path.exists(fpath):
                        os.rename(fpath, target_p)
                        ops_log.append({
                            "original_path": fpath,
                            "new_path": target_p,
                            "original_name": fname,
                            "new_name": new_name,
                            "details": f"{personality} | {language} | {pattern}"
                        })
                except Exception as ex:
                    print(f"Rename failed for {fname}: {ex}")

            # Phase 3: Completion Phase
            if ops_log:
                sess_rec = self.history_mgr.log_session("rename", ops_log, personality, language, pattern)
                sess_name = sess_rec.get("session_name", sess_rec.get("session_id"))
                msg = f"Renamed {len(ops_log)} file(s) in session '{sess_name}'!"
            else:
                msg = "No files required renaming."

            self._emit_progress("Completion Phase", total_count, total_count, "Done", "", 100.0, msg)
            self._is_processing = False

        t = threading.Thread(target=_worker, daemon=True)
        t.start()
        return {"status": "started", "message": "Batch renaming initiated in live multi-phase mode."}

    def run_junk_quarantine(self, depth="deep", target_dir="", selected_files=None):
        """Quarantines unnecessary files into _Unnecessary_Files directory with live progress."""
        if self._is_processing:
            return {"status": "error", "message": "Another task is currently running."}

        if not target_dir:
            target_dir = self.select_directory()

        if not target_dir or not os.path.exists(target_dir):
            return {"status": "error", "message": "No directory selected."}

        def _worker():
            self._is_processing = True
            self._cancel_requested = False
            quarantine_dir = os.path.join(target_dir, "_Unnecessary_Files")
            ops_log = []

            try:
                entries = [f for f in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, f))]
            except Exception as e:
                self._emit_progress("Error", 0, 0, "", "", 0, str(e))
                self._is_processing = False
                return

            if selected_files and isinstance(selected_files, list) and len(selected_files) > 0:
                sel_set = set(selected_files)
                entries = [f for f in entries if f in sel_set or os.path.join(target_dir, f) in sel_set]

            total_count = len(entries)
            if total_count == 0:
                self._emit_progress("Completion Phase", 0, 0, "", "", 100, "No files found to clean.")
                self._is_processing = False
                return

            # Phase 1: Counting Phase
            self._emit_progress("Counting Phase", 0, total_count, "Scanning directory for junk files...", "", 5.0, f"Found {total_count} files")
            time.sleep(0.4)

            # Phase 2: Analyzing Phase
            for idx, fname in enumerate(entries):
                if self._cancel_requested:
                    self._emit_progress("Cancelled Phase", idx, total_count, fname, "", (idx / total_count) * 100, "Task cancelled by user.")
                    self._is_processing = False
                    return

                fpath = os.path.join(target_dir, fname)
                pct = 5.0 + ((idx + 1) / total_count) * 85.0

                try:
                    is_junk, reason = self.ai_engine.inspect_file_for_junk(fpath)

                    self._emit_progress(
                        "Analyzing Phase",
                        idx + 1,
                        total_count,
                        fname,
                        f"_Unnecessary_Files/{fname}" if is_junk else "Clean",
                        pct,
                        f"Inspecting {fname}: {reason}"
                    )

                    if is_junk and os.path.exists(fpath):
                        os.makedirs(quarantine_dir, exist_ok=True)
                        target_p = os.path.join(quarantine_dir, fname)
                        target_p = self._get_unique_path(target_p)
                        final_fname = os.path.basename(target_p)
                        shutil.move(fpath, target_p)
                        ops_log.append({
                            "original_path": fpath,
                            "new_path": target_p,
                            "original_name": fname,
                            "new_name": final_fname,
                            "details": f"{depth.upper()} Clean: {reason}"
                        })
                except Exception as ex:
                    print(f"Quarantine error for {fname}: {ex}")

            # Phase 3: Completion Phase
            if ops_log:
                sess_rec = self.history_mgr.log_session("quarantine", ops_log, "Quarantine", "English", depth)
                sess_name = sess_rec.get("session_name", sess_rec.get("session_id"))
                msg = f"Quarantined {len(ops_log)} file(s) in session '{sess_name}'!"
            else:
                msg = "No junk files detected."

            self._emit_progress("Completion Phase", total_count, total_count, "Done", "", 100.0, msg)
            self._is_processing = False

        t = threading.Thread(target=_worker, daemon=True)
        t.start()
        return {"status": "started", "message": f"{depth.capitalize()} clean initiated in live multi-phase mode."}

    def _format_subfolder(self, subfolder, naming_scheme="standard"):
        """Formats target subfolder according to chosen folder naming scheme."""
        if not subfolder:
            return "Uncategorized"
        
        scheme = str(naming_scheme).lower()
        if scheme == "lowercase":
            return subfolder.lower()
        elif scheme == "emoji":
            emoji_map = {
                "Photos": "🖼️ Photos",
                "Images": "🖼️ Images",
                "Documents": "📄 Documents",
                "Invoices": "🧾 Invoices",
                "Work": "💼 Work",
                "Code": "💻 Code",
                "Archives": "📦 Archives",
                "Executables": "⚙️ Executables",
                "Audio": "🎵 Audio",
                "Video": "🎬 Video",
                "Personal": "👤 Personal",
                "Others": "📁 Others",
                "Uncategorized": "📂 Uncategorized"
            }
            return emoji_map.get(subfolder, f"📁 {subfolder}")
        elif scheme == "dated":
            today_str = datetime.now().strftime("%Y-%m")
            return f"{today_str}_{subfolder}"
        else: # standard
            return subfolder

    def get_organization_preview(self, target_dir="", strategy="content", naming_scheme="standard"):
        """Returns live tree preview mapping of files to target subfolders."""
        if not target_dir or not os.path.exists(target_dir):
            return {"status": "error", "message": "Directory not found", "tree": {}}

        try:
            entries = [f for f in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, f))]
            folder_tree = {}

            for fname in entries[:300]:
                ext = os.path.splitext(fname)[1].lower()
                subfolder = "Uncategorized"

                if strategy == "extensions":
                    if ext in {'.jpg', '.png', '.jpeg', '.webp', '.gif', '.bmp'}: subfolder = "Images"
                    elif ext in {'.pdf', '.docx', '.xlsx', '.pptx', '.txt', '.csv'}: subfolder = "Documents"
                    elif ext in {'.zip', '.rar', '.7z', '.tar', '.gz'}: subfolder = "Archives"
                    elif ext in {'.exe', '.msi', '.apk', '.dmg'}: subfolder = "Executables"
                    elif ext in {'.py', '.js', '.html', '.css', '.json', '.cpp'}: subfolder = "Code"
                    elif ext in {'.mp3', '.wav', '.flac', '.aac'}: subfolder = "Audio"
                    elif ext in {'.mp4', '.mkv', '.avi', '.mov'}: subfolder = "Video"
                    else: subfolder = "Others"

                elif strategy == "modifier":
                    try:
                        fpath = os.path.join(target_dir, fname)
                        mtime = os.path.getmtime(fpath)
                        subfolder = time.strftime("%Y-%m", time.localtime(mtime))
                    except Exception:
                        subfolder = "Date_Unknown"

                elif strategy == "nesting":
                    try:
                        fpath = os.path.join(target_dir, fname)
                        mtime = os.path.getmtime(fpath)
                        year = time.strftime("%Y", time.localtime(mtime))
                        cat = "Media" if ext in IMAGE_EXTENSIONS else "Docs"
                        ext_clean = ext.replace('.', '').upper() or "FILE"
                        subfolder = f"{cat}/{year}/{ext_clean}"
                    except Exception:
                        subfolder = "Nested_Misc"

                else: # "content"
                    fname_lower = fname.lower()
                    if any(k in fname_lower for k in ["invoice", "receipt", "bill", "tax"]): subfolder = "Invoices"
                    elif any(k in fname_lower for k in ["report", "doc", "letter", "legal"]): subfolder = "Documents"
                    elif ext in IMAGE_EXTENSIONS: subfolder = "Photos"
                    elif any(k in fname_lower for k in ["work", "project", "task"]): subfolder = "Work"
                    elif ext in {'.py', '.js', '.html', '.css', '.json'}: subfolder = "Code"
                    else: subfolder = "Personal"

                formatted_folder = self._format_subfolder(subfolder, naming_scheme)

                if formatted_folder not in folder_tree:
                    folder_tree[formatted_folder] = []
                folder_tree[formatted_folder].append(fname)

            return {
                "status": "success",
                "total_files": len(entries),
                "folder_count": len(folder_tree),
                "tree": folder_tree
            }
        except Exception as e:
            return {"status": "error", "message": str(e), "tree": {}}

    def run_file_organization(self, strategy="content", target_dir="", selected_files=None, naming_scheme="standard"):
        """
        Organizes workspace files according to core organizational strategies.
        """
        if self._is_processing:
            return {"status": "error", "message": "Another task is currently running."}

        if not target_dir:
            target_dir = self.select_directory()

        if not target_dir or not os.path.exists(target_dir):
            return {"status": "error", "message": "No directory selected."}

        def _worker():
            self._is_processing = True
            self._cancel_requested = False
            ops_log = []

            try:
                entries = [f for f in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, f))]
            except Exception as e:
                self._emit_progress("Error", 0, 0, "", "", 0, str(e))
                self._is_processing = False
                return

            if selected_files and isinstance(selected_files, list) and len(selected_files) > 0:
                sel_set = set(selected_files)
                entries = [f for f in entries if f in sel_set or os.path.join(target_dir, f) in sel_set]

            total_count = len(entries)
            if total_count == 0:
                self._emit_progress("Completion Phase", 0, 0, "", "", 100, "No files found to organize.")
                self._is_processing = False
                return

            # Phase 1: Counting Phase
            self._emit_progress("Counting Phase", 0, total_count, f"Indexing files for {strategy} organization...", "", 5.0, f"Found {total_count} files")
            time.sleep(0.4)

            # Phase 2: Analyzing Phase
            for idx, fname in enumerate(entries):
                if self._cancel_requested:
                    self._emit_progress("Cancelled Phase", idx, total_count, fname, "", (idx / total_count) * 100, "Task cancelled by user.")
                    self._is_processing = False
                    return

                fpath = os.path.join(target_dir, fname)
                pct = 5.0 + ((idx + 1) / total_count) * 85.0

                try:
                    ext = os.path.splitext(fname)[1].lower()
                    subfolder = "Uncategorized"
                    if strategy == "extensions":
                        if ext in {'.jpg', '.png', '.jpeg', '.webp', '.gif', '.bmp'}: subfolder = "Images"
                        elif ext in {'.pdf', '.docx', '.xlsx', '.pptx', '.txt', '.csv'}: subfolder = "Documents"
                        elif ext in {'.zip', '.rar', '.7z', '.tar', '.gz'}: subfolder = "Archives"
                        elif ext in {'.exe', '.msi', '.apk', '.dmg'}: subfolder = "Executables"
                        elif ext in {'.py', '.js', '.html', '.css', '.json', '.cpp'}: subfolder = "Code"
                        elif ext in {'.mp3', '.wav', '.flac', '.aac'}: subfolder = "Audio"
                        elif ext in {'.mp4', '.mkv', '.avi', '.mov'}: subfolder = "Video"
                        else: subfolder = "Others"

                    elif strategy == "modifier":
                        try:
                            mtime = os.path.getmtime(fpath)
                            subfolder = time.strftime("%Y-%m", time.localtime(mtime))
                        except Exception:
                            subfolder = "Date_Unknown"

                    elif strategy == "nesting":
                        try:
                            mtime = os.path.getmtime(fpath)
                            year = time.strftime("%Y", time.localtime(mtime))
                            cat = "Media" if ext in IMAGE_EXTENSIONS else "Docs"
                            ext_clean = ext.replace('.', '').upper() or "FILE"
                            subfolder = os.path.join(cat, year, ext_clean)
                        except Exception:
                            subfolder = "Nested_Misc"

                    else: # "content"
                        fname_lower = fname.lower()
                        if any(k in fname_lower for k in ["invoice", "receipt", "bill", "tax"]): subfolder = "Invoices"
                        elif any(k in fname_lower for k in ["report", "doc", "letter", "legal"]): subfolder = "Documents"
                        elif ext in IMAGE_EXTENSIONS: subfolder = "Photos"
                        elif any(k in fname_lower for k in ["work", "project", "task"]): subfolder = "Work"
                        elif ext in {'.py', '.js', '.html', '.css', '.json'}: subfolder = "Code"
                        else: subfolder = "Personal"

                    subfolder = self._format_subfolder(subfolder, naming_scheme)
                    dest_dir = os.path.join(target_dir, subfolder)
                    target_p = os.path.join(dest_dir, fname)

                    self._emit_progress(
                        "Analyzing Phase",
                        idx + 1,
                        total_count,
                        fname,
                        f"{subfolder}/{fname}",
                        pct,
                        f"Moving to folder: {subfolder}"
                    )

                    if target_p != fpath and os.path.exists(fpath):
                        os.makedirs(dest_dir, exist_ok=True)
                        target_p = self._get_unique_path(target_p)
                        final_fname = os.path.basename(target_p)
                        shutil.move(fpath, target_p)
                        ops_log.append({
                            "original_path": fpath,
                            "new_path": target_p,
                            "original_name": fname,
                            "new_name": final_fname,
                            "details": f"Strategy: {strategy.capitalize()} -> {subfolder}"
                        })
                except Exception as ex:
                    print(f"Organization move error for {fname}: {ex}")

            # Phase 3: Completion Phase
            if ops_log:
                sess_rec = self.history_mgr.log_session("organize", ops_log, "Organizer", "English", strategy.capitalize())
                sess_name = sess_rec.get("session_name", sess_rec.get("session_id"))
                msg = f"Organized {len(ops_log)} file(s) into subfolders in session '{sess_name}'!"
            else:
                msg = "No files required organization."

            self._emit_progress("Completion Phase", total_count, total_count, "Done", "", 100.0, msg)
            self._is_processing = False

        t = threading.Thread(target=_worker, daemon=True)
        t.start()
        return {"status": "started", "message": f"File organization ({strategy}) initiated in live multi-phase mode."}

    def get_history(self, sort_order="recent"):
        """Returns recorded session history logs to JavaScript with sorting."""
        return self.history_mgr.get_sessions(sort_order)

    def revert_session(self, session_id):
        """Reverts all file operations in a given session."""
        success, msg = self.history_mgr.revert_session(session_id)
        return {"success": success, "message": msg}

    def revert_session_files(self, session_id, target_paths=None):
        """Reverts specific files or all files in a session."""
        success, msg = self.history_mgr.revert_session_files(session_id, target_paths)
        return {"success": success, "message": msg}


def main():
    api = FlexBitAPI()
    html_file = get_resource_path("index.html")

    if os.path.exists(html_file):
        with open(html_file, "r", encoding="utf-8") as f:
            html_content = f.read()
    else:
        html_content = "<html><body style='background:#080A10;color:white;'><h2>index.html missing!</h2></body></html>"

    window = webview.create_window(
        title="FlexBit AI — Stitch Glassmorphic Edition",
        html=html_content,
        js_api=api,
        width=1120,
        height=760,
        resizable=True,
        background_color="#080A10"
    )
    api.set_window(window)

    webview.start(debug=False)


if __name__ == "__main__":
    main()
