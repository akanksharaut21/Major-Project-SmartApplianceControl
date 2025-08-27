import cv2
import mediapipe as mp

# Uncomment if you want ESP32 connection
# import serial
# esp = serial.Serial('COM3', 115200)  # Replace with your ESP32 port

# ============================
# Show Gesture Instructions
# ============================

print("====================================")
print(" Gesture Control for Home Appliances ")
print("====================================")
print(" 💡 Light: Index finger up → ON, Fist → OFF")
print(" 🌬️ Fan: Peace Sign (✌) → ON, Open Palm (🖐) → OFF")
print(" 📺 TV: Three fingers (Index+Middle+Ring) → ON, Thumb+Pinky (🤟) → OFF")
print(" ❄️ AC: Thumbs Up (👍) → ON, Thumbs Down (👎) → OFF")
print("====================================")
print("Press 'q' to exit the program")
print("====================================\n")

# ============================
# Initialize MediaPipe Hand Model
# ============================
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Open Webcam
cap = cv2.VideoCapture(0)

def get_finger_status(hand_landmarks):
    """Return which fingers are up"""
    finger_status = []
    tip_ids = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky

    # Thumb
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

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    command = "No Command"

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            fingers = get_finger_status(hand_landmarks)

            # ============================
            # Appliance Control Mapping
            # ============================

            # Light
            if fingers == [0, 1, 0, 0, 0]:
                command = "Light ON"
            elif fingers == [0, 0, 0, 0, 0]:
                command = "Light OFF"

            # Fan
            elif fingers == [0, 1, 1, 0, 0]:
                command = "Fan ON"
            elif fingers == [1, 1, 1, 1, 1]:
                command = "Fan OFF"

            # TV
            elif fingers == [0, 1, 1, 1, 0]:
                command = "TV ON"
            elif fingers == [1, 0, 0, 0, 1]:
                command = "TV OFF"

            # AC
            elif fingers == [1, 0, 0, 0, 0]:
                command = "AC ON"
            elif fingers == [0, 0, 0, 0, 1]:
                command = "AC OFF"

            cv2.putText(frame, f'Command: {command}', (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Gesture Control - Appliances", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
