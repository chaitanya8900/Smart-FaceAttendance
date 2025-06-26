import tkinter as tk
from tkinter import messagebox, simpledialog
import subprocess
import os
import sqlite3
import pandas as pd


def register_face():
    subprocess.run(["python", "register.py"], shell=True)


def recognize_faces():
    subprocess.run(["python", "recognize.py"], shell=True)


def export_csv():
    if not os.path.exists("attendance.csv"):
        messagebox.showwarning("No Records", "No attendance data to export.")
        return

    df = pd.read_csv("attendance.csv", names=["Name", "Date", "Time"])
    top = tk.Toplevel(root)
    top.title("Attendance Records")
    text = tk.Text(top, wrap=tk.NONE)
    text.insert(tk.END, df.to_string(index=False))
    text.pack(expand=True, fill='both')


def clear_all_attendance():
    confirm = messagebox.askyesno(
        "Confirm", "Are you sure you want to delete ALL attendance records?")
    if confirm:
        if os.path.exists("attendance.db"):
            conn = sqlite3.connect("attendance.db")
            cur = conn.cursor()
            cur.execute("DELETE FROM attendance")
            conn.commit()
            conn.close()

        if os.path.exists("attendance.csv"):
            with open("attendance.csv", "w") as f:
                f.truncate(0)

        messagebox.showinfo(
            "Cleared", "✅ All attendance records have been cleared.")


def clear_attendance_by_name_or_date():
    choice = simpledialog.askstring(
        "Clear Specific", "Type 'name' to delete by name or 'date' to delete by date:")

    if choice is None:
        return

    conn = sqlite3.connect("attendance.db")
    cur = conn.cursor()

    if choice.lower() == "name":
        name = simpledialog.askstring("Enter Name", "Enter the person's name:")
        if name:
            cur.execute("DELETE FROM attendance WHERE name=?", (name,))
            conn.commit()
            messagebox.showinfo(
                "Done", f"✅ Records for '{name}' have been cleared.")

    elif choice.lower() == "date":
        date = simpledialog.askstring(
            "Enter Date", "Enter date in YYYY-MM-DD format:")
        if date:
            cur.execute("DELETE FROM attendance WHERE date=?", (date,))
            conn.commit()
            messagebox.showinfo(
                "Done", f"✅ Records for date '{date}' have been cleared.")

    else:
        messagebox.showwarning("Invalid", "You must type 'name' or 'date'.")

    conn.close()


def exit_app():
    root.destroy()


# GUI Window
root = tk.Tk()
root.title("Smart Face Attendance System")
root.geometry("350x400")

tk.Label(root, text="Welcome!", font=("Arial", 16)).pack(pady=10)

tk.Button(root, text="Register Face",
          command=register_face, width=30).pack(pady=5)
tk.Button(root, text="Start Attendance",
          command=recognize_faces, width=30).pack(pady=5)
tk.Button(root, text="View Attendance (CSV)",
          command=export_csv, width=30).pack(pady=5)
tk.Button(root, text="Clear All Attendance",
          command=clear_all_attendance, width=30).pack(pady=5)
tk.Button(root, text="Exit", command=exit_app, width=30).pack(pady=20)

root.mainloop()
