import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import cv2
import mediapipe as mp
import speech_recognition as sr
from PIL import Image, ImageTk
import re # For advanced voice command parsing

class SmartHomeUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hybrid Smart Assistant")
        self.root.geometry("1366x768")
        self.root.configure(bg="#F5F7FA")

        # Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 12), padding=6)
        style.configure("TLabel", font=("Segoe UI", 12), background="#F5F7FA")

        # Title
        title = tk.Label(root, text="🤖 Hybrid Smart Home Control",
                         font=("Segoe UI", 22, "bold"), bg="#F5F7FA", fg="#333")
        title.pack(pady=15)

        # Main Frame
        main_frame = tk.Frame(root, bg="#F5F7FA")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        main_frame.columnconfigure((0,1), weight=1)
        main_frame.rowconfigure((0,1), weight=1)

        # Voice Input Module
        voice_frame = self.create_card(main_frame, "🎤 Voice Input Module")
        voice_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.voice_text = tk.Label(voice_frame, text="Press 'Start' to listen...",
                                   font=("Segoe UI", 11), bg="white", width=40, height=3, relief="solid")
        self.voice_text.pack(pady=10)
        ttk.Button(voice_frame, text="Start Listening", command=self.start_voice).pack(pady=5)

        # Gesture Module
        gesture_frame = self.create_card(main_frame, "🖐️ Gesture Module")
        gesture_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.gesture_label = tk.Label(gesture_frame, text="Camera feed will appear here",
                                      font=("Segoe UI", 11), bg="white", width=400, height=300, relief="solid")
        self.gesture_label.pack(pady=10)
        ttk.Button(gesture_frame, text="Start Camera", command=self.start_gesture).pack(pady=5)

        # Chatbot
        chatbot_frame = self.create_card(main_frame, "💬 Chatbot Assistant")
        chatbot_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.chat_area = scrolledtext.ScrolledText(chatbot_frame, wrap=tk.WORD, width=50, height=15, font=("Segoe UI", 10))
        self.chat_area.pack(pady=5)
        self.chat_input = tk.Entry(chatbot_frame, font=("Segoe UI", 11))
        self.chat_input.pack(fill="x", pady=5)
        ttk.Button(chatbot_frame, text="Send", command=self.send_chat).pack(pady=5)

        # Components
        comp_frame = self.create_card(main_frame, "⚡ Components Control")
        comp_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.devices = {
            "💡 Light": tk.BooleanVar(),
            "🌬️ Fan": tk.BooleanVar(),
            "📺 TV": tk.BooleanVar(),
            "❄️ AC": tk.BooleanVar()
        }
        self.checkbuttons = {}
        for device, var in self.devices.items():
            cb = ttk.Checkbutton(comp_frame, text=device, variable=var, command=self.update_devices)
            cb.pack(anchor="w", pady=5)
            self.checkbuttons[device] = cb

        # Gesture Setup
        self.cap = None
        self.running_gesture = False
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
        self.mp_draw = mp.solutions.drawing_utils

    # ---------------- Functions ----------------
    def create_card(self, parent, title):
        frame = tk.Frame(parent, bg="white", relief="raised", bd=2)
        tk.Label(frame, text=title, font=("Segoe UI", 14, "bold"), bg="#0078D7", fg="white", pady=6).pack(fill="x")
        return frame

    # ---------------- Voice ----------------
    def start_voice(self):
        threading.Thread(target=self.voice_recognition, daemon=True).start()

    def voice_recognition(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.voice_text.config(text="🎤 Listening...")
            try:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
                text = recognizer.recognize_google(audio).lower()
                self.voice_text.config(text=f"Recognized: {text}")
                self.process_voice_command(text)
            except sr.WaitTimeoutError:
                self.voice_text.config(text="Timeout: No speech detected")
            except sr.UnknownValueError:
                self.voice_text.config(text="Could not understand the audio")
            except sr.RequestError as e:
                self.voice_text.config(text=f"Error with speech recognition service: {e}")
            except Exception as e:
                self.voice_text.config(text=f"⚠️ An unexpected error occurred: {str(e)}")

    def process_voice_command(self, command):
        
        # Mapping patterns from your voiceinput.py
        on_patterns = [r'turn\s+on', r'switch\s+on', r'start']
        off_patterns = [r'turn\s+off', r'switch\s+off', r'stop']

        action = None
        device = None

        if any(re.search(p, command) for p in on_patterns):
            action = True
        elif any(re.search(p, command) for p in off_patterns):
            action = False
            
        if "light" in command:
            device = "💡 Light"
        elif "fan" in command:
            device = "🌬️ Fan"
        elif "tv" in command:
            device = "📺 TV"
        elif "ac" in command or "air conditioner" in command:
            device = "❄️ AC"
        
        if device and action is not None:
            self.devices[device].set(action)
            self.update_devices()
        else:
            self.voice_text.config(text="Command not recognized. Please try again.")

    # ---------------- Gesture ----------------
    def start_gesture(self):
        if not self.running_gesture:
            self.running_gesture = True
            self.cap = cv2.VideoCapture(0)
            threading.Thread(target=self.gesture_loop, daemon=True).start()
            
    def get_finger_status(self, hand_landmarks):
        """Return which fingers are up based on landmark positions."""
        finger_status = []
        tip_ids = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky

        # Thumb (special case)
        if hand_landmarks.landmark[tip_ids[0]].x < hand_landmarks.landmark[tip_ids[0] - 1].x:
            finger_status.append(1)
        else:
            finger_status.append(0)

        # Other fingers
        for id in range(1, 5):
            if hand_landmarks.landmark[tip_ids[id]].y < hand_landmarks.landmark[tip_ids[id] - 2].y:
                finger_status.append(1)
            else:
                finger_status.append(0)

        return finger_status

    def gesture_loop(self):
        while self.running_gesture and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)

            gesture_command = None
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    fingers = self.get_finger_status(hand_landmarks)

                    # Appliance Control Mapping from Gesture_Control.py
                    if fingers == [0, 1, 0, 0, 0]:
                        gesture_command = "Light ON"
                    elif fingers == [0, 0, 0, 0, 0]:
                        gesture_command = "Light OFF"
                    elif fingers == [0, 1, 1, 0, 0]:
                        gesture_command = "Fan ON"
                    elif fingers == [1, 1, 1, 1, 1]:
                        gesture_command = "Fan OFF"
                    elif fingers == [0, 1, 1, 1, 0]:
                        gesture_command = "TV ON"
                    elif fingers == [1, 0, 0, 0, 1]:
                        gesture_command = "TV OFF"
                    elif fingers == [1, 0, 0, 0, 0]:
                        gesture_command = "AC ON"
                    elif fingers == [0, 0, 0, 0, 1]:
                        gesture_command = "AC OFF"

            if gesture_command:
                self.process_gesture_command(gesture_command)

            # Convert frame for Tkinter
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            imgtk = ImageTk.PhotoImage(image=img)
            self.gesture_label.imgtk = imgtk
            self.gesture_label.config(image=imgtk)

        if self.cap:
            self.cap.release()

    def process_gesture_command(self, action):
        if action == "Light ON":
            self.devices["💡 Light"].set(True)
        elif action == "Light OFF":
            self.devices["💡 Light"].set(False)
        elif action == "Fan ON":
            self.devices["🌬️ Fan"].set(True)
        elif action == "Fan OFF":
            self.devices["🌬️ Fan"].set(False)
        elif action == "TV ON":
            self.devices["📺 TV"].set(True)
        elif action == "TV OFF":
            self.devices["📺 TV"].set(False)
        elif action == "AC ON":
            self.devices["❄️ AC"].set(True)
        elif action == "AC OFF":
            self.devices["❄️ AC"].set(False)
        self.update_devices()

    # ---------------- Chatbot ----------------
    def send_chat(self):
        user_msg = self.chat_input.get()
        if user_msg.strip():
            self.chat_area.insert(tk.END, "You: " + user_msg + "\n")
            bot_reply = self.chatbot_reply(user_msg.lower())
            self.chat_area.insert(tk.END, "Bot: " + bot_reply + "\n\n")
            self.chat_input.delete(0, tk.END)

    def chatbot_reply(self, msg):
        if "hello" in msg:
            return "Hi! How can I assist you today?"
        elif "status" in msg or "devices" in msg:
            status = [f"{dev} {'ON' if var.get() else 'OFF'}" for dev, var in self.devices.items()]
            return "Here’s the current device status:\n" + "\n".join(status)
        elif "light" in msg:
            return "Light is " + ("ON" if self.devices["💡 Light"].get() else "OFF")
        elif "fan" in msg:
            return "Fan is " + ("ON" if self.devices["🌬️ Fan"].get() else "OFF")
        else:
            return "Sorry, I didn't understand. Try asking about devices!"

    # ---------------- Devices ----------------
    def update_devices(self):
        status = [f"{dev} {'ON' if var.get() else 'OFF'}" for dev, var in self.devices.items()]
        print("Device Status:", status)

# Run App
if __name__ == "__main__":
    root = tk.Tk()
    app = SmartHomeUI(root)
    root.mainloop()
