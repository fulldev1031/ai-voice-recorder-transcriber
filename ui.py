import warnings
import torch
from tkinter import simpledialog

# Suppress specific warning
warnings.filterwarnings(
    "ignore",
    message=(
        "You are using `torch.load` with `weights_only=False`.*"
    ),
)

import tkinter as tk
from tkinter import filedialog
from recorder import AudioRecorder
from transcriber import AudioTranscriber
import logging
import warnings
import os

# Suppress FP16 warning
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Custom log handler to display logs in the UI
class TextBoxLogHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.config(state=tk.DISABLED)
        self.text_widget.see(tk.END)  # Auto-scroll to the latest log

# Set default save directory to the current working directory
save_directory = os.getcwd()
logging.info(f"Default save directory set to: {save_directory}")

def browse_directory(event=None):
    global save_directory
    directory = filedialog.askdirectory(title="Select Directory")
    if directory:
        save_directory = directory
        logging.info(f"Save directory selected: {save_directory}")
    else:
        logging.info(f"No directory selected. Using default: {save_directory}")

def start_recording(event=None):
    if not save_directory:
        logging.warning("Save directory is not set. Please select a directory first.")
        return
    
    recorder.set_save_directory(save_directory)
    try:
        recorder.start_recording()
        start_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.NORMAL)
        transcribe_button.config(state=tk.DISABLED)
        rename_audio_button.config(state=tk.DISABLED)
        rename_transcription_button.config(state=tk.DISABLED)
        transcription_box.delete(1.0, tk.END)  # Clear previous transcription
        logging.info("Start recording button clicked")
    except RuntimeError as e:
        logging.error(e)
        log_box.config(state=tk.NORMAL)
        log_box.insert(tk.END, f"Error: {e}\n")
        log_box.config(state=tk.DISABLED)

def stop_recording(event=None):
    recorder.stop_recording()
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    transcribe_button.config(state=tk.NORMAL)
    rename_audio_button.config(state=tk.NORMAL)
    logging.info("Stop recording button clicked")

def transcribe_audio(event=None):
    if not recorder.filepath:
        logging.warning("No audio file available for transcription.")
        transcription_box.insert(tk.END, "No audio file available for transcription.\n")
        return
    
    # Clear previous transcription
    transcription_box.delete(1.0, tk.END)
    
    # Get transcription
    transcription = transcriber.transcribe_audio(recorder.filepath, save_directory)
    
    # Check for errors and handle transcription
    if not transcription.startswith("Error:"):
        # Save transcription to file
        if transcriber.save_transcription(transcription, save_directory):
            # Enable rename button only if save was successful
            rename_transcription_button.config(state=tk.NORMAL)
        
        # Display transcription in text box
        transcription_box.delete(1.0, tk.END)  # Clear again to be safe
        transcription_box.insert(tk.END, transcription)
        logging.info("Transcription displayed in the UI.")
    else:
        # If there was an error, display it and disable rename button
        transcription_box.insert(tk.END, transcription)
        rename_transcription_button.config(state=tk.DISABLED)
        logging.error("Failed to transcribe audio")

def rename_audio_file(event=None):
    if not recorder.filepath:
        logging.warning("No audio file available to rename.")
        return
    
    new_name = simpledialog.askstring("Rename Audio File", "Enter new filename (without extension):")
    if new_name:
        if recorder.rename_audio(new_name):
            logging.info(f"Audio file renamed successfully to {new_name}.wav")
        else:
            logging.error("Failed to rename audio file")

def rename_transcription_file(event=None):
    if not transcriber.transcription_file:
        logging.warning("No transcription file available to rename.")
        return
    
    new_name = simpledialog.askstring("Rename Transcription File", "Enter new filename (without extension):")
    if new_name:
        if transcriber.rename_transcription(new_name):
            logging.info(f"Transcription file renamed successfully to {new_name}_transcription.txt")
        else:
            logging.error("Failed to rename transcription file")

recorder = AudioRecorder()
transcriber = AudioTranscriber()
root = tk.Tk()
root.title("Audio Recorder")
root.geometry("500x900")
root.configure(bg="#2b2b2b")

# Bind hotkeys
root.bind("<d>", browse_directory)
root.bind("<s>", start_recording)
root.bind("<x>", stop_recording)
root.bind("<t>", transcribe_audio)
root.bind("<r>", rename_audio_file)
root.bind("<y>", rename_transcription_file)

# Create log box
log_box = tk.Text(root, height=10, width=60, wrap=tk.WORD, state=tk.DISABLED, bg="#333333", fg="white", font=("Helvetica", 10))
log_box.pack(pady=10)

# Configure logging to display in the log box
log_handler = TextBoxLogHandler(log_box)
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(log_handler)
logging.getLogger().setLevel(logging.DEBUG)

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
browse_button.pack(pady=10)

start_button = tk.Button(
    root, text="Start Recording", command=start_recording, **button_style
)
start_button.pack(pady=10)

stop_button = tk.Button(
    root,
    text="Stop Recording",
    command=stop_recording,
    state=tk.DISABLED,
    **button_style
)
stop_button.pack(pady=10)

rename_audio_button = tk.Button(
    root,
    text="Rename Audio (R)",
    command=rename_audio_file,
    state=tk.DISABLED,
    **button_style
)
rename_audio_button.pack(pady=5)

rename_transcription_button = tk.Button(
    root,
    text="Rename Transcription (Y)",
    command=rename_transcription_file,
    state=tk.DISABLED,
    **button_style
)
rename_transcription_button.pack(pady=5)

transcribe_button = tk.Button(
    root, text="Transcribe (T)", command=transcribe_audio, state=tk.DISABLED, **button_style
)
transcribe_button.pack(pady=5)

# Transcription Box
transcription_box = tk.Text(root, height=15, width=50, wrap=tk.WORD)
transcription_box.pack(pady=10)

# Add hotkey label
hotkey_label = tk.Label(
    root,
    text="Hotkeys:\nD - Select Directory\nS - Start Recording\nX - Stop Recording\nT - Transcribe\nR - Rename Audio\nY - Rename Transcription",
    bg="#2b2b2b",
    fg="white",
    font=("Helvetica", 10),
)
hotkey_label.pack(pady=10)

root.mainloop()
