import tkinter as tk
from recorder import AudioRecorder
from transcriber import AudioTranscriber
import logging
import warnings

warnings.filterwarnings("ignore", message = "FP16 is not supported on CPU; using FP32 instead")

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


def start_recording(self, event=None):
    recorder.start_recording()
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    transcribe_button.config(state=tk.DISABLED)
    logging.info("Start recording button clicked (Hotkey: 's')")


def stop_recording(self, event=None):
    recorder.stop_recording()
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    transcribe_button.config(state=tk.NORMAL)
    logging.info("Stop recording button clicked (Hotkey: 'x')")


def transcribe_audio(self, event=None):
    transcriber.transcribe_audio(recorder.filepath)
    logging.info("Transcribe button clicked (Hotkey: 't')")


recorder = AudioRecorder()
transcriber = AudioTranscriber()

root = tk.Tk()
root.title("Audio Recorder")
root.geometry("300x400")
root.configure(bg="#2b2b2b")

root.bind('<s>', start_recording)
root.bind('<x>', stop_recording)
root.bind('<t>', transcribe_audio)

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

hotkey_label = tk.Label(
    root,
    text="Hotkeys:\nS - Start\nX - Stop\nT - Transcribe",
    bg="#2b2b2b",
    fg="white",
    font=("Helvetica", 10)
)
hotkey_label.pack(pady=10)

root.mainloop()
