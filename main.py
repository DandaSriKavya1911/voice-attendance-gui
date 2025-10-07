import tkinter as tk
from tkinter import messagebox
import pyttsx3
import speech_recognition as sr
import pandas as pd
from fuzzywuzzy import fuzz
from fpdf import FPDF
import threading
import time
import datetime

WAKE_WORDS = ["present", "yes", "here", "i am here", "yessir", "yep", "yup", "hai sir"]

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    time.sleep(0.3)

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.3)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=4)
            response = recognizer.recognize_google(audio)
            return response.lower()
        except Exception:
            return ""

def detect_wake_word(text):
    for word in WAKE_WORDS:
        if word in text or fuzz.partial_ratio(word, text) > 85:
            return True
    return False

def start_attendance():
    try:
        df = pd.read_csv("studentss.csv")
        df["status"] = "Absent"
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read studentss.csv\n{e}")
        return

    subject = subject_entry.get().strip()
    if not subject:
        messagebox.showwarning("Input Required", "Enter the subject name.")
        return

    date = datetime.date.today().strftime("%Y-%m-%d")
    status_label.config(text="🎤 Taking Attendance...", fg="blue")
    speak(f"Starting attendance for subject {subject}")

    for index, row in df.iterrows():
        roll = row["roll_no"]
        name = row["name"]
        status_label.config(text=f"🎧 Listening for Roll No. {roll} - {name}")
        speak(f"Roll number {roll}, {name}, are you present?")
        response = listen()
        if detect_wake_word(response):
            df.at[index, "status"] = "Present"
            speak("Marked present")
        else:
            speak("Marked absent")

    present = df[df["status"] == "Present"]
    absent = df[df["status"] == "Absent"]

    result_text = f"✅ Present: {len(present)}\n❌ Absent: {len(absent)}\n"
    if not absent.empty:
        result_text += "\n🚫 Absentees:\n"
        for _, row in absent.iterrows():
            result_text += f"{row['roll_no']} - {row['name']}\n"
    result_label.config(text=result_text)

    # Save PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Attendance Report for {subject} - {date}", ln=True, align='C')
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(40, 10, "Roll No.", 1)
    pdf.cell(80, 10, "Name", 1)
    pdf.cell(40, 10, "Status", 1)
    pdf.ln()
    pdf.set_font("Arial", '', 12)
    for _, row in df.iterrows():
        pdf.cell(40, 10, str(row["roll_no"]), 1)
        pdf.cell(80, 10, row["name"], 1)
        pdf.cell(40, 10, row["status"], 1)
        pdf.ln()
    filename = f"Attendance_{subject}_{date}.pdf".replace(" ", "_")
    pdf.output(filename)
    status_label.config(text=f"✅ Attendance saved as {filename}", fg="green")

def start_thread():
    threading.Thread(target=start_attendance).start()

# ----------------- GUI Layout -----------------
root = tk.Tk()
root.title("Voice Attendance System")
root.geometry("500x500")

tk.Label(root, text="🎓 Voice Attendance System", font=("Arial", 18)).pack(pady=10)

tk.Label(root, text="Enter Subject:").pack()
subject_entry = tk.Entry(root, font=("Arial", 12), width=30)
subject_entry.pack(pady=5)

start_btn = tk.Button(root, text="Start Attendance", font=("Arial", 12), bg="blue", fg="white", command=start_thread)
start_btn.pack(pady=10)

status_label = tk.Label(root, text="", font=("Arial", 12))
status_label.pack(pady=5)

result_label = tk.Label(root, text="", font=("Arial", 12), justify="left")
result_label.pack(pady=10)

root.mainloop()
