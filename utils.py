import sqlite3
from datetime import datetime
import pickle
import os
import face_recognition
from tabulate import tabulate


def load_encodings():
    encodings = []
    names = []
    if not os.path.exists("encodings.pickle"):
        return names, encodings

    with open("encodings.pickle", "rb") as f:
        while True:
            try:
                name, encoding = pickle.load(f)
                names.append(name)
                encodings.append(encoding)
            except EOFError:
                break
    return names, encodings


def mark_attendance(name):
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (
                        name TEXT,
                        date TEXT,
                        time TEXT
                      )''')

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    # Prevent duplicate entry for the same person on the same day
    cursor.execute(
        "SELECT * FROM attendance WHERE name=? AND date=?", (name, date))
    entry = cursor.fetchone()

    if entry is None:
        cursor.execute("INSERT INTO attendance VALUES (?, ?, ?)",
                       (name, date, time))
        print(f"🟢 Attendance marked for {name} at {time}")
        conn.commit()
    else:
        print(f"ℹ️ {name} is already marked present today.")

    conn.close()


def view_attendance():
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (
                        name TEXT,
                        date TEXT,
                        time TEXT
                      )''')

    # Get all attendance records
    cursor.execute("SELECT * FROM attendance ORDER BY date DESC, time DESC")
    records = cursor.fetchall()

    if not records:
        print("\nNo attendance records found.")
    else:
        # Format the data for tabulate
        headers = ["Name", "Date", "Time"]
        print("\nAttendance Records:")
        print(tabulate(records, headers=headers, tablefmt="grid"))

    conn.close()
    input("\nPress Enter to continue...")
