"""
FlexBit AI - Multi-Provider Vision Engine & Model Manager
Supports:
1. Embedded Moondream 2 GGUF (llama-cpp-python) in ./models/
2. Custom Local GGUF file (llama-cpp-python)
3. LM Studio Server (OpenAI Compatible API)
4. Ollama Server (Ollama API)
5. Persona Naming (Gamer, Movie, Music, Poetic, Normal)
6. Language Script Transliteration (English, Hinglish, Gujlish)
7. Pattern Formatting (Emoji Only, Pattern Only, Both, Clean Sentence)
"""

import os
import re
import sys
import time
import base64
import requests
import threading
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageStat, ImageFilter

TEXT_MODEL_URL = "https://huggingface.co/moondream/moondream2-gguf/resolve/main/moondream2-text-model-f16.gguf"
MMPROJ_URL = "https://huggingface.co/moondream/moondream2-gguf/resolve/main/moondream2-mmproj-f16.gguf"

TEXT_MODEL_FILENAME = "moondream2-text-model-f16.gguf"
MMPROJ_FILENAME = "moondream2-mmproj-f16.gguf"


def get_models_dir():
    """Returns absolute path to the local relative models directory (100% portable)."""
    if getattr(sys, 'frozen', False):
        base_dir = Path(sys.executable).parent
    else:
        base_dir = Path(__file__).resolve().parent
    models_dir = base_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    return str(models_dir)


def check_models_exist():
    """Checks if default Moondream 2 GGUF files exist in models/."""
    m_dir = get_models_dir()
    text_path_f16 = os.path.join(m_dir, TEXT_MODEL_FILENAME)
    text_path_q4 = os.path.join(m_dir, "moondream2-text-model-q4_k_m.gguf")
    mmproj_path = os.path.join(m_dir, MMPROJ_FILENAME)

    text_exists = os.path.exists(text_path_f16) or os.path.exists(text_path_q4)
    return text_exists and os.path.exists(mmproj_path)


def download_file(url, target_path, progress_callback=None):
    """Downloads a file with streaming progress reports."""
    filename = os.path.basename(target_path)
    temp_path = target_path + ".tmp"

    response = requests.get(url, stream=True, timeout=30)
    response.raise_for_status()

    total_bytes = int(response.headers.get('content-length', 0))
    downloaded_bytes = 0
    start_time = time.time()

    with open(temp_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)
                downloaded_bytes += len(chunk)
                elapsed = time.time() - start_time
                speed_mbps = (downloaded_bytes / (1024 * 1024)) / elapsed if elapsed > 0 else 0

                if progress_callback:
                    progress_callback(downloaded_bytes, total_bytes, speed_mbps, filename)

    if os.path.exists(target_path):
        os.remove(target_path)
    os.rename(temp_path, target_path)


def download_moondream_models(progress_callback=None, completion_callback=None):
    """Asynchronously downloads required Moondream 2 GGUF files."""
    def _worker():
        m_dir = get_models_dir()
        text_path = os.path.join(m_dir, TEXT_MODEL_FILENAME)
        mmproj_path = os.path.join(m_dir, MMPROJ_FILENAME)

        try:
            if not os.path.exists(text_path):
                download_file(TEXT_MODEL_URL, text_path, progress_callback)
            if not os.path.exists(mmproj_path):
                download_file(MMPROJ_URL, mmproj_path, progress_callback)
            if completion_callback:
                completion_callback(True, "Models downloaded successfully!")
        except Exception as e:
            if completion_callback:
                completion_callback(False, str(e))

    t = threading.Thread(target=_worker, daemon=True)
    t.start()


