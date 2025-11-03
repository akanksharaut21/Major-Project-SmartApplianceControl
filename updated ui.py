import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import re
from datetime import datetime
from PIL import Image, ImageTk
import requests

# Optional imports
try:
    import cv2
except Exception:
    cv2 = None
try:
    import mediapipe as mp
except Exception:
    mp = None
try:
    import speech_recognition as sr
except Exception:
    sr = None

# ---------------- IoT Setup ----------------
ESP32_IP = "10.189.214.56"  # Replace with your ESP32 IP

def control_device(device_name, state: bool):
    """Sends control command to ESP32 via HTTP GET."""
    try:
        # Mapping device to ESP32 endpoints
        endpoints = {
            "💡 Light": "led",
            "🌬 Fan": "fan",
            # "📺 TV": "tv",
            # "❄ AC": "ac"
        }
        if device_name in endpoints:
            url = f"http://{ESP32_IP}/{endpoints[device_name]}/{'on' if state else 'off'}"
            r = requests.get(url, timeout=2)
            if r.status_code == 200:
                print(f"{device_name} {'ON' if state else 'OFF'} successfully")
            else:
                print(f"Failed to control {device_name} (status {r.status_code})")
    except Exception as e:
        # print error but don't crash the UI thread
        print(f"Error controlling {device_name}: {e}")

# ---------------- Gesture Mapping (Updated as requested) ----------------
# This map expects the count of fingers returned by count_fingers()
GESTURE_MAP = {
    1: "💡 Light ON",
    2: "💡 Light OFF",
    3: "🌬 Fan ON",
    4: "🌬 Fan OFF",
    0: "ALL_OFF",
    5: "ALL_ON"
}

# ---------------- Translation dictionary (English, Hindi, Marathi) ----------------
TRANSLATIONS = {
    "greet": {
        "English": "Hello! 👋",
        "Hindi": "नमस्ते! 👋",
        "Marathi": "नमस्कार! 👋"
    },
    "how_help": {
        "English": "How can I help you?",
        "Hindi": "मैं आपकी किस प्रकार मदद करूँ?",
        "Marathi": "मी तुम्हाला कशी मदत करू?"
    },
    "ask_language": {
        "English": "Which language would you like to use? (English / Hindi / Marathi)",
        "Hindi": "आप किस भाषा का प्रयोग करना चाहेंगे? (English / Hindi / Marathi)",
        "Marathi": "आपण कोणती भाषा वापरू इच्छिता? (English / Hindi / Marathi)"
    },
    "ask_mode": {
        "English": "Do you want to use Voice or Gesture to control devices?",
        "Hindi": "क्या आप Voice या Gesture से कंट्रोल करना चाहेंगे?",
        "Marathi": "आपण डिव्हाइस नियंत्रित करण्यासाठी Voice की Gesture वापरू इच्छिता?"
    },
    "ask_device": {
        "English": "Which device would you like to operate? (Light, Fan, TV, AC)",
        "Hindi": "आप किस डिवाइस को नियंत्रित करना चाहेंगे? (Light, Fan, TV, AC)",
        "Marathi": "आपण कोणता डिव्हाइस वापरू इच्छिता? (Light, Fan, TV, AC)"
    },
    "show_commands_intro": {
        "English": "Here are the commands you can use for",
        "Hindi": "यहाँ कमांड हैं जो आप उपयोग कर सकते हैं:",
        "Marathi": "येथे तुम्ही वापरू शकता अशा कमांड आहेत:"
    },
    "voice_command_template": {
        "English": "Voice: Say 'turn on {device}' or 'turn off {device}'.",
        "Hindi": "Voice: कहें ' {device} चालू करो' या ' {device} बंद करो'.",
        "Marathi": "Voice: बोला ' {device} चालू करा' किंवा ' {device} बंद करा'."
    },
    "gesture_command_template": { # UPDATED GESTURE COMMAND INSTRUCTIONS
        "English": "Gesture: Show 1 finger for Light ON, 2 for Light OFF, 3 for Fan ON, 4 for Fan OFF, 0 to turn all OFF, 5 to turn all ON.",
        "Hindi": "Gesture: Light चालू करण्यासाठी 1 अंगुली, बंद करण्यासाठी 2; Fan चालू करण्यासाठी 3, बंद करण्यासाठी 4. सर्व बंद करण्यासाठी 0, सर्व चालू करण्यासाठी 5.",
        "Marathi": "Gesture: Light साठी 1 बोट चालू, 2 बंद; Fan साठी 3 चालू, 4 बंद. सर्व बंद करण्यासाठी 0, सर्व चालू करण्यासाठी 5 दाखवा."
    },
    "choose_mode_buttons": {
        "English": ("Use Voice", "Use Gesture"),
        "Hindi": ("Voice का उपयोग करें", "Gesture का उपयोग करें"),
        "Marathi": ("Voice वापरा", "Gesture वापरा")
    },
    "unknown": {
        "English": "Sorry, I didn't understand. Please try again.",
        "Hindi": "क्षमा करें, मुझे समझ नहीं आया। कृपया पुनः कोशिश करें।",
        "Marathi": "माफ करा, मला समजले नाही. कृपया पुन्हा प्रयत्न करा."
    },
    "chatbot_features": {
        "English": "I can: 1) Control devices via Voice 2) Control via Gesture 3) Show commands and help.",
        "Hindi": "मैं कर सकता हूँ: 1) Voice से कंट्रोल 2) Gesture से कंट्रोल 3) कमांड और मदद दिखाना।",
        "Marathi": "मी करू शकतो: 1) Voice द्वारे नियंत्रित 2) Gesture द्वारे नियंत्रित 3) कमांड आणि मदत दाखवणे."
    }
}

