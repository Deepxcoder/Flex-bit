# ⚡ FlexBit AI (v2.5.0) — Official User Guide & Documentation

> **Hyper-lightweight, 100% Offline AI File & Image Manager powered by Moondream 2 Vision Language Model (GGUF)**

Welcome to **FlexBit AI**! FlexBit AI is an intelligent, 100% offline desktop workspace designed to help you organize, rename, search, and clean your files using local vision AI—with complete privacy and zero subscription fees.

---

## ⚡ Quick Start Checklist

1. **First Launch setup**: On your first launch, FlexBit AI automatically checks for the local vision model (`Moondream 2`). If missing, it downloads it directly into your local `./models/` folder.
2. **Select a Directory**: Use the interactive dropzone on the Home Dashboard to drag & drop any folder or browse your drive.
3. **Pick an Action**: Choose whether you want to **Rename Photos**, **Organize Files**, or **Clean Junk**.
4. **Review Previews**: Inspect the pre-execution preview table, check or uncheck specific files, and click **Start Batch Action**.
5. **Undo Anytime**: Made a mistake? Open the **Session Undo Vault** to revert any batch operation with 1 click.

---

## 🖼️ Module 1: Local Vision AI Photo Renaming

FlexBit AI uses an embedded **Moondream 2 Vision Language Model (VLM)** running locally on your CPU/GPU to look inside your images and generate human-like titles.

### 🎨 Renaming Personalities

* **Natural Sentence**: Full descriptive phrases (*"A golden retriever running through wheat field at sunset.jpg"*).
* **Minimal Descriptors**: Clean, keyword-focused titles (*"golden_retriever_wheat_field.png"*).
* **Creative Modes**: Adds stylistic flavor based on your mood:
  * 🎮 **Gamer Mode**: Modern, setup, and tech-centric naming.
  * 🍿 **Movie Mode**: Cinematic and atmospheric descriptions.
  * 🎵 **Music Mode**: Rhythmic and mood-based phrasing.
  * 🌌 **Poetic Mode**: Artistic and evocative titles.
  * 🖼️ **Normal Mode**: Standard clear descriptions.

### 🌐 Multi-Lingual Transliteration

Switch language scripts easily in the formatting bar:

* **English**: Native English descriptors.
* **Hinglish**: Hindi transliterated into Latin script (*"Glass ke saamne selfie reflection.jpg"*).
* **Gujlish**: Gujarati transliterated into Latin script.

### 📑 Pattern & Emoji Options

* **Emoji Inclusions**: Choose between **None**, **Leading Emoji Only** (`📸_sunset.jpg`), or **Contextual Emojis** (`🐕_golden_retriever_🌾_wheat.jpg`).
* **Patterns**: Combine dates, incremental counters, or clean text structures to fit your workflow.

---

## 🗂️ Module 2: Smart File Organization

Sort cluttered directories containing thousands of mixed files into structured, readable folders in seconds.

### 🎯 Organization Strategies

* **By Content**: Automatically categorizes files into clean subfolders (`Images`, `Documents`, `Code`, `Archives`, `Executables`, `Audio`, `Video`).
* **By Modifier**: Organizes files into temporal hierarchy (`2026/August/`) based on file creation or modification dates.
* **Deep Nesting**: Multi-tiered hierarchical folder structure for complex project assets.
* **By Extension**: Quick extension-based grouping (`.pdf`, `.zip`, `.py`, `.png`).

---

## 🧹 Module 3: Vision AI Junk Quarantine

Clean up digital clutter without risking your important personal files.

### 🧼 Cleaning Modes

* **Light Clean**: Safe administrative cleanup. Scans and moves `.tmp`, `.log`, `.dmp`, leftover `.msi`/`.exe` installers, and 0-byte ghost files.
* **Deep AI Clean**: Leverages Vision AI to inspect photo quality, isolating pitch-black accidental shots, severe motion blur, duplicate screenshots, and temporary memes.

> 🔒 **Safety Guarantee**: FlexBit AI never permanently deletes your files. All junk items are moved safely to a local `_Unnecessary_Files` quarantine folder where you can review or restore them anytime.

---

## 🔎 Natural Language Semantic AI Search

Find any file on your computer using natural language queries—no exact filename needed.

* **How it works**: Type descriptions like *"Sunset at the beach"*, *"Tax Invoices 2026"*, or *"Code Screenshot"* into the top search bar.
* **Suggestion Chips**: Click on dynamic 1-click search tags generated from your recent sessions.
* **Reveal in Explorer**: Click the **Locate** button on any search result card to instantly jump to the file location in Windows Explorer.

---

## 📜 Session History & Undo Vault

Every operation in FlexBit AI is logged persistently to your local session history (`~/.flexbit_history.json`).

* **Granular Revert**: Open the Undo Vault from the left sidebar to view past operations grouped by timestamp.
* **1-Click Restore**: Click **Revert Session** next to any run to restore every file back to its original name and location. You can also select individual files within a session to restore selectively.

---

## 👤 Profile & Avatar Studio

Personalize your workspace and track your productivity milestones.

* **Experience Tiers**: Switch between **Newbie**, **Balanced**, and **Power User** modes to adjust UI guidance and telemetry density.
* **Unlockable Avatars**: Gain access to exclusive retro and cyberpunk profile avatars as you complete more organization sessions.
* **Interactive Image Studio**: Upload custom photos and adjust them in real-time with drag-to-move, 90° rotation, scale controls, and filters (*Neon Glow*, *Cyberpunk HSL*, *Grayscale*, *Sepia*).

---

## 🛠️ Developer Setup & Running from Source

```bash
# 1. Clone repository
git clone https://github.com/Deepxcoder/FlexBit-AI.git
cd FlexBit-AI

# 2. Install dependencies
pip install pywebview requests pillow

# 3. Launch application
python main.py

# 4. Build Windows Standalone Package
python build.py
```

---

## ❓ Frequently Asked Questions (FAQ)

#### Q: Is my data uploaded to any cloud server?
**No.** FlexBit AI operates **100% offline**. All AI inference runs locally on your PC via `llama.cpp`/`Moondream 2`. Your files, images, and search history never leave your computer.

#### Q: How do I move FlexBit AI to a USB drive?
FlexBit AI is completely portable. Simply copy the `FlexBit_AI` folder (along with its local `./models/` directory) to any external drive. You can plug it into any Windows PC and double-click `FlexBit_AI.exe` to run instantly.

#### Q: What should I do if a batch rename made a mistake?
Don't worry! Click **Recent Actions / History** in the left sidebar, locate the session, and click **Revert Session**. All modified files will instantly return to their original names and locations.

#### Q: Can I use an external AI server instead of local CPU processing?
Yes! In the settings menu, you can connect FlexBit AI to a local **LM Studio** or **Ollama** server instance by providing your local endpoint (`http://localhost:1234/v1`).

---

## 💬 Community & Feedback

Have a suggestion, feature request, or bug report? We'd love to hear from you!

* 🐙 **GitHub Repository**: [github.com/Deepxcoder/FlexBit-AI](https://github.com/Deepxcoder/FlexBit-AI)
* 🛡️ **License**: Open Source under GNU General Public License v3 (GPL-3.0)

---

*Designed & Engineered with care by **Deep Dineshbhai Kotval** ([@Deepxcoder](https://github.com/Deepxcoder)).*
