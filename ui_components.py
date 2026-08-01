"""
FlexBit AI - UI Components, Ultra-Sleek Luxury Dark Glassmorphic Styling & Modals
Implements Luxury Dark Glass (#080A10 / #101422), Soft Lavender Accents (#C084FC / #D8B4FE),
Pill Controls, Custom Modals, Sidebar, Setup Wizard, and Step Components.
"""

import os
import sys
import webbrowser
import threading
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk

from ai_engine import scan_server_models, check_server_health, check_models_exist

# Attempt pywinstyles for Windows 11 Acrylic blur
try:
    import pywinstyles
    HAS_PYWINSTYLES = True
except ImportError:
    HAS_PYWINSTYLES = False


def apply_glassmorphism(window):
    """Applies Windows 11 Acrylic glassmorphism effect with deep dark tint."""
    if HAS_PYWINSTYLES and sys.platform == "win32":
        try:
            pywinstyles.apply_style(window, style="acrylic")
        except Exception as e:
            print(f"[pywinstyles] Warning applying acrylic: {e}")


# Luxury Dark Glass Colors (Reference Design Palette)
COLOR_BG_DARK = "#080A10"       # Deep luxury dark canvas
COLOR_CARD = "#101422"          # Dark obsidian glass card fill
COLOR_CARD_BORDER = "#1E2640"   # Thin glowing border
COLOR_LAVENDER = "#C084FC"      # Soft glowing lavender accent
COLOR_LAVENDER_HOVER = "#A855F7"# Deep lavender hover
COLOR_LAVENDER_BTN = "#D8B4FE"  # Light violet primary action button fill
COLOR_LAVENDER_TEXT = "#090D16" # Dark text for primary action buttons

COLOR_CYAN = "#2DD4BF"          # Mint cyan status indicator
COLOR_ROSE = "#F43F5E"          # Warm rose accent
COLOR_TEXT_MAIN = "#F8FAFC"     # White text
COLOR_TEXT_MUTED = "#94A3B8"    # Dim slate subtext
COLOR_CODE_BG = "#030712"       # Code/preview pill capsule background
COLOR_AI_BADGE_BG = "#064E3B"   # AI Powered badge fill
COLOR_AI_BADGE_TEXT = "#34D399" # AI Powered badge text

COLOR_SUCCESS = "#10B981"       # Success green
COLOR_WARNING = "#F59E0B"       # Warning amber
COLOR_DANGER = "#EF4444"        # Danger red

FONT_FAMILY = "Segoe UI Variable Display" if sys.platform == "win32" else "Inter"
FONT_BODY = "Segoe UI Variable" if sys.platform == "win32" else "Inter"
FONT_MONO = "JetBrains Mono" if sys.platform == "win32" else "Consolas"


class CustomMessageModal(ctk.CTkToplevel):
    """Luxury dark glassmorphic CustomTkinter modal."""
    def __init__(self, master, title, message, icon_type="info"):
        super().__init__(master)
        self.title(title)
        self.geometry("440x240")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG_DARK)
        apply_glassmorphism(self)
        self.grab_set()

        icon_emoji = "ℹ️"
        border_clr = COLOR_LAVENDER
        if icon_type == "warning":
            icon_emoji = "⚠️"
            border_clr = COLOR_WARNING
        elif icon_type == "error":
            icon_emoji = "❌"
            border_clr = COLOR_DANGER
        elif icon_type == "success":
            icon_emoji = "✨"
            border_clr = COLOR_SUCCESS

        card = ctk.CTkFrame(
            self,
            fg_color=COLOR_CARD,
            border_color=border_clr,
            border_width=1.5,
            corner_radius=16
        )
        card.pack(fill="both", expand=True, padx=16, pady=16)

        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(fill="x", padx=16, pady=(16, 8))

        ctk.CTkLabel(header_frame, text=icon_emoji, font=(FONT_FAMILY, 24)).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(header_frame, text=title, font=(FONT_FAMILY, 16, "bold"), text_color=COLOR_TEXT_MAIN).pack(side="left")

        msg_lbl = ctk.CTkLabel(
            card,
            text=message,
            font=(FONT_BODY, 12),
            text_color=COLOR_TEXT_MUTED,
            wraplength=380,
            justify="left"
        )
        msg_lbl.pack(fill="both", expand=True, padx=16, pady=5)

        ok_btn = ctk.CTkButton(
            card,
            text="OK",
            width=110,
            height=38,
            fg_color=COLOR_LAVENDER_BTN,
            text_color=COLOR_LAVENDER_TEXT,
            hover_color=COLOR_LAVENDER,
            corner_radius=22,
            font=(FONT_BODY, 12, "bold"),
            command=self.destroy
        )
        ok_btn.pack(pady=(5, 16))


