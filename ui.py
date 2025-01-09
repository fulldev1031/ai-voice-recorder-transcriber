import tkinter as tk
from tkinter import filedialog
from recorder import AudioRecorder
from transcriber import AudioTranscriber
import logging
import os

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Set default save directory to the current working directory
save_directory = os.getcwd()
logging.info(f"Default save directory set to: {save_directory}")

def browse_directory():
    global save_directory
    directory = filedialog.askdirectory(title="Select Directory")
    if directory:
        save_directory = directory
        logging.info(f"Save directory selected: {save_directory}")
    else:
        logging.info("No directory selected")

def start_recording():
    if not save_directory:
        logging.warning("Save directory is not set. Please select a directory first.")
        return  
    recorder.set_save_directory(save_directory)
    recorder.start_recording()
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    transcribe_button.config(state=tk.DISABLED)
    logging.info("Start recording button clicked")
def stop_recording():
    recorder.stop_recording()
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    transcribe_button.config(state=tk.NORMAL)
    logging.info("Stop recording button clicked")

def transcribe_audio():
    if not recorder.filepath:
        logging.warning("No audio file available for transcription.")
        return
    transcriber.transcribe_audio(recorder.filepath, save_directory)
    logging.info("Transcribe button clicked")

recorder = AudioRecorder()
transcriber = AudioTranscriber()
root = tk.Tk()
root.title("Audio Recorder")
root.geometry("300x400")  # i increased height to fit new browse button
root.configure(bg="#2b2b2b")
button_style = {
    "font": ("Helvetica", 12, "bold"),
    "bg": "#4caf50",
    "fg": "white",
    "activebackground": "#45a049",
    "activeforeground": "white",
    "relief": tk.RAISED,
    "bd": 3,
    "width": 20,
    "height": 2,
}
browse_button = tk.Button(
    root, text="Browse Directory", command=browse_directory, **button_style
)
browse_button.pack(pady=20)
start_button = tk.Button(
    root, text="Start Recording", command=start_recording, **button_style
)
start_button.pack(pady=20)
stop_button = tk.Button(
    root,
    text="Stop Recording",
    command=stop_recording,
    state=tk.DISABLED,
    **button_style
)
stop_button.pack(pady=20)
transcribe_button = tk.Button(
    root, text="Transcribe", command=transcribe_audio, state=tk.DISABLED, **button_style
)
transcribe_button.pack(pady=20)
root.mainloop()

