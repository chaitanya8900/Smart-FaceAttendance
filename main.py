import cv2
import mediapipe as mp
import os
import numpy as np
import pickle
import sqlite3
from datetime import datetime

# Load known face encodings
known_encodings = []
known_names = []

if os.path.exists("encodings.pickle"):
    with open("encodings.pickle", "rb") as f:
        while True:
            try:
                name, encoding = pickle.load(f)
                known_names.append(name)
                known_encodings.append(encoding)
            except EOFError:
                break

if not known_encodings:
    print("⚠️ No registered faces. Run register.py first.")
    exit()

# Setup Mediapipe face detection
mp_face = mp.solutions.face_detection
face_detection = mp_face.FaceDetection(
    model_selection=0, min_detection_confidence=0.5)

# SQLite setup


def mark_attendance(name):
    conn = sqlite3.connect("attendance.db")
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS attendance (
                    name TEXT,
                    date TEXT,
                    time TEXT
                )''')
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    cur.execute("SELECT * FROM attendance WHERE name=? AND date=?", (name, date))
    if cur.fetchone() is None:
        cur.execute("INSERT INTO attendance VALUES (?, ?, ?)",
                    (name, date, time))
        conn.commit()
        print(f"🟢 {name} marked present at {time}")
    else:
        # Don't spam the console
        pass

    conn.close()


# ✅ Store already marked names for this session
session_marked = set()

# Start webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Cannot open camera.")
    exit()

print("🔍 Starting face recognition. Press 'q' to quit.")
while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = face_detection.process(rgb)

    if result.detections:
        for det in result.detections:
            box = det.location_data.relative_bounding_box
            h, w, _ = frame.shape
            x, y = int(box.xmin * w), int(box.ymin * h)
            w_box, h_box = int(box.width * w), int(box.height * h)
            cv2.rectangle(frame, (x, y), (x + w_box,
                          y + h_box), (0, 255, 0), 2)

            face_img = rgb[y:y + h_box, x:x + w_box]
            if face_img.size == 0:
                continue

            face_vec = np.array(face_img).flatten()[:5120]
            face_vec = np.pad(
                face_vec, (0, 5120 - len(face_vec)), mode='constant')

            for idx, enc in enumerate(known_encodings):
                match = np.linalg.norm(enc - face_vec) < 10000
                if match:
                    name = known_names[idx]
                    if name not in session_marked:
                        mark_attendance(name)
                        session_marked.add(name)
                    cv2.putText(frame, name, (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
                    break

    cv2.imshow("Face Attendance (Mediapipe)", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