class CustomConfirmModal(ctk.CTkToplevel):
    """Luxury dark confirmation modal."""
    def __init__(self, master, title, message, on_confirm_callback):
        super().__init__(master)
        self.title(title)
        self.geometry("460x260")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG_DARK)
        apply_glassmorphism(self)
        self.grab_set()

        self.on_confirm_callback = on_confirm_callback

        card = ctk.CTkFrame(
            self,
            fg_color=COLOR_CARD,
            border_color=COLOR_LAVENDER,
            border_width=1.5,
            corner_radius=16
        )
        card.pack(fill="both", expand=True, padx=16, pady=16)

        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(fill="x", padx=16, pady=(16, 8))

        ctk.CTkLabel(header_frame, text="🛡️", font=(FONT_FAMILY, 24)).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(header_frame, text=title, font=(FONT_FAMILY, 16, "bold"), text_color=COLOR_TEXT_MAIN).pack(side="left")

        msg_lbl = ctk.CTkLabel(
            card,
            text=message,
            font=(FONT_BODY, 12),
            text_color=COLOR_TEXT_MUTED,
            wraplength=400,
            justify="left"
        )
        msg_lbl.pack(fill="both", expand=True, padx=16, pady=5)

        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(pady=(5, 16))

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            width=100,
            height=38,
            fg_color=COLOR_BG_DARK,
            hover_color=COLOR_CARD_BORDER,
            corner_radius=22,
            font=(FONT_BODY, 12),
            command=self.destroy
        )
        cancel_btn.pack(side="left", padx=8)

        confirm_btn = ctk.CTkButton(
            btn_frame,
            text="Confirm",
            width=110,
            height=38,
            fg_color=COLOR_LAVENDER_BTN,
            text_color=COLOR_LAVENDER_TEXT,
            hover_color=COLOR_LAVENDER,
            corner_radius=22,
            font=(FONT_BODY, 12, "bold"),
            command=self._on_confirm
        )
        confirm_btn.pack(side="left", padx=8)

    def _on_confirm(self):
        self.destroy()
        if self.on_confirm_callback:
            self.on_confirm_callback()


