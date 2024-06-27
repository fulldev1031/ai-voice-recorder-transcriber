import tkinter as tk
import pyaudio
import wave
import threading
import whisper

class AudioRecorder:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.recording = False
        self.model = whisper.load_model("small")  #tiny, base, small, medium, and large

    def start_recording(self):
        self.frames = []
        self.stream = self.audio.open(format=pyaudio.paInt16,
                                      channels=1,
                                      rate=44100,
                                      input=True,
                                      frames_per_buffer=1024)
        self.recording = True
        self.thread = threading.Thread(target=self.record)
        self.thread.start()

    def record(self):
        while self.recording:
            data = self.stream.read(1024)
            self.frames.append(data)

    def stop_recording(self):
        self.recording = False
        self.thread.join()
        self.stream.stop_stream()
        self.stream.close()
        self.save_recording()

    def save_recording(self):
        self.filepath = "output.wav"
        wf = wave.open(self.filepath, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(self.frames))
        wf.close()

    def transcribe_audio(self):
        result = self.model.transcribe(self.filepath)
        with open("transcription.txt", "w") as f:
            f.write(result["text"])
        print("Transcription saved to transcription.txt")

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
    recorder.transcribe_audio()

recorder = AudioRecorder()

# Set up the main application window
root = tk.Tk()
root.title("Audio Recorder")
root.geometry("300x300")
root.configure(bg="#2b2b2b")  # Dark background color

# Style configuration
button_style = {
    "font": ("Helvetica", 12, "bold"),
    "bg": "#4caf50",  # Green background color
    "fg": "white",  # White text color
    "activebackground": "#45a049",  # Darker green on click
    "activeforeground": "white",
    "relief": tk.RAISED,
    "bd": 3,
    "width": 20,
    "height": 2
}

# Create and pack the buttons with padding
start_button = tk.Button(root, text="Start Recording", command=start_recording, **button_style)
start_button.pack(pady=20)

stop_button = tk.Button(root, text="Stop Recording", command=stop_recording, state=tk.DISABLED, **button_style)
stop_button.pack(pady=20)

transcribe_button = tk.Button(root, text="Transcribe", command=transcribe_audio, state=tk.DISABLED, **button_style)
transcribe_button.pack(pady=20)

# Run the Tkinter event loop
root.mainloop()
