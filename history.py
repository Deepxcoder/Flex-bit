"""
FlexBit AI - Session-Wise History & Undo Vault Engine
Groups operations into Sessions with Catchy Names, Partial Revert capabilities, and multi-field sorting.
"""

import os
import json
import shutil
import uuid
import random
from datetime import datetime

HISTORY_FILE_PATH = os.path.expanduser("~/.flexbit_history.json")

ADJECTIVES = [
    "Beautiful", "Yellow", "Velvet", "Emerald", "Golden", "Midnight",
    "Crystal", "Neon", "Ruby", "Sapphire", "Solar", "Cosmic",
    "Silent", "Radiant", "Serene", "Amber", "Vibrant", "Celestial",
    "Mystic", "Oceanic", "Silver", "Crimson", "Luminous", "Prismatic"
]

NOUNS = [
    "Sunday", "Watermelon", "Sunset", "Horizon", "Breeze", "Echo",
    "Stream", "Meadow", "Dawn", "Rain", "Whisper", "Voyage",
    "Orchard", "Starlight", "Cascade", "Galaxy", "Lagoon", "Forest",
    "Phoenix", "Blossom", "Haven", "Mirage", "Zenith", "Banyan"
]


def generate_session_name():
    """Generates a memorable catchy session name like 'Beautiful Sunday' or 'Yellow Watermelon'."""
    adj = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS)
    return f"{adj} {noun}"


class HistoryManager:
    def __init__(self, filepath=HISTORY_FILE_PATH):
        self.filepath = filepath
        self._ensure_history_file()

    def _ensure_history_file(self):
        """Creates history JSON if missing."""
        if not os.path.exists(self.filepath):
            self._save_data([])

    def _load_data(self):
        """Reads sessions array from JSON file."""
        try:
            if os.path.exists(self.filepath):
                with open(self.filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"[HistoryManager] Error reading history: {e}")
        return []

    def _save_data(self, data):
        """Writes sessions array to JSON file atomically."""
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[HistoryManager] Error writing history: {e}")

    def log_session(self, op_type, file_ops, persona="Normal", language="English", pattern="Clean Natural Sentence", custom_name=None):
        """
        Logs an entire batch run as a Session with a catchy human-readable name.
        :param op_type: 'rename', 'quarantine', or 'organize'
        :param file_ops: List of dicts [{original_path, new_path, original_name, new_name, details}]
        """
        sessions = self._load_data()
        session_id = str(uuid.uuid4())[:8]
        session_name = custom_name or generate_session_name()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Mark individual operations as active (not reverted)
        ops_with_status = []
        for op in file_ops:
            op_copy = dict(op)
            if "reverted" not in op_copy:
                op_copy["reverted"] = False
            ops_with_status.append(op_copy)

        session_record = {
            "session_id": session_id,
            "session_name": session_name,
            "timestamp": timestamp,
            "op_type": op_type,
            "file_count": len(file_ops),
            "persona": persona,
            "language": language,
            "pattern": pattern,
            "status": "completed",
            "operations": ops_with_status
        }

        sessions.insert(0, session_record)
        self._save_data(sessions)
        return session_record

    def get_sessions(self, sort_order="recent"):
        """Returns sessions array sorted by specified criteria."""
        sessions = self._load_data()
        # Backwards compatibility: ensure legacy records have session_name
        for sess in sessions:
            if "session_name" not in sess or not sess["session_name"]:
                sess["session_name"] = f"Session {sess.get('session_id', 'Unknown')}"

        if sort_order == "oldest":
            return sorted(sessions, key=lambda x: x.get("timestamp", ""))
        elif sort_order == "name":
            return sorted(sessions, key=lambda x: x.get("session_name", "").lower())
        elif sort_order == "file_count":
            return sorted(sessions, key=lambda x: x.get("file_count", 0), reverse=True)
        # Default: recent (newest first)
        return sorted(sessions, key=lambda x: x.get("timestamp", ""), reverse=True)

    def revert_session(self, session_id):
        """Reverts all un-reverted files in a session."""
        return self.revert_session_files(session_id, target_paths=None)

    def revert_session_files(self, session_id, target_paths=None):
        """
        Reverts specific files or all files in a session.
        :param session_id: ID of session to revert
        :param target_paths: List of original_path strings to revert. If None, reverts all remaining active files.
        """
        sessions = self._load_data()
        for sess in sessions:
            if sess["session_id"] == session_id:
                if sess["status"] == "reverted":
                    return False, f"Session '{sess.get('session_name', session_id)}' has already been fully reverted."

                reverted_count = 0
                failed_count = 0
                errors = []

                norm_target_set = set(os.path.normpath(tp).lower() for tp in target_paths) if target_paths is not None else None

                for op in sess["operations"]:
                    # Check if file is already reverted
                    if op.get("reverted", False):
                        continue

                    # If target_paths specified, check if this operation should be reverted
                    orig_p = op.get("original_path", "")
                    new_p = op.get("new_path", "")

                    if norm_target_set is not None:
                        norm_orig = os.path.normpath(orig_p).lower()
                        norm_new = os.path.normpath(new_p).lower()
                        if norm_orig not in norm_target_set and norm_new not in norm_target_set:
                            continue

                    curr_p = new_p

                    if not os.path.exists(curr_p):
                        failed_count += 1
                        errors.append(f"File not found: {os.path.basename(curr_p)}")
                        continue

                    try:
                        os.makedirs(os.path.dirname(orig_p), exist_ok=True)
                        dest_p = orig_p
                        if os.path.exists(dest_p) and os.path.normpath(dest_p).lower() != os.path.normpath(curr_p).lower():
                            d_dir, d_base = os.path.split(dest_p)
                            d_name, d_ext = os.path.splitext(d_base)
                            c_idx = 1
                            while os.path.exists(dest_p):
                                dest_p = os.path.join(d_dir, f"{d_name}_reverted_{c_idx}{d_ext}")
                                c_idx += 1
                        shutil.move(curr_p, dest_p)
                        op["reverted"] = True
                        op["reverted_path"] = dest_p
                        reverted_count += 1
                    except Exception as e:
                        failed_count += 1
                        errors.append(str(e))

                # Update session status based on remaining active operations
                total_ops = len(sess["operations"])
                reverted_ops = sum(1 for op in sess["operations"] if op.get("reverted", False))

                if reverted_ops >= total_ops:
                    sess["status"] = "reverted"
                    sess["reverted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                elif reverted_ops > 0:
                    sess["status"] = "partially_reverted"

                self._save_data(sessions)

                s_name = sess.get("session_name", session_id)
                if reverted_count == 0:
                    return False, f"No files were reverted for Session '{s_name}'."
                elif failed_count == 0:
                    return True, f"Successfully reverted {reverted_count} file(s) in Session '{s_name}'!"
                else:
                    return True, f"Reverted {reverted_count} file(s), {failed_count} failed.\n{'; '.join(errors[:2])}"

        return False, "Session ID not found."

    def clear_history(self):
        """Wipes all session history records."""
        self._save_data([])
        return True
