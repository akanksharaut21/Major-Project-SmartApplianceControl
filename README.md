# 🏠 Smart Home Automation with Chatbot Assistance  

This project implements a **low-cost smart home automation system** powered by **chatbot assistance**.  
It allows users to control home appliances via **voice commands, text queries, or hand gestures**.  
The system also tracks **appliance states, usage patterns, and durations** to provide intelligent feedback like:  

- “Fan has been ON for 2 hours, do you want to turn it OFF?”  
- “Here’s your daily usage summary: Light - 3 hrs, Fan - 5 hrs”  
- “Currently, the TV and Fan are ON.”  

The goal is to build an **affordable, intelligent, and interactive home automation system** using **ESP32 + Laptop-based chatbot**.  

---

## 🚀 Features  

- ✅ **Multi-input control** (Voice, Text, Gesture via laptop mic & camera)  
- ✅ **Appliance control via ESP32 + Relays**  
- ✅ **Chatbot assistant** that:  
  - Detects appliance states (ON/OFF)  
  - Tracks usage time  
  - Answers appliance-related queries  
  - Provides reminders & energy-saving tips  
- ✅ **Daily/Weekly usage logs** stored locally (JSON/CSV/SQLite)  
- ✅ **Low-cost implementation** (uses free APIs and open-source tools)  

---

## 🛠️ System Architecture  

**Laptop (User Interaction Layer):**  
- Voice input (SpeechRecognition + free Google API)  
- Text input (Chatbot terminal/GUI)  
- Gesture input (OpenCV hand detection)  
- Chatbot (Python + Rule-based/ML)  

**ESP32 (Control Layer):**  
- Connects to laptop via WiFi  
- Receives ON/OFF commands  
- Controls appliances via **Relay Module**  

**Data Layer:**  
- Tracks appliance state (ON/OFF)  
- Logs usage (time + duration)  
- Stores in **JSON/CSV/SQLite**  

---

## 🧩 Components Required  

- **Hardware:**  
  - Laptop (microphone + webcam used)  
  - ESP32 WiFi microcontroller  
  - 2/4 channel Relay Module  
  - Appliances (Fan, Light, TV, etc.)  
  - Jumper wires + Breadboard + Power supply  

- **Software/Frameworks:**  
  - Python 3.8+  
  - ESP32 (Arduino IDE / MicroPython)  
  - Libraries:  
    - `speechrecognition` (voice commands)  
    - `opencv-python` (gesture recognition)  
    - `pyttsx3` (text-to-speech feedback)  
    - `flask` / `fastapi` (for laptop-ESP32 communication)  
    - `sqlite3` or `pandas` (for logging usage)  

---

## 🔑 API Keys  

- **Voice recognition** → Free Google SpeechRecognition API (no paid API needed)  
- **Text chatbot** → Local rule-based / Rasa (optional, no key required)  
- **Gesture detection** → OpenCV (no API required)  

*(This keeps the project completely free and offline-friendly)*  

---

