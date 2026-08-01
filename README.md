# ⚡ FlexBit AI (v2.5 Standalone)

**Hyper-lightweight, 100% Offline AI File & Image Manager powered by Moondream 2 Vision Language Model (GGUF)**

FlexBit AI is a standalone Windows desktop application designed for power users, photographers, content creators, and minimalists. It automatically renames local media with natural AI descriptions, cleans up unnecessary temporary files, and moves blurry or accidental snapshots into a quarantine folder—**all running locally on your CPU with zero external APIs, zero server subscriptions, and 100% privacy.**

---

## ✨ Features

- 🏷️ **Natural Vision Image Renaming**:
  - Automatically analyzes photo contents using Moondream 2 VLM GGUF.
  - 3 Naming Styles: *Natural Sentence*, *Title Case*, and *Date + Natural Phrase*.
- 🧹 **Junk File & Accidental Photo Quarantine**:
  - Scans for temporary files (`.tmp`, `.log`, `.dmp`, `.exe` installers).
  - Uses AI vision analysis to spot pitch-black or extremely blurry photos and moves them to `_Unnecessary_Files`.
- 📜 **1-Click Undo Vault & History Log**:
  - Every rename or quarantine operation is logged in `~/.flexbit_history.json`.
  - Instantly revert any file operation back to its original location with 1-click.
- 🛡️ **3 User Safety Tiers**:
  - **Newbie**: Non-destructive preview mode (simulates changes without touching disk).
  - **Balanced**: Standard renaming & quarantine with explicit confirmation modals.
  - **Power User**: Unrestricted high-speed batch execution.
- 🤖 **Embedded Moondream 2 Local VLM**:
  - Automatic download handler on first launch directly from Hugging Face (`moondream2-text-model-q4_k_m.gguf` & `moondream2-mmproj-f16.gguf`).
  - Pre-resizes images to 768px for sub-2-second inference on budget CPUs without requiring CUDA or high-end GPUs.

---

## 🎨 Theme & UI Aesthetics

- **Theme**: Dark Obsidian mode (`#0F172A`)
- **Accents**: Deep Glowing Purple (`#8B5CF6`) & Cyber Cyan (`#06B6D4`)
- **Framework**: CustomTkinter with JetBrains Mono / Segoe UI typography

---

## 🚀 1-Click ZIP Release Installation (For YouTube Viewers)

1. Download **`FlexBit_AI_v2.5_Windows.zip`** from the [Releases](https://github.com/deepxcoder) tab.
2. Extract the ZIP folder to your preferred directory.
3. Double-click **`FlexBit_AI.exe`** to launch!
4. *On first launch*: The app will automatically fetch the Moondream 2 GGUF models directly from Hugging Face via streaming progress modal if missing.

---

## 🛠️ Developer Setup & Build Instructions

If you want to run or build from source:

```bash
# 1. Clone repository
git clone https://github.com/deepxcoder/flexbit-ai.git
cd flexbit-ai

# 2. Install Python dependencies
pip install customtkinter pyinstaller requests pillow

# 3. Launch application
python main.py

# 4. Package standalone Windows executable ZIP release
python build.py
```

---

## 👨‍💻 About Developer

- **Developer**: Deep Dineshbhai Kotval
- **Role**: UI/UX Design Intern & CSBS Student
- **GitHub**: [github.com/deepxcoder](https://github.com/deepxcoder)
- **LinkedIn**: [linkedin.com/in/deep-kotval](https://linkedin.com/in/deep-kotval)
- **Tagline**: *"Made with ❤️ for power users & minimalists."*

---

## 📜 License

MIT License © 2026 Deep Dineshbhai Kotval.
