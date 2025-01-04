import tkinter as tk
from recorder import AudioRecorder
from transcriber import AudioTranscriber


def start_recording():
    recorder.start_recording()
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    transcribe_button.config(state=tk.DISABLED)


def stop_recording():
    recorder.stop_recording()
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    transcribe_button.config(state=tk.NORMAL)


def transcribe_audio():
    transcriber.transcribe_audio(recorder.filepath)


recorder = AudioRecorder()
transcriber = AudioTranscriber()

root = tk.Tk()
root.title("Audio Recorder")
root.geometry("300x300")
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
