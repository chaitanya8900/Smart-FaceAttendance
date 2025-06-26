import cv2
import mediapipe as mp
import numpy as np
import pandas as ps
import os
import pickle
import sqlite3
import csv
from datetime import datetime
import threading
import tkinter as tk
from tkinter import messagebox
from gspread_helper import sync_to_sheet  # ✅ Google Sheet integration
from notifier import send_notification


def load_encodings():
    encodings, names = [], []
    if os.path.exists("encodings.pickle"):
        with open("encodings.pickle", "rb") as f:
            while True:
                try:
                    name, enc = pickle.load(f)
                    names.append(name)
                    encodings.append(enc)
                except EOFError:
                    break
    return encodings, names


def show_popup(name):
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Welcome!", f"✅ {name} recognized!")
    root.destroy()


def mark_attendance(name):
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    conn = sqlite3.connect("attendance.db")
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS attendance (
        name TEXT, date TEXT, time TEXT)''')

    cur.execute("SELECT * FROM attendance WHERE name=? AND date=?", (name, date))
    if cur.fetchone() is None:
        cur.execute("INSERT INTO attendance VALUES (?, ?, ?)",
                    (name, date, time))
        conn.commit()

        with open("attendance.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([name, date, time])

        sync_to_sheet(name, date, time)  # ✅ Cloud sync
        threading.Thread(target=show_popup, args=(name,)).start()
        print(f"🟢 {name} marked present at {time}")
        result = "marked"
    else:
        result = "already"
    conn.close()
    send_notification(name, date, time)
    return result


def recognize_faces():
    known_encodings, known_names = load_encodings()
    if not known_encodings:
        print("⚠️ No registered faces. Run register.py first.")
        return

    mp_face = mp.solutions.face_detection
    face_detection = mp_face.FaceDetection(
        model_selection=0, min_detection_confidence=0.5)

    print("🔍 Starting recognition. Press 'q' to quit.")
    seen = set()
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot open camera.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detection.process(rgb)

        if results.detections:
            for det in results.detections:
                box = det.location_data.relative_bounding_box
                h, w, _ = frame.shape
                x, y = int(box.xmin * w), int(box.ymin * h)
                w_box, h_box = int(box.width * w), int(box.height * h)

                face_img = rgb[y:y + h_box, x:x + w_box]
                if face_img.size == 0:
                    continue

                face_vec = np.array(face_img).flatten()[:5120]
                for idx, enc in enumerate(known_encodings):
                    match = np.linalg.norm(enc - face_vec) < 10000
                    if match:
                        name = known_names[idx]
                        if name not in seen:
                            status = mark_attendance(name)
                            seen.add(name)
                            if status == "already":
                                print(f"ℹ️ {name} already marked today.")
                        cv2.putText(frame, name, (x, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
                        cv2.rectangle(frame, (x, y), (x + w_box,
                                      y + h_box), (0, 255, 0), 2)
                        break

        cv2.imshow("Face Attendance", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    recognize_faces()
