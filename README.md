# ⚡ FlexBit AI (v2.5.0) — Official User Guide & Documentation

> **Hyper-lightweight, 100% Offline AI File & Image Manager powered by Moondream 2 Vision Language Model (GGUF)**

Welcome to **FlexBit AI**! FlexBit AI is an intelligent, 100% offline desktop workspace designed to help you organize, rename, search, and clean your files using local vision AI—with complete privacy and zero subscription fees.

---

## ⚡ Quick Start Checklist

1. **First Launch Setup**: On your first launch, FlexBit AI automatically checks for the local vision model (`Moondream 2`). If missing, it downloads it directly into your local `./models/` folder.
2. **Select a Directory**: Use the interactive dropzone on the Home Dashboard to drag & drop any folder or browse your drive.
3. **Pick an Action**: Choose whether you want to **Rename Photos**, **Organize Files**, or **Clean Junk**.
4. **Review Previews**: Inspect the pre-execution preview table, check or uncheck specific files, and click **Start Batch Action**.
5. **Undo Anytime**: Made a mistake? Open the **Session Undo Vault** to revert any batch operation with 1 click.

---

## 🖼️ Module 1: Local Vision AI Photo Renaming

FlexBit AI uses an embedded **Moondream 2 Vision Language Model (VLM)** running locally on your CPU/GPU to look inside your images and generate human-like titles.

### 🎨 Renaming Personalities
- **Natural Sentence**: Full descriptive phrases (*"A golden retriever running through wheat field at sunset.jpg"*).
- **Minimal Descriptors**: Clean, keyword-focused titles (*"golden_retriever_wheat_field.png"*).
- **Creative Naming Flavors**:
  - 🎮 **Gamer Mode**: Setup, tech, and gaming-centric titles.
  - 🍿 **Movie Mode**: Cinematic and atmospheric descriptions.
  - 🎵 **Music Mode**: Rhythmic and mood-based phrasing.
  - 🌌 **Poetic Mode**: Artistic and evocative titles.
  - 🖼️ **Normal Mode**: Standard, clear descriptions.

### 🌐 Multi-Lingual Transliteration
Switch language scripts effortlessly:
- **English**: Native English descriptors.
- **Hinglish**: Hindi transliterated into Latin script (*"Glass ke saamne selfie reflection.jpg"*).
- **Gujlish**: Gujarati transliterated into Latin script (*"Suraj samaye samudra kinaare photo.jpg"*).

### 📑 Formatting & Emojis
- **Emoji Inclusion**: **None**, **Leading Emoji Only** (`📸_sunset.jpg`), or **Contextual Emojis** (`🐕_golden_retriever_🌾_wheat.jpg`).
- **Structure Presets**: Combine dates, counters, or clean text structures to match your workflow.

---

## 🗂️ Module 2: Smart File Organization

Organize cluttered directories containing thousands of mixed files into structured, readable folders in seconds using a clean **2-Step Wizard**:

### 📍 Step 1: Organizational Strategy & Naming Scheme
Choose one of **4 Core Strategies**:
1. 📁 **By Content**: Automatically categorizes files into clean subfolders (`/Invoices/`, `/Photos/`, `/Code/`, `/Documents/`).
2. 📅 **Modifier Date**: Organizes files into temporal hierarchy (`/2026-08_Aug/`) based on modification timestamps.
3. 🌳 **Deep Nesting**: Multi-tiered hierarchical folder structure (`/Media/2026/PNG/`).
4. 🏷️ **Extensions**: Quick extension-based grouping (`/Images/`, `/Documents/`, `/Archives/`).

Choose a **Folder Naming Scheme**:
- 📁 **Standard Title** (`/Photos`, `/Documents`)
- 🏷️ **Clean Lowercase** (`/photos`, `/documents`)
- ✨ **Emoji Folders** (`/🖼️ Photos`, `/📄 Documents`)
- 📅 **Dated Prefix** (`/2026-08_Photos`)