def scan_server_models(provider, server_url):
    """Scans LM Studio or Ollama server endpoints for available loaded vision models."""
    base_url = server_url.rstrip("/")
    if base_url.endswith("/v1"):
        base_url = base_url[:-3]
    models = []

    try:
        if provider == "lm_studio":
            url = f"{base_url}/v1/models"
            resp = requests.get(url, timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("data", []):
                    models.append(item.get("id", "unknown-model"))

        elif provider == "ollama":
            url = f"{base_url}/api/tags"
            resp = requests.get(url, timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("models", []):
                    models.append(item.get("name", "unknown-model"))
    except Exception as e:
        print(f"[scan_server_models] Exception scanning {provider} at {server_url}: {e}")

    return models


def check_server_health(provider, server_url):
    """Pings the server URL to check connection health."""
    base_url = server_url.rstrip("/")
    if base_url.endswith("/v1"):
        base_url = base_url[:-3]
    try:
        if provider in ["lm_studio", "openai"]:
            url = f"{base_url}/v1/models"
            resp = requests.get(url, timeout=3)
            if resp.status_code == 200:
                return True, f"Connected to {provider.upper()} Server ({server_url})"
        elif provider == "ollama":
            url = f"{base_url}/api/tags"
            resp = requests.get(url, timeout=3)
            if resp.status_code == 200:
                return True, f"Connected to Ollama Server ({server_url})"
    except Exception as e:
        return False, f"Server offline at {server_url}: {str(e)}"

    return False, f"Could not connect to {server_url}"


class VisionModelEngine:
    def __init__(self, provider="embedded", server_url="http://localhost:1234/v1",
                 selected_model="", local_gguf_path="", n_threads=4, max_dim=768):
        self.provider = provider
        self.server_url = server_url.rstrip("/")
        self.selected_model = selected_model
        self.local_gguf_path = local_gguf_path
        self.n_threads = n_threads
        self.max_dim = max_dim

        self.llm = None
        self.chat_handler = None
        self.is_native_loaded = False

        self._init_backend()

    def update_config(self, provider, server_url="", selected_model="", local_gguf_path="", n_threads=4):
        self.provider = provider
        self.server_url = server_url.rstrip("/")
        self.selected_model = selected_model
        self.local_gguf_path = local_gguf_path
        self.n_threads = n_threads
        self._init_backend()

    def _init_backend(self):
        self.is_native_loaded = False
        if self.provider in ["embedded", "local_gguf"]:
            try:
                import llama_cpp
                from llama_cpp.llama_chat_format import Moondream2ChatHandler

                if self.provider == "embedded" and check_models_exist():
                    m_dir = get_models_dir()
                    text_path_f16 = os.path.join(m_dir, TEXT_MODEL_FILENAME)
                    text_path_q4 = os.path.join(m_dir, "moondream2-text-model-q4_k_m.gguf")
                    text_path = text_path_f16 if os.path.exists(text_path_f16) else text_path_q4
                    mmproj_path = os.path.join(m_dir, MMPROJ_FILENAME)

                    self.chat_handler = Moondream2ChatHandler(clip_model_path=mmproj_path)
                    self.llm = llama_cpp.Llama(
                        model_path=text_path,
                        chat_handler=self.chat_handler,
                        n_ctx=2048,
                        n_threads=self.n_threads,
                        n_gpu_layers=0,
                        verbose=False
                    )
                    self.is_native_loaded = True
                    print("[VisionModelEngine] Embedded Moondream 2 loaded.")

                elif self.provider == "local_gguf" and os.path.exists(self.local_gguf_path):
                    self.llm = llama_cpp.Llama(
                        model_path=self.local_gguf_path,
                        n_ctx=2048,
                        n_threads=self.n_threads,
                        n_gpu_layers=0,
                        verbose=False
                    )
                    self.is_native_loaded = True
                    print(f"[VisionModelEngine] Custom GGUF loaded: {self.local_gguf_path}")
            except Exception as e:
                print(f"[VisionModelEngine] Llama-cpp init warning: {e}")

    def preprocess_image(self, image_path, output_temp_path=None):
        with Image.open(image_path) as img_in:
            img = img_in.convert("RGB")
        width, height = img.size

        if width > self.max_dim or height > self.max_dim:
            if width > height:
                new_w = self.max_dim
                new_h = int(height * (self.max_dim / width))
            else:
                new_h = self.max_dim
                new_w = int(width * (self.max_dim / height))
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        if output_temp_path:
            img.save(output_temp_path, "JPEG", quality=85)

        return img

    def describe_image(self, image_path, language="English"):
        """Runs Vision Model inference depending on configured provider."""
        if not os.path.exists(image_path):
            return "Unknown Image"

        temp_img_path = image_path + ".thumb.jpg"
        try:
            try:
                self.preprocess_image(image_path, temp_img_path)
            except Exception as pe:
                print(f"[VisionModelEngine] Non-image or unreadable image file: {pe}")
                return self._heuristic_vision_analyzer(image_path, language)

            prompt = "Describe the main subject of this image in a short, concise 3 to 6 word title suitable for a file name. Do not include period or punctuation."
            if "Hinglish" in language:
                prompt += " Respond in simple transliterated Hinglish."
            elif "Gujlish" in language:
                prompt += " Respond in simple transliterated Gujlish."

            if self.provider == "lm_studio":
                res = self._query_lm_studio(temp_img_path, prompt)
                if res: return res

            elif self.provider == "ollama":
                res = self._query_ollama(temp_img_path, prompt)
                if res: return res

            elif self.is_native_loaded and self.llm:
                try:
                    with open(temp_img_path, "rb") as f:
                        b64_str = base64.b64encode(f.read()).decode("utf-8")
                    data_uri = f"data:image/jpeg;base64,{b64_str}"

                    response = self.llm.create_chat_completion(
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt},
                                    {"type": "image_url", "image_url": {"url": data_uri}}
                                ]
                            }
                        ],
                        max_tokens=30,
                        temperature=0.2
                    )
                    text = response['choices'][0]['message']['content'].strip()
                    text = re.sub(r'[^\w\s-]', '', text)
                    if text: return text
                except Exception as ex:
                    print(f"[VisionModelEngine] Llama completion exception: {ex}")

            return self._heuristic_vision_analyzer(image_path, language)

        finally:
            if os.path.exists(temp_img_path):
                try: os.remove(temp_img_path)
                except Exception: pass

    def _query_lm_studio(self, image_path, prompt):
        try:
            with open(image_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")

            url = f"{self.server_url}/chat/completions" if self.server_url.endswith("/v1") else f"{self.server_url}/v1/chat/completions"

            payload = {
                "model": self.selected_model or "default",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                        ]
                    }
                ],
                "max_tokens": 30,
                "temperature": 0.2
            }
            resp = requests.post(url, json=payload, timeout=6)
            if resp.status_code == 200:
                text = resp.json()["choices"][0]["message"]["content"].strip()
                return re.sub(r'[^\w\s-]', '', text)
        except Exception as e:
            print(f"[LM Studio Query Exception]: {e}")
        return None

    def _query_ollama(self, image_path, prompt):
        try:
            with open(image_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")

            url = f"{self.server_url}/api/generate"
            payload = {
                "model": self.selected_model or "llava",
                "prompt": prompt,
                "images": [b64],
                "stream": False
            }
            resp = requests.post(url, json=payload, timeout=6)
            if resp.status_code == 200:
                text = resp.json().get("response", "").strip()
                return re.sub(r'[^\w\s-]', '', text)
        except Exception as e:
            print(f"[Ollama Query Exception]: {e}")
        return None

    def _heuristic_vision_analyzer(self, image_path, language="English"):
        try:
            with Image.open(image_path) as img_in:
                img = img_in.convert("RGB")
            w, h = img.size
            aspect = w / h if h > 0 else 1.0

            stat = ImageStat.Stat(img)
            r, g, b = stat.mean
            luminance = 0.299 * r + 0.587 * g + 0.114 * b

            if aspect > 1.3: layout = "Landscape View" if "English" in language else ("Landscape Photo" if "Hinglish" in language else "Aadi Photo")
            elif aspect < 0.75: layout = "Portrait View" if "English" in language else ("Portrait Photo" if "Hinglish" in language else "Ubhi Photo")
            else: layout = "Square Snapshot"

            if r > g + 20 and r > b + 20: color_tone = "Warm Sunset"
            elif b > r + 20 and b > g + 20: color_tone = "Cyber Blue"
            elif g > r + 15 and g > b + 15: color_tone = "Nature Green"
            elif luminance > 200: color_tone = "Bright Light"
            elif luminance < 50: color_tone = "Dark Mood"
            else: color_tone = "Balanced Color"

            return f"{color_tone} {layout}"
        except Exception:
            filename = os.path.splitext(os.path.basename(image_path))[0]
            return filename.replace("_", " ").replace("-", " ")

    def generate_filename(self, image_path, persona="Normal", language="English", pattern="Clean Natural Sentence", counter_idx=1):
        """
        Generates formatted filename based on Persona, Language, and Pattern:
        - Personas: Gamer (🎮), Movie (🍿), Music (🎵), Poetic (🌌), Normal (🖼️)
        - Languages: English, Hinglish, Gujlish
        - Patterns: Vibrant, Timestamps, Org/Counter, Minimalist / Clean, Emoji Only, Pattern Only, Both
        """
        ext = os.path.splitext(image_path)[1].lower() or ".png"
        description = self.describe_image(image_path, language)

        description = re.sub(r'[\/:*?"<>|]', '', description).strip() or "Captured Moment"

        # Apply Persona prefix/style
        emoji_prefix = ""
        p_str = str(persona).lower()
        if "gamer" in p_str:
            emoji_prefix = "🎮"
            description = f"Cyber {description}"
        elif "movie" in p_str:
            emoji_prefix = "🍿"
            description = f"Scene {counter_idx:02d} - {description}"
        elif "music" in p_str:
            emoji_prefix = "🎵"
            description = f"Track {counter_idx:02d} - {description}"
        elif "poetic" in p_str:
            emoji_prefix = "🌌"
            description = f"Echoes of {description}"
        elif "creative" in p_str:
            emoji_prefix = "✨"
            description = f"Creative {description}"
        else: # Normal or default
            emoji_prefix = "🖼️"

        # Apply Date + Counter Pattern
        try:
            mtime = os.path.getmtime(image_path)
        except Exception:
            mtime = time.time()
        f_date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
        date_pattern = f"{f_date}_{counter_idx:03d}"

        # Apply Format Pattern (support both UI string keywords & backend constants)
        pat_upper = str(pattern).upper()
        if "EMOJI_NAME" in pat_upper or "EMOJI + NAME" in pat_upper:
            return f"{emoji_prefix} {description}{ext}".strip()
        elif "VIBRANT" in pat_upper or "BOTH" in pat_upper:
            return f"{emoji_prefix} {date_pattern}_{description}{ext}".strip()
        elif "TIMESTAMPS" in pat_upper or "PATTERN ONLY" in pat_upper:
            return f"{date_pattern}_{description}{ext}"
        elif "ORG" in pat_upper or "COUNTER" in pat_upper:
            return f"{counter_idx:03d}_{description}{ext}"
        elif "EMOJI" in pat_upper:
            return f"{emoji_prefix} {description}{ext}".strip()
        elif "MINIMALIST" in pat_upper or "CLEAN" in pat_upper:
            return f"{description}{ext}"
        else: # Fallback: Vibrant pattern if prefix present, else clean
            if emoji_prefix:
                return f"{emoji_prefix} {description}{ext}".strip()
            return f"{description}{ext}"

    def inspect_file_for_junk(self, file_path):
        name = os.path.basename(file_path).lower()
        ext = os.path.splitext(file_path)[1].lower()

        junk_exts = {'.tmp', '.log', '.dmp', '.bak', '.chk', '.crdownload', '.part', '.sys', '.old'}
        if ext in junk_exts:
            return True, f"Temporary file ({ext})"

        if ext == '.exe' and ('setup' in name or 'installer' in name or 'update' in name):
            return True, "Executable Installer package"

        try:
            if os.path.getsize(file_path) == 0:
                return True, "Empty 0-byte file"
        except Exception: pass

        if ext in {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif'}:
            try:
                with Image.open(file_path) as img_raw:
                    img = img_raw.convert("L")
                    stat = ImageStat.Stat(img)
                    brightness = stat.mean[0] if stat.mean else 128
                    if brightness < 8:
                        return True, "Accidental pitch-black photo"

                    img_small = img.resize((256, 256))
                    edges = img_small.filter(ImageFilter.FIND_EDGES)
                    edges_stat = ImageStat.Stat(edges)
                    var_edges = edges_stat.var[0] if edges_stat.var else 0
                    if var_edges < 15 and brightness < 40:
                        return True, "Extremely blurry / dark photo"
            except Exception: pass

        return False, "Clean file"


def preload_model_async():
    """Warms up local AI vision model in background thread on app startup."""
    def _worker():
        try:
            engine = VisionModelEngine()
            print("[AI Engine] Async background warm-up completed successfully.")
        except Exception as e:
            print(f"[AI Engine Warmup Warning]: {e}")

    t = threading.Thread(target=_worker, daemon=True)
    t.start()


def extract_document_text(file_path):
    """Extracts text content or heuristic OCR summary from PDFs, docs, text, and images."""
    if not os.path.exists(file_path):
        return ""

    ext = os.path.splitext(file_path)[1].lower()
    name = os.path.basename(file_path)

    # 1. Plain text & code files
    if ext in {'.txt', '.md', '.json', '.csv', '.log', '.xml', '.html', '.py', '.js'}:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(1024)
                return content.replace('\n', ' ').strip()
        except Exception:
            pass

    # 2. PDF Files
    if ext == '.pdf':
        try:
            with open(file_path, 'rb') as f:
                raw_bytes = f.read(2048)
                # Simple regex text extraction from PDF stream
                matches = re.findall(rb'\((.*?)\)', raw_bytes)
                extracted = " ".join([m.decode('ascii', errors='ignore') for m in matches if len(m) > 3])
                if extracted and len(extracted.strip()) > 5:
                    return extracted[:300]
        except Exception:
            pass
        return "PDF Document"

    # 3. Document keywords from filename heuristics
    name_lower = name.lower()
    doc_types = []
    if 'invoice' in name_lower or 'bill' in name_lower: doc_types.append("Invoice Bill")
    if 'receipt' in name_lower: doc_types.append("Purchase Receipt")
    if 'statement' in name_lower: doc_types.append("Financial Statement")
    if 'contract' in name_lower or 'agreement' in name_lower: doc_types.append("Legal Contract")
    if 'report' in name_lower: doc_types.append("Summary Report")

    if doc_types:
        return " • ".join(doc_types)

    return ""


def semantic_search_files(query, directory):
    """
    Performs natural language semantic search across files in directory.
    Evaluates filename tokens, extracted document text/OCR, and visual metadata.
    Returns list of result objects sorted by relevance score.
    """
    if not os.path.exists(directory):
        return []

    q_clean = query.strip().lower()
    q_tokens = [t for t in re.findall(r'\w+', q_clean) if len(t) > 0]
    if not q_tokens and not q_clean:
        return []

    results = []
    ignored_prefixes = ('.', '$', 'desktop.ini', 'thumbs.db')
    max_scanned_files = 400

    scanned_count = 0
    base_depth = directory.rstrip(os.sep).count(os.sep)

    for root, dirs, files in os.walk(directory):
        # Limit search depth to 2 levels to guarantee instantaneous response
        current_depth = root.count(os.sep) - base_depth
        if current_depth > 2:
            dirs.clear()
            continue

        for f in files:
            if f.lower().startswith(ignored_prefixes):
                continue

            scanned_count += 1
            if scanned_count > max_scanned_files:
                break

            full_path = os.path.join(root, f)
            f_lower = f.lower()
            f_words = re.findall(r'\w+', f_lower)
            ext = os.path.splitext(f)[1].lower()
            doc_text = extract_document_text(full_path).lower()

            combined_text = f"{f_lower} {' '.join(f_words)} {doc_text} {ext} {full_path.lower()}"
            
            score = 0
            # 1. Direct full query substring match in filename
            if q_clean and q_clean in f_lower:
                score += 90
            # 2. Direct full query substring match in doc text / path
            elif q_clean and q_clean in combined_text:
                score += 70

            # 3. Individual token matches (partial / substring)
            matched_tokens = []
            for token in q_tokens:
                if len(token) > 1 and token in f_lower:
                    score += 45
                    matched_tokens.append(token)
                elif len(token) > 1 and token in combined_text:
                    score += 30
                    matched_tokens.append(token)

            # 4. Keyword concept boosts
            if any(k in q_clean for k in ['sunset', 'sun', 'sky', 'beach', 'landscape', 'dark', 'mood', 'photo', 'track']) and any(k in combined_text for k in ['sunset', 'dusk', 'warm', 'sun', 'sky', 'beach', 'photo', 'img', 'dark', 'mood', 'track']):
                score += 35
            if any(k in q_clean for k in ['invoice', 'bill', 'payment', 'receipt', 'tax', 'doc']) and any(k in combined_text for k in ['invoice', 'bill', 'receipt', 'statement', 'pdf', 'doc']):
                score += 45
            if any(k in q_clean for k in ['code', 'screen', 'script', 'dev']) and any(k in combined_text for k in ['code', 'screen', 'script', 'py', 'js', 'html', 'css', 'json']):
                score += 35

            # 5. Fallback: if query token overlap exists with filename
            if score == 0 and len(q_clean) >= 2:
                overlap = sum(1 for char in q_clean if char in f_lower)
                if (overlap / len(q_clean)) > 0.5:
                    score = 40

            if score > 0:
                is_img = ext in {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif', '.tiff', '.ico', '.heic', '.svg'}
                score_clamped = min(99, max(35, score))
                snippet = doc_text[:100] if doc_text else (f"Matches: {', '.join(set(matched_tokens))}" if matched_tokens else f"File: {f}")

                results.append({
                    "original_name": f,
                    "path": full_path,
                    "is_image": is_img,
                    "score": score_clamped,
                    "snippet": snippet,
                    "ext": (ext.replace('.', '') or 'FILE').upper()
                })

        if scanned_count > max_scanned_files:
            break

    # Sort descending by relevance score
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:50]