# ---------------- Smart Home UI ----------------
class SmartHomeUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Hybrid Smart Home Control")
        self.root.geometry("1366x768")
        self.root.configure(bg="#F5F7FA")
        self.root.minsize(1000, 640)

        # ---------------- Styles ----------------
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=6)
        style.configure("Primary.TButton", background="#0078D7", foreground="white")
        style.configure("Danger.TButton", background="#C62828", foreground="white")
        style.configure("TCheckbutton", font=("Segoe UI", 12), background="#F5F7FA")
        style.configure("TLabel", font=("Segoe UI", 12), background="#F5F7FA")
        style.configure("TProgressbar", thickness=14)

        # ---------------- Title ----------------
        title_frame = tk.Frame(root, bg="#0078D7", pady=10)
        title_frame.pack(fill="x")
        tk.Label(title_frame, text="🤖 Hybrid Smart Home Control",
                 font=("Segoe UI", 22, "bold"), bg="#0078D7", fg="white").pack()

        # ---------------- Main Layout ----------------
        main_frame = tk.Frame(root, bg="#F5F7FA", padx=16, pady=16)
        main_frame.pack(fill="both", expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=2)

        # ---------------- Chatbot Module ----------------
        chatbot_frame = self.create_card(main_frame, "💬 Chatbot Assistant")
        chatbot_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        self.chat_area_frame = tk.Frame(chatbot_frame, bg="white")
        self.chat_area_frame.pack(fill="both", expand=True, padx=10, pady=(10,5))
        self.chat_area = scrolledtext.ScrolledText(self.chat_area_frame, wrap=tk.WORD, height=8, font=("Segoe UI", 10))
        self.chat_area.pack(pady=(0,5), fill='both', expand=True)

        chat_input_frame = tk.Frame(self.chat_area_frame, bg="white")
        chat_input_frame.pack(fill="x", pady=(0,10))
        self.chat_input = tk.Entry(chat_input_frame, font=("Segoe UI", 11), relief="solid", bd=1)
        self.chat_input.pack(side="left", fill="x", expand=True, padx=(0,6))
        self.chat_input.bind("<Return>", self.send_chat_event)
        ttk.Button(chat_input_frame, text="Send", command=self.send_chat).pack(side="left", padx=(0,6))
        ttk.Button(chat_input_frame, text="Clear", command=self.clear_chat).pack(side="left")
        # Quick mode buttons (appear during flow)
        self.mode_buttons_frame = tk.Frame(self.chat_area_frame, bg="white")
        self.mode_buttons_frame.pack(fill="x", pady=(6,0))

        # ---------------- Voice Module ----------------
        voice_frame = self.create_card(main_frame, "🎤 Voice Input Module")
        voice_frame.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)

        self.voice_text_var = tk.StringVar(value="Speak clearly into the microphone.")
        self.voice_label = tk.Label(voice_frame, textvariable=self.voice_text_var, font=("Segoe UI", 11),
                                     bg="white", height=3, relief="solid", bd=1)
        self.voice_label.pack(pady=(10,5), fill='x', padx=10)

        self.voice_progress = ttk.Progressbar(voice_frame, orient='horizontal', mode='indeterminate', style="TProgressbar")
        self.voice_progress.pack(pady=(0,5), fill='x', padx=10)

        language_options = ["English", "Hindi", "Marathi"]
        self.language_var = tk.StringVar(value=language_options[0])
        self.language_codes = {"English": "en-IN", "Hindi": "hi-IN", "Marathi": "mr-IN"}

        lang_row = tk.Frame(voice_frame, bg="white")
        lang_row.pack(fill="x", padx=10, pady=6)
        ttk.Label(lang_row, text="Language:").pack(side="left")
        self.lang_combobox = ttk.Combobox(lang_row, textvariable=self.language_var, values=language_options, state="readonly",
                             font=("Segoe UI", 11), width=10)
        self.lang_combobox.pack(side="left", padx=6)

        self.voice_button = ttk.Button(voice_frame, text="Start Listening", command=self.toggle_voice)
        self.voice_button.pack(pady=(0,9))

        # ---------------- Gesture Module ----------------
        gesture_frame = self.create_card(main_frame, "🖐 Gesture Module")
        gesture_frame.grid(row=1, column=1, sticky="nsew", padx=8, pady=8)

        self.gesture_text_var = tk.StringVar(value="Ensure proper lighting for camera.")
        self.gesture_label = tk.Label(gesture_frame, textvariable=self.gesture_text_var, font=("Segoe UI", 11),
                                         bg="white", relief="solid", bd=1)
        self.gesture_label.pack(pady=(10,5), fill='x', padx=10)

        self.gesture_canvas = tk.Label(gesture_frame, bg="black")
        self.gesture_canvas.pack(padx=10, pady=(5,10), fill="both", expand=True)

        self.gesture_button = ttk.Button(gesture_frame, text="Start Camera", command=self.toggle_gesture)
        self.gesture_button.pack(pady=(0,10))

        # Bind ESC to stop camera quickly
        try:
            self.root.bind('<Escape>', lambda e: self.stop_gesture())
        except Exception:
            pass

        # ---------------- Components Module ----------------
        comp_frame = self.create_card(main_frame, "⚡ Components Control")
        comp_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)

        # ESP32 IP controls
        self.esp32_ip_var = tk.StringVar(value=ESP32_IP)
        ip_row = tk.Frame(comp_frame, bg="white")
        ip_row.pack(fill="x", padx=10, pady=(10,4))
        ttk.Label(ip_row, text="ESP32 IP:").pack(side="left")
        self.ip_entry = tk.Entry(ip_row, textvariable=self.esp32_ip_var, width=18, relief="solid", bd=1)
        self.ip_entry.pack(side="left", padx=(6,6))
        ttk.Button(ip_row, text="Save", command=self.save_ip).pack(side="left", padx=(0,6))
        ttk.Button(ip_row, text="Test Connection", command=self.test_connection).pack(side="left")

        self.devices = {
            "💡 Light": tk.BooleanVar(value=False),
            "🌬 Fan": tk.BooleanVar(value=False),
            "📺 TV": tk.BooleanVar(value=False),
            "❄ AC": tk.BooleanVar(value=False)
        }

        dev_grid = tk.Frame(comp_frame, bg="white")
        dev_grid.pack(fill="x", padx=10, pady=(10,6))
        self.chips = {}
        for i, (device, var) in enumerate(self.devices.items()):
            row = tk.Frame(dev_grid, bg="white")
            row.grid(row=i, column=0, sticky="ew", pady=4)
            row.columnconfigure(1, weight=1)
            ttk.Checkbutton(row, text=device, variable=var, command=self.update_devices, style="TCheckbutton")\
                .grid(row=0, column=0, sticky="w")
            chip_var = tk.StringVar()
            chip = tk.Label(row, textvariable=chip_var, font=("Segoe UI", 10, "bold"), bd=0, relief="solid", padx=10, pady=2)
            chip.grid(row=0, column=2, sticky="e")
            self.chips[device] = (chip_var, chip)
            self.update_chip(device)

        self.log_area = scrolledtext.ScrolledText(comp_frame, height=8, wrap=tk.WORD, font=("Segoe UI", 10))
        self.log_area.pack(fill="both", expand=True, padx=10, pady=(4,10))

        # ---------------- Voice/Gesture State ----------------
        self.running_voice = False
        self.running_gesture = False
        self.cap = None
        self.mp_hands = None
        self.hands = None
        self.mp_draw = None
        if mp is not None:
            try:
                self.mp_hands = mp.solutions.hands
                self.hands = self.mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
                self.mp_draw = mp.solutions.drawing_utils
            except Exception as e:
                print("MediaPipe init error:", e)
                self.mp_hands = None
                self.hands = None
                self.mp_draw = None

        self.last_gesture_time = 0.0
        self.gesture_cooldown = 2.0  # Increased cooldown to 2.0 seconds for better usability
        # Stabilization: require same count for N frames before acting
        self.required_stable_frames = 5
        self.gesture_recent_counts = []
        self.last_confirmed_count = None

        self.status_bar = tk.Label(root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#333", fg="white")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self._clear_gesture_canvas()

        # ---------------- Voice command mapping ----------------
        # Include english/hindi/marathi common phrases (simple)
        self.on_patterns = [r"turn on", r"switch on", r"start", "चालू करा", "चालू", "ऑन", "on"]
        self.off_patterns = [r"turn off", r"switch off", r"stop", "बंद करा", "बंद", "ऑफ", "off"]

        # mapping for many synonyms (English/Hindi/Marathi)
        self.device_keyword_map = {
            "light": "💡 Light", "बत्ती": "💡 Light", "लाईट": "💡 Light", "लाइट": "💡 Light",
            "fan": "🌬 Fan", "पंखा": "🌬 Fan", "पंख": "🌬 Fan",
            "tv": "📺 TV", "television": "📺 TV", "टीवी": "📺 TV",
            "ac": "❄ AC", "cooler": "❄ AC", "air conditioner": "❄ AC", "एसी": "❄ AC"
        }

        # Conversational flow state
        self.stage = 0
        # We'll keep the selected device and mode in these:
        self.selected_mode = None  # "Voice" or "Gesture"
        self.selected_device = None
        self.selected_language = self.language_var.get()

        # start conversation automatically
        self.safe_update(self.start_conversation)

    # ---------------- Utilities ----------------
    def create_card(self, parent, title):
        frame = tk.Frame(parent, bg="white", relief="raised", bd=2)
        tk.Label(frame, text=title, font=("Segoe UI", 14, "bold"), bg="#0078D7", fg="white", pady=6).pack(fill="x")
        return frame

    def show_toast(self, message, duration=2500):
        toast = tk.Label(self.root, text=message, bg="#333", fg="white",
                         font=("Segoe UI", 11, "bold"), bd=1, relief="raised", padx=10, pady=5)
        toast.place(relx=0.8, rely=0.05, anchor='ne') # Adjusted placement
        self.root.after(duration, toast.destroy)

    def log(self, text, type_="status"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_area.tag_configure("voice", foreground="blue")
        self.log_area.tag_configure("gesture", foreground="green")
        self.log_area.tag_configure("status", foreground="black")
        self.log_area.insert(tk.END, f"[{timestamp}] {text}\n", type_)
        self.log_area.see(tk.END)

    def update_chip(self, device):
        chip_var, chip = self.chips[device]
        state = "ON" if self.devices[device].get() else "OFF"
        chip_var.set(state)
        chip.configure(bg="#E8F5E9" if self.devices[device].get() else "#FFEBEE",
                         fg="#1B5E20" if self.devices[device].get() else "#B71C1C")

    def update_devices(self):
        for device in self.devices:
            self.update_chip(device)
            # IoT Control (run but don't block UI)
            try:
                threading.Thread(target=self.send_device_command, args=(device, self.devices[device].get()), daemon=True).start()
            except Exception:
                pass

    # ---------------- Networking helpers ----------------
    def save_ip(self):
        global ESP32_IP
        ip = (self.esp32_ip_var.get() or "").strip()
        if not ip:
            self.show_toast("Enter a valid IP")
            return
        ESP32_IP = ip
        self.log(f"ESP32 IP set to {ip}")
        self.show_toast(f"IP saved: {ip}")

    def test_connection(self):
        ip = (self.esp32_ip_var.get() or "").strip()
        if not ip:
            self.show_toast("Enter ESP32 IP")
            return
        def _probe():
            try:
                r = requests.get(f"http://{ip}/", timeout=4)
                self.log(f"Probe {ip} → HTTP {r.status_code}")
                if r.status_code < 400 and isinstance(r.text, str) and "ESP32 Smart Control Server Running" in r.text:
                    self.safe_update(self.show_toast, "Connected ✔")
                elif r.status_code < 400:
                    self.safe_update(self.show_toast, "Reachable (unexpected content)")
                else:
                    self.safe_update(self.show_toast, f"Reachable, status {r.status_code}")
            except Exception as e:
                self.log(f"Probe failed: {e}")
                self.safe_update(self.show_toast, "Connection failed ✖")
        threading.Thread(target=_probe, daemon=True).start()

    def send_device_command(self, device_name, state):
        try:
            ip = (self.esp32_ip_var.get() or "").strip()
            if not ip:
                self.log("ESP32 IP not set", "status")
                return
            # Exact endpoints per Arduino sketch
            if device_name == "💡 Light":
                url = f"http://{ip}/light/{'on' if state else 'off'}"
            elif device_name == "🌬 Fan":
                url = f"http://{ip}/fan/{'on' if state else 'off'}"
            else:
                return
            r = requests.get(url, timeout=5)
            self.log(f"{device_name} → {url} → HTTP {r.status_code}")
            if 200 <= r.status_code < 300:
                return
            self.safe_update(self.show_toast, f"Failed: {device_name}")
        except Exception as e:
            self.log(f"Error controlling {device_name}: {e}")
            self.safe_update(self.show_toast, f"Network error: {device_name}")

    # ---------------- Chatbot Flow ----------------
    def start_conversation(self):
        # Stage 0: greet
        self.stage = 0
        self.selected_mode = None
        self.selected_device = None
        self.selected_language = self.language_var.get()
        self.post_bot_message(self.translate("greet"))
        # Using after to simulate a small delay without blocking
        self.root.after(200, lambda: self.post_bot_message(self.translate("how_help")))
        self.root.after(400, lambda: self.post_bot_message(self.translate("ask_language")))
        # ask for language preference next
        self.stage = 1
        self.root.after(600, lambda: self.post_bot_message(self.translate("chatbot_features")))

        # place mode selection buttons hidden until language is chosen
        self._render_mode_buttons()

    def translate(self, key, **kwargs):
        lang = self.selected_language if hasattr(self, "selected_language") else self.language_var.get()
        text_template = TRANSLATIONS.get(key, {}).get(lang, "")
        if kwargs:
            return text_template.format(**kwargs)
        return text_template

    def _render_mode_buttons(self):
        # Clear previous
        for w in self.mode_buttons_frame.winfo_children():
            w.destroy()
        # Buttons show language-specific labels
        texts = TRANSLATIONS["choose_mode_buttons"].get(self.selected_language, TRANSLATIONS["choose_mode_buttons"]["English"])
        b1 = ttk.Button(self.mode_buttons_frame, text=texts[0], command=lambda: self.handle_mode_choice("Voice"))
        b2 = ttk.Button(self.mode_buttons_frame, text=texts[1], command=lambda: self.handle_mode_choice("Gesture"))
        # initially hidden — only enabled after language chosen (stage >=2)
        b1.pack(side="left", padx=(0,6))
        b2.pack(side="left")
        if self.stage < 2:
            b1.configure(state="disabled")
            b2.configure(state="disabled")
        else:
            b1.configure(state="normal")
            b2.configure(state="normal")

    def post_bot_message(self, text):
        # Insert into chat area and keep cursor at end
        self.chat_area.insert(tk.END, f"Bot: {text}\n")
        self.chat_area.see(tk.END)

    def send_chat_event(self, event):
        self.send_chat()

    def send_chat(self):
        raw = self.chat_input.get().strip()
        if not raw:
            return
        self.chat_input.delete(0, tk.END)
        # display user input
        self.chat_area.insert(tk.END, f"You: {raw}\n")
        self.chat_area.see(tk.END)
        # process according to conversation stage
        self.chatbot_handle_user_response(raw.strip())

    def clear_chat(self):
        self.chat_area.delete("1.0", tk.END)

    def chatbot_handle_user_response(self, raw_text):
        text = raw_text.lower()
        # stage 1: ask language preference
        if self.stage == 1:
            # try to detect language keywords
            if "english" in text or "eng" in text:
                self.selected_language = "English"
            elif "hindi" in text or "हिन्दी" in text or "हिंदी" in text:
                self.selected_language = "Hindi"
            elif "marathi" in text or "मराठी" in text:
                self.selected_language = "Marathi"
            else:
                # allow user to pick via combobox: sync value
                selected = self.language_var.get()
                if selected in ("English", "Hindi", "Marathi"):
                    self.selected_language = selected
                else:
                    # unknown language choice
                    self.post_bot_message(self.translate("unknown"))
                    return
            # update combobox to belief
            self.safe_update(self.language_var.set, self.selected_language)
            self.safe_update(self.lang_combobox.set, self.selected_language)
            self.post_bot_message({
                "English": f"Language set to {self.selected_language}.",
                "Hindi": f"भाषा {self.selected_language} नियुक्त की गई।",
                "Marathi": f"भाषा {self.selected_language} सेट केली."
            }.get(self.selected_language, f"Language set to {self.selected_language}."))

            # proceed to ask mode
            self.stage = 2
            self._render_mode_buttons()
            self.post_bot_message(self.translate("ask_mode"))
            return

        # stage 2: expect mode (Voice/Gesture)
        if self.stage == 2:
            # if user typed mode
            if "voice" in text or "वॉइस" in text or "आवाज" in text:
                self.handle_mode_choice("Voice")
                return
            if "gesture" in text or "हावभाव" in text or "इशारा" in text:
                self.handle_mode_choice("Gesture")
                return
            # unknown
            self.post_bot_message(self.translate("unknown"))
            return

        # stage 3: expect device name
        if self.stage == 3:
            # try to map device keywords
            for k, v in self.device_keyword_map.items():
                if k in text:
                    self.selected_device = v
                    break
            # allow english names as well
            if not self.selected_device:
                if "light" in text or "बत्ती" in text or "लाइट" in text or "लाईट" in text:
                    self.selected_device = "💡 Light"
                elif "fan" in text or "पंख" in text or "पंखा" in text:
                    self.selected_device = "🌬 Fan"
                elif "tv" in text or "television" in text or "टीवी" in text:
                    self.selected_device = "📺 TV"
                elif "ac" in text or "cooler" in text or "एसी" in text:
                    self.selected_device = "❄ AC"

            if not self.selected_device:
                self.post_bot_message(self.translate("unknown"))
                return

            # We have device — show commands
            self.stage = 4
            self.post_bot_message(f"{self.translate('show_commands_intro')} {self.selected_device}")
            # show voice command template in chosen language
            self.post_bot_message(self.translate("voice_command_template", device=self.strip_emoji(self.selected_device)))
            # show gesture template
            self.post_bot_message(self.translate("gesture_command_template"))
            # remind features
            self.post_bot_message(self.translate("chatbot_features"))
            # done stage — keep at stage 4, allow repeated commands / direct control
            return

        # default fallback for later stages: interpret direct control sentences
        # If user typed "turn on light" or language equivalent, try to control device
        # Reuse process_voice_command logic for typed commands
        reply_before = self.process_typed_command(text)
        if reply_before:
            self.post_bot_message(reply_before)
            return

        # fallback unknown
        self.post_bot_message(self.translate("unknown"))

    def handle_mode_choice(self, mode):
        self.selected_mode = mode
        # If user chooses Gesture, offer to start camera; if Voice, suggest to start listening
        if mode == "Voice":
            self.post_bot_message({
                "English": "Voice mode selected. Press 'Start Listening' to begin.",
                "Hindi": "Voice मोड चुना गया। शुरू करने के लिए 'Start Listening' दबाएँ।",
                "Marathi": "Voice मोड निवडला गेला. सुरू करण्यासाठी 'Start Listening' दाबा."
            }[self.selected_language])
            # move to device selection
            self.stage = 3
            self.post_bot_message(self.translate("ask_device"))
        else:
            self.post_bot_message({
                "English": "Gesture mode selected. Press 'Start Camera' to begin gesture control.",
                "Hindi": "Gesture मोड चुना गया। कैमरा शुरू करने के लिए 'Start Camera' दबाएँ।",
                "Marathi": "Gesture मोड निवडला गेला. Gesture नियंत्रण सुरू करण्यासाठी 'Start Camera' दाबा."
            }[self.selected_language])
            # move to device selection
            self.stage = 3
            self.post_bot_message(self.translate("ask_device"))
        # enable mode buttons now (they are enabled already when stage >=2)
        self._render_mode_buttons()

    def strip_emoji(self, device_label):
        # e.g. "💡 Light" -> "Light"
        return re.sub(r"[^\w\s]", "", device_label).strip().split()[-1]

    def process_typed_command(self, text):
        """
        Try to parse a typed command and act (used for typed chat control).
        Returns a bot reply string if an action happened, else None.
        """
        action = None
        if any(re.search(p, text) for p in self.on_patterns):
            action = True
        elif any(re.search(p, text) for p in self.off_patterns):
            action = False

        device = None
        for k, v in self.device_keyword_map.items():
            if k in text:
                device = v
                break
        # fallback by english words
        if not device:
            if "light" in text: device = "💡 Light"
            elif "fan" in text: device = "🌬 Fan"
            elif "tv" in text: device = "📺 TV"
            elif "ac" in text: device = "❄ AC"

        if device and action is not None:
            # perform control
            self.devices[device].set(action)
            self.update_devices()
            self.log(f"Chat command → {device} set to {'ON' if action else 'OFF'}", "voice")
            return {
                "English": f"{device} turned {'ON' if action else 'OFF'}.",
                "Hindi": f"{device} {' चालू किया गया' if action else ' बंद किया गया'}.",
                "Marathi": f"{device} {' सुरू केले' if action else ' बंद केले'}."
            }[self.selected_language]
        return None

    # ---------------- Chatbot minimal fallback (kept for compatibility) ----------------
    def chatbot_reply(self, msg):
        # Kept simple — prefer guided flow; this is a compatibility method
        msg = msg.lower()
        if "help" in msg or "commands" in msg:
            commands_text = "You can control appliances using:\n"
            commands_text += "- Voice commands (English/Hindi/Marathi)\n"
            commands_text += "- Gesture commands\n"
            commands_text += "Appliances: Light, Fan, TV, AC\n"
            return commands_text
        elif "voice or gesture" in msg:
            return "You can use either Voice or Gesture commands. Voice commands: 'turn on light', Gesture: show 1 finger for Light ON, 2 for Light OFF, etc."
        else:
            return "Sorry, I can only respond in English here. Use guided flow above."

    # ---------------- Voice ----------------
    def toggle_voice(self):
        if sr is None:
            messagebox.showerror("Voice Error", "SpeechRecognition not available. Please install 'SpeechRecognition' package.")
            return
        if not self.running_voice:
            self.running_voice = True
            self.voice_button.config(text="Stop Listening", style="Danger.TButton")
            self.voice_progress.start(12)
            threading.Thread(target=self.voice_loop, daemon=True).start()
            self.show_toast("Voice module started")
        else:
            self.running_voice = False
            self.voice_button.config(text="Start Listening", style="TButton")
            self.voice_progress.stop()
            self.voice_text_var.set("Voice module stopped.")
            self.show_toast("Voice module stopped")

    def voice_loop(self):
        recognizer = sr.Recognizer()
        # update language for recognizer based on selected_language
        language_code = self.language_codes.get(self.language_var.get(), "en-IN")
        while self.running_voice:
            try:
                with sr.Microphone() as source:
                    self.safe_update(self.voice_text_var.set, f"🎤 Listening in {self.language_var.get()}...")
                    recognizer.adjust_for_ambient_noise(source, duration=0.6)
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=4)
                if not self.running_voice:
                    break
                self.safe_update(self.voice_text_var.set, "Processing audio...")
                try:
                    text = recognizer.recognize_google(audio, language=language_code).lower()
                    self.safe_update(self.voice_text_var.set, f"Recognized: {text}")
                    # feed into typed-command processor to reuse logic (multilingual)
                    reply = self.process_typed_command(text)
                    if reply:
                        self.safe_update(self.post_bot_message, reply)
                    else:
                        # if no direct action found, still show helpful guidance
                        self.safe_update(self.post_bot_message, self.translate("unknown"))
                except sr.UnknownValueError:
                    self.safe_update(self.voice_text_var.set, "Could not understand audio")
                except sr.RequestError as e:
                    self.safe_update(self.voice_text_var.set, f"Service error: {e}")
            except sr.WaitTimeoutError:
                self.safe_update(self.voice_text_var.set, "Timeout: No speech detected")
            except Exception as e:
                self.safe_update(self.voice_text_var.set, f"⚠ Voice error: {e}")
            time.sleep(0.1)

    # ---------------- Gesture ----------------
    def toggle_gesture(self):
        if cv2 is None or mp is None:
            messagebox.showerror("Gesture Error", "OpenCV/MediaPipe not available. Please install 'opencv-python' and 'mediapipe' packages.")
            return
        if not self.running_gesture:
            self.cap = cv2.VideoCapture(0)
            if not self.cap or not self.cap.isOpened():
                messagebox.showerror("Camera Error", "Could not open webcam.")
                self.running_gesture = False
                self.gesture_button.config(text="Start Camera", command=self.toggle_gesture, style="TButton")
                return
            try:
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
            except Exception:
                pass
            self.running_gesture = True
            self.gesture_button.config(text="Stop Camera", command=self.stop_gesture, style="Danger.TButton")
            threading.Thread(target=self.gesture_loop, daemon=True).start()
            self.show_toast("Gesture module started")
        else:
            self.stop_gesture()

    def stop_gesture(self):
        self.running_gesture = False
        try:
            if self.cap:
                try:
                    self.cap.release()
                except Exception:
                    pass
                self.cap = None
        except Exception:
            pass
        self._clear_gesture_canvas()
        self.gesture_button.config(text="Start Camera", command=self.toggle_gesture, style="TButton")
        self.gesture_text_var.set("Camera stopped.")
        self.show_toast("Gesture module stopped")


    def count_fingers(self, handLms, handedness_label):
        """
        Returns the number of fingers considered "up".
        """
        tips = [4,8,12,16,20]
        lm = handLms.landmark
        fingers = []

        # Thumb (use horizontal relative to IP joint)
        try:
            thumb_tip_x = lm[tips[0]].x
            thumb_ip_x = lm[tips[0]-1].x
            # NOTE: Thumb logic is complex, this simple check often works for front-facing
            if handedness_label == "Right":
                fingers.append(1 if thumb_tip_x > thumb_ip_x + 0.02 else 0)
            else:
                fingers.append(1 if thumb_tip_x < thumb_ip_x - 0.02 else 0)
        except Exception:
            fingers.append(0)

        # Other four fingers (vertical: tip y-coordinate is smaller (higher on screen) than PIP y-coordinate)
        for i in range(1,5):
            try:
                tip_y = lm[tips[i]].y
                pip_y = lm[tips[i]-2].y
                # Add tolerance (0.02)
                fingers.append(1 if tip_y < pip_y - 0.02 else 0)
            except Exception:
                fingers.append(0)

        return sum(fingers)

    def _set_gesture_image(self, imgtk):
        self.gesture_canvas.configure(image=imgtk)
        self.gesture_canvas.image = imgtk

    def gesture_loop(self):
        try:
            while self.running_gesture and self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if not self.running_gesture or self.cap is None or (self.cap and not self.cap.isOpened()):
                    break
                if not ret:
                    time.sleep(0.02)
                    continue
                frame = cv2.flip(frame,1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.hands.process(rgb_frame) if self.hands else None
                current_time = time.time()
                
                # --- Gesture Processing with Cooldown and Stabilization ---
                if results and results.multi_hand_landmarks:
                    try:
                        handedness_list = [h.classification[0].label for h in results.multi_handedness] \
                                         if results.multi_handedness else ["Right"] * len(results.multi_hand_landmarks)
                    except Exception:
                        handedness_list = ["Right"] * len(results.multi_hand_landmarks)

                    # Only consider first detected hand
                    handLms = results.multi_hand_landmarks[0]
                    hand_label = handedness_list[0]
                    fingers_up = self.count_fingers(handLms, hand_label)

                    # Keep a sliding window of recent counts
                    self.gesture_recent_counts.append(fingers_up)
                    if len(self.gesture_recent_counts) > self.required_stable_frames:
                        self.gesture_recent_counts.pop(0)

                    # Confirm when all recent counts match and different from last confirmed
                    if len(self.gesture_recent_counts) == self.required_stable_frames and \
                       all(c == self.gesture_recent_counts[0] for c in self.gesture_recent_counts):
                        confirmed = self.gesture_recent_counts[0]
                        if confirmed != self.last_confirmed_count and \
                           current_time - self.last_gesture_time > self.gesture_cooldown:
                            self.last_confirmed_count = confirmed
                            self.last_gesture_time = current_time

                            # Strict mapping
                            gesture_map = {
                                1: ("💡 Light", True),
                                2: ("💡 Light", False),
                                3: ("🌬 Fan", True),
                                4: ("🌬 Fan", False),
                                5: ("ALL", True),
                                0: ("ALL", False),
                            }
                            if confirmed in gesture_map:
                                device_name, state = gesture_map[confirmed]
                                if device_name == "ALL":
                                    for d in list(self.devices.keys()):
                                        self.devices[d].set(state)
                                else:
                                    if device_name in self.devices:
                                        self.devices[device_name].set(state)
                                self.update_devices()
                                label = {
                                    1: "💡 Light ON",
                                    2: "💡 Light OFF",
                                    3: "🌬 Fan ON",
                                    4: "🌬 Fan OFF",
                                    5: "ALL_ON",
                                    0: "ALL_OFF",
                                }[confirmed]
                                self.log(f"Gesture confirmed ({confirmed} fingers) → {label}", "gesture")
                                self.safe_update(self.show_toast, f"{label} via gesture")
                else:
                    # No hands detected: reset recent counts to avoid stale confirmation
                    self.gesture_recent_counts = []

                # Draw landmarks and finger count for visual feedback
                if results and results.multi_hand_landmarks and self.mp_draw:
                    self.mp_draw.draw_landmarks(frame, results.multi_hand_landmarks[0], self.mp_hands.HAND_CONNECTIONS)
                    if 'fingers_up' in locals():
                        cv2.putText(frame, str(fingers_up), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)

                # --- UI Update ---
                imgtk = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
                self.safe_update(self._set_gesture_image, imgtk)
                time.sleep(0.01)
                
        except Exception as e:
            print(f"Gesture Loop Error: {e}")
        finally:
            if self.cap:
                self.cap.release()
            self._clear_gesture_canvas()
            self.running_gesture = False
            self.safe_update(self.gesture_button.config, {"text":"Start Camera", "style":"TButton"})
            self.safe_update(self.gesture_text_var.set, "Camera stopped.")
            try:
                self.safe_update(self.gesture_stop_button.state, ["disabled"])  # disable stop when done
            except Exception:
                pass


    def _clear_gesture_canvas(self):
        self.gesture_canvas.configure(image="", bg="black")
        self.gesture_canvas.image = None

    # ---------------- Helper ----------------
    def safe_update(self, func, *args, **kwargs):
        """Helper to safely call UI updates from a non-main thread."""
        try:
            self.root.after(0, lambda: func(*args, **kwargs))
        except Exception:
            pass

    def on_closing(self):
        self.running_voice = False
        self.running_gesture = False
        if self.cap:
            try:
                self.cap.release()
            except Exception:
                pass
        self.root.destroy()


# ---------------- Main ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = SmartHomeUI(root)
    # 🌟 ADD THIS LINE 🌟
    print("Starting Main Loop...")
    root.mainloop()