### 📍 Step 2: Interactive Directory Explorer & Tree Preview
- **Live Folder Tree Preview**: See exactly how subfolders will be created before applying changes.
- **1-Click Execution & Step-Back**: Go back to tweak strategies or execute with full non-destructive safety.

---

## 🧹 Module 3: Vision AI Junk Quarantine

Clean up workspace clutter safely with a **2-Step Cleanup Protocol**:

### 🧼 Precision Cleanup Modes
- **Light Clean**: Administrative cleanup focusing on `.tmp`, `.log`, leftover installer packages, and 0-byte ghost files.
- **Deep AI Clean**: Leverages Vision AI to inspect image quality, isolating pitch-black accidental shots, severe blur, duplicate screenshots, and temporary memes.

> 🔒 **Safety Guarantee**: FlexBit AI never permanently deletes files. Unwanted items are safely moved to a local `.flexbit_quarantine` isolation vault where you can review or restore them anytime.

---

## 🔎 Natural Language Semantic AI Search

Find any file on your computer using natural queries—no exact filename needed.

- **Semantic Querying**: Type queries like *"Sunset at the beach"*, *"Tax Invoices 2026"*, or *"Code Screenshot"*.
- **Dynamic Search Chips**: Click on dynamic 1-click tags generated from recent workspace sessions.
- **Locate in Explorer**: Click **Show in Explorer** on any search result to jump straight to its folder.

---

## 📜 Session History & Undo Vault

Every operation in FlexBit AI is logged persistently to local history (`~/.flexbit_history.json`).

- **Granular Revert**: Open the Undo Vault to view past operations with real visual file cards (`.PNG`, `.PDF`, `.DOCX`).
- **1-Click Restore**: Click **Revert Session** to restore every file back to its original name and location, or select individual files to restore selectively.

---

## 👤 Profile & User Telemetry Analytics

Track your workspace efficiency and customize your profile:

- **Productivity Metrics**: Real-time counters for **Total Sessions Executed**, **App Times Started**, **Total Files Processed**, and **Manual Time Saved** (`~Hours`).
- **Overtime Workspace Activity Graph**: SVG chart plotting daily files processed per session over time.
- **50 Cute Avatar Options**: Personalize your user identity card with cute retro, robot, and cyberpunk avatars.

---

## 🔒 Privacy & Security Guarantee

- **100% Offline**: FlexBit AI operates completely offline. No telemetry, cloud APIs, or file uploads.
- **Local Model Processing**: All AI vision inference runs locally on your PC via `llama.cpp` and `Moondream 2`.
- **Portable Architecture**: Simply copy the `FlexBit_AI` folder to a USB drive to run portably on any Windows PC.

---

## 🛠️ Developer Setup & Running from Source

```bash
# 1. Clone repository
git clone https://github.com/Deepxcoder/Flex-bit.git
cd Flex-bit

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
**No.** FlexBit AI operates **100% offline**. Your files, photos, and search queries never leave your machine.

#### Q: How do I run FlexBit AI from a USB drive?
FlexBit AI is fully portable. Copy the release folder `FlexBit_AI_v2.5_Windows` to your USB drive and launch `FlexBit_AI.exe`.

#### Q: What should I do if a batch rename made a mistake?
Open **Session History / Undo Vault** from the sidebar and click **Revert Session** to instantly restore every file.

---

## 💬 Community & Support

- 💬 **Submit Feedback**: [FlexBit AI Feedback Form](https://forms.gle/flexbit-feedback)
- 🐙 **GitHub Repository**: [github.com/deepxcoder/Flex-bit](https://github.com/deepxcoder/Flex-bit)
- 🛡️ **License**: Open Source under GNU General Public License v3 (GPL-3.0)

*Designed & Engineered with care by **Deep Dineshbhai Kotval** ([@deepxcoder](https://github.com/deepxcoder)).*