class SidebarComponent(ctk.CTkFrame):
    """Global Persistent Sidebar Component matching Reference Design Layout."""
    def __init__(self, master, on_nav_change, user_name="deep", current_tier="Free Plan", model_info="Moondream 2 VLM", **kwargs):
        super().__init__(master, fg_color=COLOR_CARD, corner_radius=0, width=240, **kwargs)
        self.on_nav_change = on_nav_change
        self.user_name = user_name
        self.current_tier = current_tier
        self.model_info = model_info
        self.nav_buttons = {}

        self._build_sidebar()

    def _build_sidebar(self):
        # Top Header Brand Identity
        logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        logo_frame.pack(fill="x", padx=18, pady=(24, 16))

        logo_title = ctk.CTkLabel(
            logo_frame,
            text="⚡ FlexBit AI",
            font=(FONT_FAMILY, 20, "bold"),
            text_color=COLOR_TEXT_MAIN
        )
        logo_title.pack(anchor="w")

        version_badge = ctk.CTkLabel(
            logo_frame,
            text="v2.5.0 • Personal Edition",
            font=(FONT_MONO, 10),
            text_color=COLOR_TEXT_MUTED
        )
        version_badge.pack(anchor="w", pady=(2, 0))

        # User Profile Badge (Dark Rounded Card)
        profile_card = ctk.CTkFrame(
            self,
            fg_color=COLOR_BG_DARK,
            border_color=COLOR_CARD_BORDER,
            border_width=1,
            corner_radius=14
        )
        profile_card.pack(fill="x", padx=16, pady=(0, 20))
        profile_card.grid_columnconfigure(1, weight=1)

        avatar_lbl = ctk.CTkLabel(profile_card, text="👤", font=(FONT_FAMILY, 18), width=32, height=32, fg_color=COLOR_CARD, corner_radius=16)
        avatar_lbl.grid(row=0, column=0, padx=10, pady=10)

        u_info = ctk.CTkFrame(profile_card, fg_color="transparent")
        u_info.grid(row=0, column=1, sticky="w")

        self.u_name_lbl = ctk.CTkLabel(u_info, text=self.user_name, font=(FONT_BODY, 12, "bold"), text_color=COLOR_TEXT_MAIN)
        self.u_name_lbl.pack(anchor="w")

        self.u_tier_lbl = ctk.CTkLabel(u_info, text=self.current_tier, font=(FONT_BODY, 10), text_color=COLOR_CYAN)
        self.u_tier_lbl.pack(anchor="w")

        # Global Navigation Links
        nav_items = [
            ("home", "📂  My Library"),
            ("history", "📜  Recent Actions"),
            ("settings", "⚙️  Settings")
        ]

        for key, label in nav_items:
            btn = ctk.CTkButton(
                self,
                text=label,
                anchor="w",
                height=42,
                corner_radius=10,
                font=(FONT_BODY, 12),
                fg_color=COLOR_CARD_BORDER if key == "home" else "transparent",
                text_color=COLOR_TEXT_MAIN if key == "home" else COLOR_TEXT_MUTED,
                hover_color=COLOR_BG_DARK,
                command=lambda k=key: self.select_nav(k)
            )
            btn.pack(fill="x", padx=12, pady=3)
            self.nav_buttons[key] = btn

    def update_profile(self, user_name, new_tier, model_info):
        self.user_name = user_name
        self.current_tier = new_tier
        self.model_info = model_info

        self.u_name_lbl.configure(text=self.user_name)
        self.u_tier_lbl.configure(text=self.current_tier)

    def select_nav(self, key):
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(fg_color=COLOR_CARD_BORDER, text_color=COLOR_TEXT_MAIN, hover_color=COLOR_CARD_BORDER)
            else:
                btn.configure(fg_color="transparent", text_color=COLOR_TEXT_MUTED, hover_color=COLOR_BG_DARK)
        self.on_nav_change(key)


