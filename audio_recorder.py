import tkinter as tk
from tkinter import ttk
import pyaudio
import threading
import time
import wave
import whisper

# Initialize Whisper model with error handling
try:
    model = whisper.load_model("small")
except Exception as e:
    print(f"Error loading Whisper model: {e}")
    model = None

# Audio recording settings
rate = 16000
chunk_size = 1024
channels = 1
frames = []
recording = False
audio_file = "recorded_audio.wav"
transcription_file = "transcription.txt"

# Function to start recording
def start_recording():
    global recording, frames
    frames = []
    recording = True

    progress_bar['value'] = 0
    duration = int(duration_spinbox.get())

    # Create PyAudio object
    try:
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=channels,
                        rate=rate, input=True, frames_per_buffer=chunk_size)
    except Exception as e:
        print(f"Error initializing microphone: {e}")
        return

    # Timer to stop recording after duration
    def stop_timer():
        time.sleep(duration)
        stop_recording()

    threading.Thread(target=stop_timer, daemon=True).start()

    # Start recording audio
    def record_audio():
        nonlocal stream
        while recording:
            try:
                data = stream.read(chunk_size)
                frames.append(data)
                progress = min(100, len(frames) / (rate / chunk_size * duration) * 100)
                progress_bar['value'] = progress
                root.after(10, lambda: progress_bar.update_idletasks())
            except Exception as e:
                print(f"Error reading audio: {e}")
                break

        # Save audio to file
        try:
            with wave.open(audio_file, 'wb') as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
                wf.setframerate(rate)
                wf.writeframes(b''.join(frames))
        except Exception as e:
            print(f"Error saving audio file: {e}")
        
        stream.stop_stream()
        stream.close()
        p.terminate()

    threading.Thread(target=record_audio, daemon=True).start()

# Function to stop recording
def stop_recording():
    global recording
    recording = False

# Function to transcribe audio
def transcribe_audio():
    if model is None:
        transcription_box.insert(tk.END, "Whisper model not loaded.\n")
        return

    try:
        result = model.transcribe(audio_file)
        transcription_text = result['text']

        with open(transcription_file, 'w') as f:
            f.write(transcription_text)

        transcription_box.delete(1.0, tk.END)
        transcription_box.insert(tk.END, transcription_text)
    except Exception as e:
        transcription_box.insert(tk.END, f"Error transcribing audio: {e}\n")

# Set up the Tkinter window
root = tk.Tk()
root.title("Audio Recorder")

# UI Elements
record_button = tk.Button(root, text="Start Recording", command=start_recording)
record_button.pack(pady=10)

stop_button = tk.Button(root, text="Stop Recording", command=stop_recording)
stop_button.pack(pady=10)

transcribe_button = tk.Button(root, text="Transcribe Audio", command=transcribe_audio)
transcribe_button.pack(pady=10)

transcription_box = tk.Text(root, height=10, width=50)
transcription_box.pack(pady=10)

duration_label = tk.Label(root, text="Recording Duration (seconds):")
duration_label.pack(pady=5)

duration_spinbox = tk.Spinbox(root, from_=1, to_=300, width=5)
duration_spinbox.pack(pady=5)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10)

root.mainloop()
