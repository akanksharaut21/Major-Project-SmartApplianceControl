import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import re
from datetime import datetime
from PIL import Image, ImageTk

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

class SmartHomeUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hybrid Smart Home Control")
        self.root.geometry("1366x768")
        self.root.configure(bg="#F5F7FA")
        self.root.minsize(1000, 640)

        # ---------- Styles ----------
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=6)
        style.configure("Primary.TButton", background="#0078D7", foreground="white")
        style.configure("Danger.TButton", background="#C62828", foreground="white")
        style.configure("TCheckbutton", font=("Segoe UI", 12), background="#F5F7FA")
        style.configure("TLabel", font=("Segoe UI", 12), background="#F5F7FA")
        style.configure("TProgressbar", thickness=14)

        # ---------- Title ----------
        title_frame = tk.Frame(root, bg="#0078D7", pady=10)
        title_frame.pack(fill="x")
        tk.Label(title_frame, text="🤖 Hybrid Smart Home Control",
                 font=("Segoe UI", 22, "bold"), bg="#0078D7", fg="white").pack()

        # ---------- Action Bar ----------
        action_bar = tk.Frame(root, bg="#E9F2FF")
        action_bar.pack(fill="x")
        ttk.Button(action_bar, text="All ON", command=lambda: self.toggle_all(True)).pack(side="left", padx=8, pady=8)
        ttk.Button(action_bar, text="All OFF", command=lambda: self.toggle_all(False)).pack(side="left", padx=(0,8), pady=8)
        ttk.Button(action_bar, text="Help", command=self.show_help).pack(side="right", padx=8, pady=8)

        # ---------- Main Layout ----------
        main_frame = tk.Frame(root, bg="#F5F7FA", padx=16, pady=16)
        main_frame.pack(fill="both", expand=True)
        main_frame.columnconfigure(0, weight=1)  # Left column
        main_frame.columnconfigure(1, weight=2)  # Right column (gesture bigger)
        main_frame.rowconfigure(0, weight=1)     # Top row (chatbot & voice)
        main_frame.rowconfigure(1, weight=2)     # Bottom row (components & gesture)

        # ---------- Chatbot Module (Top-left) ----------
        chatbot_frame = self.create_card(main_frame, "💬 Chatbot Assistant")
        chatbot_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        self.chat_area_frame = tk.Frame(chatbot_frame, bg="white")
        self.chat_area_frame.pack(fill="both", expand=True, padx=10, pady=(10,5))

        self.chat_area = scrolledtext.ScrolledText(self.chat_area_frame, wrap=tk.WORD, height=5, font=("Segoe UI", 10))
        self.chat_area.pack(pady=(0, 5), fill='both', expand=True)

        chat_input_frame = tk.Frame(self.chat_area_frame, bg="white")
        chat_input_frame.pack(fill="x", pady=(0, 10))
        self.chat_input = tk.Entry(chat_input_frame, font=("Segoe UI", 11), relief="solid", bd=1)
        self.chat_input.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.chat_input.bind("<Return>", self.send_chat_event)
        ttk.Button(chat_input_frame, text="Send", command=self.send_chat).pack(side="left", padx=(0, 6))
        ttk.Button(chat_input_frame, text="Clear", command=self.clear_chat).pack(side="left")
        # ---------- Extra Chatbot Button ----------
        ttk.Button(chatbot_frame, text="Say Hello", command=lambda: self.chat_area.insert(tk.END, "Bot: Hello!\n")).pack(pady=5)

        # ---------- Voice Module (Top-right small) ----------
        voice_frame = self.create_card(main_frame, "🎤 Voice Input Module")
        voice_frame.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)

        self.voice_text_var = tk.StringVar(value="Speak clearly into the microphone.")
        self.voice_label = tk.Label(voice_frame, textvariable=self.voice_text_var, font=("Segoe UI", 11),
                                    bg="white", height=3, relief="solid", bd=1)
        self.voice_label.pack(pady=(10, 5), fill='x', padx=10)

        self.voice_progress = ttk.Progressbar(voice_frame, orient='horizontal', mode='indeterminate', style="TProgressbar")
        self.voice_progress.pack(pady=(0, 5), fill='x', padx=10)

        language_options = ["English", "Hindi", "Marathi"]
        self.language_var = tk.StringVar(value=language_options[0])
        self.language_codes = {"English": "en-IN", "Hindi": "hi-IN", "Marathi": "mr-IN"}

        lang_row = tk.Frame(voice_frame, bg="white")
        lang_row.pack(fill="x", padx=10, pady=6)
        ttk.Label(lang_row, text="Language:").pack(side="left")
        ttk.Combobox(lang_row, textvariable=self.language_var, values=language_options, state="readonly",
                     font=("Segoe UI", 11), width=10).pack(side="left", padx=6)

        self.voice_button = ttk.Button(voice_frame, text="Start Listening", command=self.toggle_voice)
        self.voice_button.pack(pady=(0, 9))
        # ---------- Extra Voice Button ----------
        ttk.Button(voice_frame, text="Test Voice Command", command=lambda: self.voice_text_var.set("Test Command Executed")).pack(pady=2)

        # ---------- Gesture Module (Bottom-right, big) ----------
        gesture_frame = self.create_card(main_frame, "🖐️ Gesture Module")
        gesture_frame.grid(row=1, column=1, sticky="nsew", padx=8, pady=8)

        self.gesture_text_var = tk.StringVar(value="Ensure proper lighting for camera.")
        self.gesture_label = tk.Label(gesture_frame, textvariable=self.gesture_text_var, font=("Segoe UI", 11),
                                      bg="white", relief="solid", bd=1)
        self.gesture_label.pack(pady=(10, 5), fill='x', padx=10)

        self.gesture_canvas = tk.Label(gesture_frame, bg="black")
        self.gesture_canvas.pack(padx=10, pady=(5,10), fill="both", expand=True)

        self.gesture_button = ttk.Button(gesture_frame, text="Start Camera", command=self.toggle_gesture)
        self.gesture_button.pack(pady=(0, 10))
        # ---------- Extra Gesture Button ----------
        ttk.Button(gesture_frame, text="Capture Snapshot", command=lambda: self.show_toast("Snapshot Captured")).pack(pady=2)

        # ---------- Components Module (Bottom-left) ----------
        comp_frame = self.create_card(main_frame, "⚡ Components Control")
        comp_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)

        self.devices = {
            "💡 Light": tk.BooleanVar(value=False),
            "🌬️ Fan": tk.BooleanVar(value=False),
            "📺 TV": tk.BooleanVar(value=False),
            "❄️ AC": tk.BooleanVar(value=False)
        }

        dev_grid = tk.Frame(comp_frame, bg="white")
        dev_grid.pack(fill="x", padx=10, pady=(10, 6))
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
        # ---------- Extra Components Button ----------
        ttk.Button(comp_frame, text="Toggle All Devices", command=lambda: self.toggle_all(True)).pack(pady=4)

        tk.Label(comp_frame, text="Activity Log", font=("Segoe UI", 12, "bold"), bg="white").pack(anchor="w", padx=10, pady=(8, 0))
        self.log_area = scrolledtext.ScrolledText(comp_frame, height=8, wrap=tk.WORD, font=("Segoe UI", 10))
        self.log_area.pack(fill="both", expand=True, padx=10, pady=(4, 10))

        # ---------- Voice/Gesture State ----------
        self.running_voice = False
        self.running_gesture = False
        self.cap = None
        self.mp_hands = None
        self.hands = None
        self.mp_draw = None
        if mp is not None:
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
            self.mp_draw = mp.solutions.drawing_utils

        self.last_gesture_time = 0.0
        self.gesture_cooldown = 1.0  # seconds

        # ---------- Status Bar ----------
        self.status_bar = tk.Label(root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#333", fg="white")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Initialize canvas black
        self._clear_gesture_canvas()

    # ---------- Utility Methods ----------
    def create_card(self, parent, title):
        frame = tk.Frame(parent, bg="white", relief="raised", bd=2)
        tk.Label(frame, text=title, font=("Segoe UI", 14, "bold"), bg="#0078D7", fg="white", pady=6).pack(fill="x")
        return frame

    def show_toast(self, message, duration=2500):
        toast = tk.Label(self.root, text=message, bg="#333", fg="white",
                         font=("Segoe UI", 11, "bold"), bd=1, relief="raised", padx=10, pady=5)
        toast.place(relx=0.8, rely=0.05)
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

    # ---------- Voice Methods ----------
    def toggle_voice(self):
        if sr is None:
            messagebox.showerror("Voice Error", "SpeechRecognition not available.")
            return
        if not self.running_voice:
            self.running_voice = True
            self.voice_button.config(text="Stop Listening")
            self.voice_progress.start(12)
            self.show_toast("Voice module started")
            threading.Thread(target=self.voice_loop, daemon=True).start()
        else:
            self.running_voice = False
            self.voice_button.config(text="Start Listening")
            self.voice_progress.stop()
            self.voice_text_var.set("Voice module stopped.")
            self.show_toast("Voice module stopped")

    def voice_loop(self):
        recognizer = sr.Recognizer()
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
                    self.process_voice_command(text)
                except sr.UnknownValueError:
                    self.safe_update(self.voice_text_var.set, "Could not understand audio")
                except sr.RequestError as e:
                    self.safe_update(self.voice_text_var.set, f"Service error: {e}")
            except sr.WaitTimeoutError:
                self.safe_update(self.voice_text_var.set, "Timeout: No speech detected")
            except Exception as e:
                self.safe_update(self.voice_text_var.set, f"⚠️ Voice error: {e}")
            time.sleep(0.1)

    def process_voice_command(self, command: str):
        on_patterns = [r"\bturn\s+on\b", r"\bswitch\s+on\b", r"\bstart\b", "चालू करा", "चालू"]
        off_patterns = [r"\bturn\s+off\b", r"\bswitch\s+off\b", r"\bstop\b", "बंद करा", "बंद"]
        action = None
        if any(re.search(p, command) for p in on_patterns):
            action = True
        elif any(re.search(p, command) for p in off_patterns):
            action = False

        mapping = {
            ("light", "बत्ती"): "💡 Light",
            ("fan", "पंख", "पंखा"): "🌬️ Fan",
            ("tv", "television"): "📺 TV",
            ("ac", "air conditioner", "cooler"): "❄️ AC",
        }

        device = None
        for keys, name in mapping.items():
            if any(k in command for k in keys):
                device = name
                break

        if device is not None and action is not None:
            changed = self.devices[device].get() != action
            self.devices[device].set(action)
            self.update_devices()
            self.show_toast(f"{device} turned {'ON' if action else 'OFF'} via voice")
            self.log(f"Voice command → {device} set to {'ON' if action else 'OFF'}", "voice")

    # ---------- Gesture Methods ----------
    def toggle_gesture(self):
        if cv2 is None or mp is None:
            messagebox.showerror("Gesture Error", "OpenCV/MediaPipe not available.")
            return
        if not self.running_gesture:
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) if hasattr(cv2, "CAP_DSHOW") else cv2.VideoCapture(0)
            if not self.cap or not self.cap.isOpened():
                messagebox.showerror("Camera Error", "Could not open webcam.")
                self.running_gesture = False
                self.gesture_button.config(text="Start Camera")
                return
            try:
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
            except Exception:
                pass
            self.running_gesture = True
            self.gesture_button.config(text="Stop Camera")
            self.show_toast("Gesture module started")
            threading.Thread(target=self.gesture_loop, daemon=True).start()
        else:
            self.running_gesture = False
            self.gesture_button.config(text="Start Camera")
            self.show_toast("Gesture module stopped")

    def count_fingers(self, handLms, handedness_label):
        tips = [4, 8, 12, 16, 20]
        lm = handLms.landmark
        fingers = []

        thumb_tip = lm[tips[0]].x
        thumb_ip = lm[tips[0]-1].x
        if handedness_label == "Right":
            fingers.append(1 if thumb_tip > thumb_ip + 0.02 else 0)
        else:
            fingers.append(1 if thumb_tip < thumb_ip - 0.02 else 0)

        for i in range(1, 5):
            tip_y = lm[tips[i]].y
            pip_y = lm[tips[i]-2].y
            fingers.append(1 if tip_y < pip_y - 0.02 else 0)

        return sum(fingers)

    def _set_gesture_image(self, imgtk):
        self.gesture_canvas.configure(image=imgtk)
        self.gesture_canvas.image = imgtk

    def gesture_loop(self):
        try:
            while self.running_gesture and self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    time.sleep(0.02)
                    continue
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.hands.process(rgb_frame) if self.hands else None
                action_taken = False

                if results and results.multi_hand_landmarks:
                    handedness_list = ["Right"] * len(results.multi_hand_landmarks)
                    if hasattr(results, "multi_handedness") and results.multi_handedness:
                        handedness_list = [h.classification[0].label for h in results.multi_handedness]

                    for handLms, hand_label in zip(results.multi_hand_landmarks, handedness_list):
                        if self.mp_draw:
                            self.mp_draw.draw_landmarks(frame, handLms, self.mp_hands.HsAND_CONNECTIONS)
                        fingers_up = self.count_fingers(handLms, hand_label)
                        current_time = time.time()
                        if current_time - self.last_gesture_time > self.gesture_cooldown:
                            self.last_gesture_time = current_time
                            if fingers_up == 1:
                                self.toggle_all(True)
                                action_taken = True
                            elif fingers_up == 0:
                                self.toggle_all(False)
                                action_taken = True
                        if action_taken:
                            self.log(f"Gesture detected: {fingers_up} fingers → All devices {'ON' if fingers_up==1 else 'OFF'}", "gesture")

                imgtk = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
                self.safe_update(self._set_gesture_image, imgtk)
                time.sleep(0.02)
        finally:
            if self.cap:
                self.cap.release()
            self._clear_gesture_canvas()
            self.running_gesture = False
            self.safe_update(self.gesture_button.config, {"text": "Start Camera"})

    def _clear_gesture_canvas(self):
        self.gesture_canvas.configure(image="", bg="black")
        self.gesture_canvas.image = None

    # ---------- Chatbot Methods ----------
    def send_chat_event(self, event):
        self.send_chat()

    def send_chat(self):
        user_text = self.chat_input.get().strip()
        if user_text:
            self.chat_area.insert(tk.END, f"You: {user_text}\n")
            self.chat_input.delete(0, tk.END)
            self.chat_area.insert(tk.END, f"Bot: {user_text[::-1]}\n")  # simple reversal for demo
            self.chat_area.see(tk.END)

    def clear_chat(self):
        self.chat_area.delete("1.0", tk.END)

    # ---------- Toggle Methods ----------
    def toggle_all(self, state=True):
        for device in self.devices:
            self.devices[device].set(state)
            self.update_chip(device)
        self.show_toast(f"All devices turned {'ON' if state else 'OFF'}")
        self.log(f"All devices set to {'ON' if state else 'OFF'}", "status")

    # ---------- Helper ----------
    def safe_update(self, func, *args, **kwargs):
        try:
            self.root.after(0, lambda: func(*args, **kwargs))
        except Exception:
            pass

    # ---------- Help ----------
    def show_help(self):
        messagebox.showinfo("Help", "This is a hybrid smart home UI.\n\n- Use voice or gesture modules to control devices.\n- Chatbot can respond.\n- Use checkboxes or buttons to control components manually.")

    # ---------- Close ----------
    def on_closing(self):
        self.running_voice = False
        self.running_gesture = False
        if self.cap:
            self.cap.release()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = SmartHomeUI(root)
    root.mainloop()