class FirstTimeOnboardingWizard(ctk.CTkToplevel):
    """First-Time Setup Wizard Modal with Luxury Dark Glassmorphism."""
    def __init__(self, master, current_config, on_complete_callback):
        super().__init__(master)
        self.title("FlexBit AI — Welcome & Setup Wizard")
        self.geometry("640x580")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG_DARK)
        apply_glassmorphism(self)
        self.grab_set()

        self.config_data = dict(current_config)
        self.on_complete_callback = on_complete_callback
        self.scanned_models = []
        self._build_ui()

    def _build_ui(self):
        container = ctk.CTkFrame(
            self,
            fg_color=COLOR_CARD,
            border_color=COLOR_LAVENDER,
            border_width=1.5,
            corner_radius=16
        )
        container.pack(fill="both", expand=True, padx=20, pady=20)

        title_lbl = ctk.CTkLabel(
            container,
            text="⚡ Welcome to FlexBit AI",
            font=(FONT_FAMILY, 20, "bold"),
            text_color=COLOR_TEXT_MAIN
        )
        title_lbl.pack(pady=(15, 2))

        sub_lbl = ctk.CTkLabel(
            container,
            text="Set up your profile and configure your local vision language model.",
            font=(FONT_BODY, 12),
            text_color=COLOR_TEXT_MUTED
        )
        sub_lbl.pack(pady=(0, 15))

        form_scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        form_scroll.pack(fill="both", expand=True, padx=15, pady=5)

        sec1_card = ctk.CTkFrame(form_scroll, fg_color=COLOR_BG_DARK, corner_radius=16)
        sec1_card.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            sec1_card,
            text="1️⃣ User Profile & Experience Role",
            font=(FONT_FAMILY, 14, "bold"),
            text_color=COLOR_TEXT_MAIN
        ).pack(anchor="w", padx=15, pady=(12, 8))

        n_frame = ctk.CTkFrame(sec1_card, fg_color="transparent")
        n_frame.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(n_frame, text="What should I call you?", font=(FONT_BODY, 12, "bold")).pack(side="left", padx=(0, 10))

        self.name_entry = ctk.CTkEntry(
            n_frame,
            width=260,
            fg_color=COLOR_CARD,
            border_color=COLOR_CARD_BORDER,
            corner_radius=12,
            font=(FONT_BODY, 12)
        )
        self.name_entry.insert(0, self.config_data.get("user_name", "deep"))
        self.name_entry.pack(side="left")

        ctk.CTkLabel(sec1_card, text="Select your experience level:", font=(FONT_BODY, 12, "bold")).pack(anchor="w", padx=15, pady=(5, 5))

        self.tier_var = ctk.StringVar(value=self.config_data.get("user_tier", "Free Plan"))

        tiers = [
            ("Newbie Mode", "Newbie", "Non-destructive preview mode. Generates AI titles without modifying files."),
            ("Normal / Medium", "Free Plan", "Standard renaming & quarantine with explicit confirmation modals."),
            ("Power User", "Power User", "Unrestricted high-speed batch processing without confirmation prompts.")
        ]

        for t_title, t_key, t_desc in tiers:
            r = ctk.CTkRadioButton(
                sec1_card,
                text=f"{t_title} — {t_desc}",
                value=t_key,
                variable=self.tier_var,
                fg_color=COLOR_LAVENDER,
                hover_color=COLOR_LAVENDER_HOVER,
                font=(FONT_BODY, 12)
            )
            r.pack(anchor="w", padx=20, pady=4)

        sec2_card = ctk.CTkFrame(form_scroll, fg_color=COLOR_BG_DARK, corner_radius=16)
        sec2_card.pack(fill="x", pady=10)

        ctk.CTkLabel(
            sec2_card,
            text="2️⃣ Vision Model Provider",
            font=(FONT_FAMILY, 14, "bold"),
            text_color=COLOR_TEXT_MAIN
        ).pack(anchor="w", padx=15, pady=(12, 8))

        self.provider_var = ctk.StringVar(value=self.config_data.get("model_provider", "embedded"))

        providers = [
            ("Embedded Moondream 2 GGUF (Offline)", "embedded", "Built-in 100% offline VLM in ./models/. Auto-downloads GGUF from Hugging Face if missing."),
            ("Local GGUF Model File (.gguf)", "local_gguf", "Select your own existing local .gguf model file on disk."),
            ("LM Studio Server", "lm_studio", "Connect to local LM Studio server API (default: http://localhost:1234/v1)."),
            ("Ollama Server", "ollama", "Connect to local Ollama server API (default: http://localhost:11434).")
        ]

        for p_title, p_key, p_desc in providers:
            r = ctk.CTkRadioButton(
                sec2_card,
                text=f"{p_title}\n   └ {p_desc}",
                value=p_key,
                variable=self.provider_var,
                fg_color=COLOR_CYAN,
                hover_color="#0891B2",
                font=(FONT_BODY, 12),
                command=self._on_provider_change
            )
            r.pack(anchor="w", padx=20, pady=6)

        self.sec3_card = ctk.CTkFrame(form_scroll, fg_color=COLOR_BG_DARK, corner_radius=16)
        self.sec3_card.pack(fill="x", pady=10)

        self._build_provider_config_widgets()

        finish_btn = ctk.CTkButton(
            container,
            text="🚀 Save Profile & Launch FlexBit AI",
            fg_color=COLOR_LAVENDER_BTN,
            text_color=COLOR_LAVENDER_TEXT,
            hover_color=COLOR_LAVENDER,
            corner_radius=22,
            height=44,
            font=(FONT_BODY, 14, "bold"),
            command=self._finish_wizard
        )
        finish_btn.pack(fill="x", padx=20, pady=(10, 15))

    def _on_provider_change(self):
        self._build_provider_config_widgets()

    def _build_provider_config_widgets(self):
        for widget in self.sec3_card.winfo_children():
            widget.destroy()

        prov = self.provider_var.get()

        if prov == "embedded":
            ctk.CTkLabel(self.sec3_card, text="3️⃣ Embedded Moondream 2 Setup (Portable ./models/)", font=(FONT_FAMILY, 14, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w", padx=15, pady=(12, 6))

            if check_models_exist():
                status_txt = "✅ Moondream 2 GGUF files found in local ./models/ folder."
                status_clr = COLOR_SUCCESS
            else:
                status_txt = "⚠️ Moondream 2 GGUF files missing. Will download to ./models/ (~1.8 GB)."
                status_clr = COLOR_WARNING

            ctk.CTkLabel(self.sec3_card, text=status_txt, font=(FONT_BODY, 12), text_color=status_clr).pack(anchor="w", padx=15, pady=(0, 12))

        elif prov == "local_gguf":
            ctk.CTkLabel(self.sec3_card, text="3️⃣ Local .GGUF File Selection", font=(FONT_FAMILY, 14, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w", padx=15, pady=(12, 6))

            f_frame = ctk.CTkFrame(self.sec3_card, fg_color="transparent")
            f_frame.pack(fill="x", padx=15, pady=(0, 12))

            self.local_path_entry = ctk.CTkEntry(f_frame, placeholder_text="Select path to .gguf file...", font=(FONT_BODY, 11), fg_color=COLOR_CARD, border_color=COLOR_CARD_BORDER, corner_radius=12)
            self.local_path_entry.insert(0, self.config_data.get("local_gguf_path", ""))
            self.local_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

            browse_btn = ctk.CTkButton(f_frame, text="Browse .gguf", width=100, corner_radius=22, fg_color=COLOR_LAVENDER_BTN, text_color=COLOR_LAVENDER_TEXT, hover_color=COLOR_LAVENDER, command=self._browse_gguf)
            browse_btn.pack(side="right")

        elif prov in ["lm_studio", "ollama"]:
            ctk.CTkLabel(self.sec3_card, text=f"3️⃣ {prov.replace('_', ' ').title()} Server Configuration", font=(FONT_FAMILY, 14, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w", padx=15, pady=(12, 6))

            url_frame = ctk.CTkFrame(self.sec3_card, fg_color="transparent")
            url_frame.pack(fill="x", padx=15, pady=(0, 8))

            ctk.CTkLabel(url_frame, text="Server URL:", font=(FONT_BODY, 12, "bold")).pack(side="left", padx=(0, 10))

            default_url = "http://localhost:1234/v1" if prov == "lm_studio" else "http://localhost:11434"
            self.server_url_entry = ctk.CTkEntry(url_frame, font=(FONT_BODY, 11), fg_color=COLOR_CARD, border_color=COLOR_CARD_BORDER, corner_radius=12)
            self.server_url_entry.insert(0, self.config_data.get("server_url") or default_url)
            self.server_url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

            scan_btn = ctk.CTkButton(
                url_frame,
                text="🔍 Scan Models",
                width=110,
                corner_radius=22,
                fg_color=COLOR_CYAN,
                hover_color="#0891B2",
                command=self._scan_models_action
            )
            scan_btn.pack(side="right")

            m_frame = ctk.CTkFrame(self.sec3_card, fg_color="transparent")
            m_frame.pack(fill="x", padx=15, pady=(0, 8))

            ctk.CTkLabel(m_frame, text="Select Model:", font=(FONT_BODY, 12, "bold")).pack(side="left", padx=(0, 10))

            self.model_dropdown_var = ctk.StringVar(value=self.config_data.get("selected_model") or "Auto / Default")
            self.model_dropdown = ctk.CTkOptionMenu(
                m_frame,
                values=["Auto / Default"],
                variable=self.model_dropdown_var,
                fg_color=COLOR_CARD,
                button_color=COLOR_LAVENDER,
                button_hover_color=COLOR_LAVENDER_HOVER,
                corner_radius=12
            )
            self.model_dropdown.pack(side="left", fill="x", expand=True)

            self.health_badge = ctk.CTkLabel(
                self.sec3_card,
                text="🟡 Checking server connection...",
                font=(FONT_BODY, 12, "bold"),
                text_color=COLOR_WARNING
            )
            self.health_badge.pack(anchor="w", padx=15, pady=(4, 12))

            self._check_health_async()

    def _browse_gguf(self):
        f = filedialog.askopenfilename(title="Select Vision GGUF Model File", filetypes=[("GGUF Model Files", "*.gguf")])
        if f:
            self.local_path_entry.delete(0, "end")
            self.local_path_entry.insert(0, f)

    def _scan_models_action(self):
        prov = self.provider_var.get()
        url = self.server_url_entry.get().strip()

        models = scan_server_models(prov, url)
        if models:
            self.scanned_models = models
            self.model_dropdown.configure(values=models)
            self.model_dropdown_var.set(models[0])
            CustomMessageModal(self, "Model Scan", f"Found {len(models)} vision model(s) on server!\nSelected: {models[0]}", "success")
        else:
            CustomMessageModal(self, "Model Scan Warning", f"Could not find loaded models on {url}.\nEnsure LM Studio or Ollama is running and has a vision model loaded.", "warning")

        self._check_health_async()

    def _check_health_async(self):
        prov = self.provider_var.get()
        url = self.server_url_entry.get().strip() if hasattr(self, 'server_url_entry') else ""

        def _worker():
            is_ok, msg = check_server_health(prov, url)
            def _update():
                if hasattr(self, 'health_badge') and self.health_badge.winfo_exists():
                    if is_ok:
                        self.health_badge.configure(text=f"🟢 {msg}", text_color=COLOR_SUCCESS)
                    else:
                        self.health_badge.configure(text=f"🔴 {msg}", text_color=COLOR_DANGER)
            self.after(0, _update)

        t = threading.Thread(target=_worker, daemon=True)
        t.start()

    def _finish_wizard(self):
        u_name = self.name_entry.get().strip() or "deep"
        u_tier = self.tier_var.get()
        m_prov = self.provider_var.get()

        out_config = {
            "user_name": u_name,
            "user_tier": u_tier,
            "model_provider": m_prov,
            "first_run_completed": True
        }

        if m_prov == "local_gguf" and hasattr(self, 'local_path_entry'):
            out_config["local_gguf_path"] = self.local_path_entry.get().strip()

        if m_prov in ["lm_studio", "ollama"] and hasattr(self, 'server_url_entry'):
            out_config["server_url"] = self.server_url_entry.get().strip()
            out_config["selected_model"] = self.model_dropdown_var.get()

        self.destroy()
        self.on_complete_callback(out_config)


class AboutDeveloperModal(ctk.CTkToplevel):
    """Modal presenting Deep Dineshbhai Kotval developer bio."""
    def __init__(self, master):
        super().__init__(master)
        self.title("About Developer - FlexBit AI")
        self.geometry("480x420")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG_DARK)
        apply_glassmorphism(self)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        card = ctk.CTkFrame(
            self,
            fg_color=COLOR_CARD,
            border_color=COLOR_LAVENDER,
            border_width=1.5,
            corner_radius=16
        )
        card.pack(fill="both", expand=True, padx=20, pady=20)

        avatar_lbl = ctk.CTkLabel(card, text="👨‍💻", font=(FONT_FAMILY, 48))
        avatar_lbl.pack(pady=(20, 5))

        name_lbl = ctk.CTkLabel(card, text="Deep Dineshbhai Kotval", font=(FONT_FAMILY, 20, "bold"), text_color=COLOR_TEXT_MAIN)
        name_lbl.pack()

        role_lbl = ctk.CTkLabel(card, text="UI/UX Design Intern & CSBS Student", font=(FONT_BODY, 13, "bold"), text_color=COLOR_LAVENDER)
        role_lbl.pack(pady=(2, 10))

        tagline = ctk.CTkLabel(card, text='"Made with ❤️ for power users & minimalists."', font=(FONT_BODY, 12, "italic"), text_color=COLOR_TEXT_MUTED)
        tagline.pack(pady=(0, 15))

        links_frame = ctk.CTkFrame(card, fg_color="transparent")
        links_frame.pack(pady=10)

        gh_btn = ctk.CTkButton(links_frame, text="🌐 GitHub", fg_color=COLOR_BG_DARK, border_color=COLOR_CARD_BORDER, border_width=1, corner_radius=22, hover_color=COLOR_LAVENDER_HOVER, command=lambda: webbrowser.open("https://github.com/deepxcoder"))
        gh_btn.grid(row=0, column=0, padx=8)

        li_btn = ctk.CTkButton(links_frame, text="💼 LinkedIn", fg_color=COLOR_BG_DARK, border_color=COLOR_CARD_BORDER, border_width=1, corner_radius=22, hover_color=COLOR_CYAN, command=lambda: webbrowser.open("https://linkedin.com/in/deep-kotval"))
        li_btn.grid(row=0, column=1, padx=8)

        close_btn = ctk.CTkButton(card, text="Close", width=120, height=38, corner_radius=22, fg_color=COLOR_CARD_BORDER, hover_color=COLOR_DANGER, command=self.destroy)
        close_btn.pack(pady=(20, 10))


class ModelDownloadDialog(ctk.CTkToplevel):
    """Progress splash dialog downloading Moondream 2 GGUF binaries."""
    def __init__(self, master):
        super().__init__(master)
        self.title("FlexBit AI - Downloading Moondream 2 VLM Models")
        self.geometry("540x320")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG_DARK)
        apply_glassmorphism(self)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        frame = ctk.CTkFrame(self, fg_color=COLOR_CARD, border_color=COLOR_CYAN, border_width=1.5, corner_radius=16)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        icon_lbl = ctk.CTkLabel(frame, text="🤖", font=(FONT_FAMILY, 40))
        icon_lbl.pack(pady=(15, 5))

        title_lbl = ctk.CTkLabel(frame, text="Downloading Local Vision Language Model", font=(FONT_FAMILY, 18, "bold"), text_color=COLOR_TEXT_MAIN)
        title_lbl.pack()

        subtitle = ctk.CTkLabel(frame, text="Downloading Moondream 2 GGUF model directly to portable ./models/ folder...\nThis only happens once for 100% offline local inference.", font=(FONT_BODY, 12), text_color=COLOR_TEXT_MUTED, justify="center")
        subtitle.pack(pady=(5, 15))

        self.file_lbl = ctk.CTkLabel(frame, text="Initializing stream...", font=(FONT_BODY, 12, "bold"), text_color=COLOR_CYAN)
        self.file_lbl.pack(anchor="w", padx=30, pady=(0, 2))

        self.progress_bar = ctk.CTkProgressBar(frame, height=12, corner_radius=6, fg_color=COLOR_BG_DARK, progress_color=COLOR_LAVENDER)
        self.progress_bar.pack(fill="x", padx=30, pady=5)
        self.progress_bar.set(0.0)

        self.status_lbl = ctk.CTkLabel(frame, text="0 MB / 0 MB (0.0 MB/s)", font=(FONT_BODY, 11), text_color=COLOR_TEXT_MUTED)
        self.status_lbl.pack(anchor="w", padx=30, pady=(2, 10))

    def update_progress(self, downloaded, total, speed_mbps, filename):
        if total > 0:
            frac = downloaded / total
            self.progress_bar.set(frac)
            dl_mb = downloaded / (1024 * 1024)
            tot_mb = total / (1024 * 1024)
            self.file_lbl.configure(text=f"Downloading: {filename}")
            self.status_lbl.configure(text=f"{dl_mb:.1f} MB / {tot_mb:.1f} MB ({speed_mbps:.1f} MB/s) - {int(frac*100)}%")
        else:
            self.file_lbl.configure(text=f"Downloading: {filename}")
            self.status_lbl.configure(text="Connecting to Hugging Face...")
