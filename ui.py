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
from tkinter import filedialog, TclError
from recorder import AudioRecorder
from transcriber import AudioTranscriber
from emotion_analyzer import EmotionAnalyzer
from text_processor import TextProcessor
from text_analyzer import TextAnalyzer
import logging
import warnings
import os
from tkinterdnd2 import TkinterDnD, DND_FILES
# Suppress FP16 warning
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

class TextBoxLogHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.config(state=tk.DISABLED)
        self.text_widget.see(tk.END)

# Set default save directory to the current working directory
save_directory = os.getcwd()
logging.info(f"Default save directory set to: {save_directory}")
class DropZone(tk.Label):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(relief="groove", borderwidth=2)
        
        # Enable drag and drop for files
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.handle_drop)
        
    def handle_drop(self, event):
        # Get the dropped file path and handle it
        file_path = event.data
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
        handle_dropped_file(file_path)

def handle_dropped_file(file_path):
    if not os.path.exists(file_path):
        error_msg = f"File not found: {file_path}"
        logging.error(error_msg)
        transcription_box.delete(1.0, tk.END)
        transcription_box.insert(tk.END, f"Error: {error_msg}")
        return
        
    # Check if it's an audio file
    valid_extensions = ('.wav', '.mp3', '.m4a', '.flac')
    if not file_path.lower().endswith(valid_extensions):
        error_msg = "Invalid file type. Please drop an audio file."
        logging.error(error_msg)
        transcription_box.delete(1.0, tk.END)
        transcription_box.insert(tk.END, f"Error: {error_msg}")
        return
        
    try:
        # Update the UI to show file is being processed
        transcription_box.delete(1.0, tk.END)
        transcription_box.insert(tk.END, "Processing dropped file...\n")
        root.update()
        
        # Set the filepath in the recorder
        recorder.filepath = file_path
        
        # Enable relevant buttons
        transcribe_button.config(state=tk.NORMAL)
        rename_audio_button.config(state=tk.NORMAL)
        
        # Automatically start transcription
        transcribe_audio()
        
    except Exception as e:
        error_msg = f"Error processing dropped file: {str(e)}"
        logging.error(error_msg)
        transcription_box.delete(1.0, tk.END)
        transcription_box.insert(tk.END, f"Error: {error_msg}")

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
        analyze_button.config(state=tk.DISABLED)  # Disable emotion analysis button

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
    analyze_button.config(state=tk.NORMAL)  # Enable emotion analysis after transcription

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

    analyze_button.config(state=tk.NORMAL)  # Enable emotion analysis after transcription
    logging.info("Transcription displayed in the UI.")


def analyze_emotions(event=None):
    if not recorder.filepath or not os.path.exists(recorder.filepath):
        logging.warning("No audio file available for emotion analysis.")
        transcription_box.insert(tk.END, "\nNo audio file available for emotion analysis.")
        return
    
    try:
        # Get the current transcription text
        current_text = transcription_box.get("1.0", tk.END).strip()
        if not current_text:
            logging.warning("No transcription available for emotion analysis.")
            return
            
        # Remove the "Transcription:" prefix if it exists
        if current_text.startswith("Transcription:"):
            current_text = current_text.replace("Transcription:", "", 1).strip()
            
        # Perform emotion analysis
        emotion_analysis = emotion_analyzer.analyze(current_text, recorder.filepath)
        
        # Save emotion analysis
        if save_directory:
            emotion_path = os.path.join(save_directory, "emotion_analysis.txt")
        else:
            emotion_path = "emotion_analysis.txt"
            
        with open(emotion_path, "w", encoding="utf-8") as f:
            f.write(f"Emotion Analysis:\n{emotion_analysis}")
        
        # Display in UI
        transcription_box.insert(tk.END, "\n\nEmotion Analysis:\n" + emotion_analysis)
        logging.info(f"Emotion analysis completed and saved to {emotion_path}")
        
    except Exception as e:
        logging.error(f"Error during emotion analysis: {e}")
        transcription_box.insert(tk.END, f"\nError during emotion analysis: {e}")
        
def analyze_text_content(event=None):
    """Analyze the transcribed text for key topics and entities."""    
    try:
        # Get text from transcription text widget
        text = transcription_box.get("1.0", tk.END).strip()
        if not text:
            logging.error("No text to analyze")
            return
            
        # Perform analysis
        analysis_results = text_analyzer.analyze_text(text)
        formatted_results = text_analyzer.format_analysis_results(analysis_results)
        
        # Show results in a new window
        analysis_window = tk.Toplevel(root)
        analysis_window.title("Text Analysis")
        analysis_window.geometry("600x600")
        
        # Create text widget with scrollbar
        analysis_text = tk.Text(analysis_window, wrap=tk.WORD, height=30, width=70)
        scrollbar = tk.Scrollbar(analysis_window, command=analysis_text.yview)
        analysis_text.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        analysis_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10, padx=(0, 10))
        
        # Insert analysis results
        analysis_text.insert("1.0", formatted_results)
        analysis_text.config(state=tk.DISABLED)
        
    except Exception as e:
        logging.error(f"Error during text analysis: {e}")

def set_api_key(event=None):
    api_key = simpledialog.askstring("API Key", "Enter your Gemini API Key:", show='*')
    if api_key:
        success = text_processor.set_api_key(api_key)
        if success:
            logging.info("API key set successfully")
        else:
            logging.error("Failed to initialize with provided API key")

def summarize_text(event=None):
    if not text_processor.model:
        logging.error("Please set Gemini API key first")
        return
        
    try:
        # Get text from transcription text widget
        text = transcription_box.get("1.0", tk.END).strip()
        if not text:
            logging.error("No text to summarize")
            return
            
        summary = text_processor.summarize_text(text)
        
        # Show summary in a new window
        summary_window = tk.Toplevel(root)
        summary_window.title("Summary")
        summary_window.geometry("600x400")
        
        summary_text = tk.Text(summary_window, wrap=tk.WORD, height=15, width=60)
        summary_text.pack(padx=10, pady=10, expand=True, fill='both')
        summary_text.insert("1.0", summary)
        summary_text.config(state=tk.DISABLED)
        
    except Exception as e:
        logging.error(f"Error generating summary: {e}")

def query_text(event=None):
    if not text_processor.model:
        logging.error("Please set Gemini API key first")
        return
        
    try:
        # Get text from transcription text widget
        text = transcription_box.get("1.0", tk.END).strip()
        if not text:
            logging.error("No text to query")
            return
            
        # Get query from user
        query = simpledialog.askstring("Query", "Enter your question about the text:")
        if not query:
            return
            
        answer = text_processor.query_text(text, query)
        
        # Show answer in a new window
        answer_window = tk.Toplevel(root)
        answer_window.title("Answer")
        answer_window.geometry("600x400")
        
        answer_text = tk.Text(answer_window, wrap=tk.WORD, height=15, width=60)
        answer_text.pack(padx=10, pady=10, expand=True, fill='both')
        answer_text.insert("1.0", answer)
        answer_text.config(state=tk.DISABLED)
        
    except Exception as e:
        logging.error(f"Error processing query: {e}")

recorder = AudioRecorder()
transcriber = AudioTranscriber()
emotion_analyzer = EmotionAnalyzer()
text_processor = TextProcessor()  # Will automatically load API key from .env if available

text_analyzer = TextAnalyzer()
root = TkinterDnD.Tk()

root.title("Audio Recorder & Emotion Analyzer")
root.geometry("500x900")
root.configure(bg="#2b2b2b")
# root.tk.eval('package require tkdnd')
# Bind hotkeys
root.bind("<d>", browse_directory)
root.bind("<s>", start_recording)
root.bind("<x>", stop_recording)
root.bind("<t>", transcribe_audio)

root.bind("<r>", rename_audio_file)
root.bind("<y>", rename_transcription_file)
root.bind("<e>", analyze_emotions)


# Create frames for better organization
button_frame = tk.Frame(root, bg="#2b2b2b")
button_frame.pack(fill=tk.X, padx=10, pady=5)

# Create log box
log_box = tk.Text(button_frame, height=8, width=60, wrap=tk.WORD, state=tk.DISABLED, bg="#333333", fg="white", font=("Helvetica", 10))
log_box.pack(pady=5)

# Configure logging to display in the log box
log_handler = TextBoxLogHandler(log_box)
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(log_handler)
logging.getLogger().setLevel(logging.DEBUG)
drop_zone = DropZone(
    root,
    text="Drag and drop audio files here\nor use the buttons below",
    bg="#333333",
    fg="white",
    font=("Helvetica", 12),
    width=40,
    height=3
)
drop_zone.pack(fill=tk.X, padx=10, pady=5)
root.tk.eval(f'tkdnd::drop_target register {drop_zone.winfo_pathname(drop_zone.winfo_id())} *')
root.tk.eval(f'tkdnd::drop_target register {root.winfo_pathname(root.winfo_id())} *')

button_style = {
    "font": ("Helvetica", 12, "bold"),
    "bg": "#4caf50",
    "fg": "white",
    "activebackground": "#45a049",
    "activeforeground": "white",
    "relief": tk.RAISED,
    "bd": 3,
    "width": 20,
    "height": 1, 
}

browse_button = tk.Button(
    button_frame, text="Browse Directory (D)", command=browse_directory, **button_style
)
browse_button.pack(pady=3)

start_button = tk.Button(
    button_frame, text="Start Recording (S)", command=start_recording, **button_style
)
start_button.pack(pady=3)

stop_button = tk.Button(
    button_frame,
    text="Stop Recording (X)",
    command=stop_recording,
    state=tk.DISABLED,
    **button_style
)
stop_button.pack(pady=3)

rename_audio_button = tk.Button(
    button_frame,
    text="Rename Audio (R)",
    command=rename_audio_file,
    state=tk.DISABLED,
    **button_style
)
rename_audio_button.pack(pady=3)

rename_transcription_button = tk.Button(
    button_frame,
    text="Rename Transcription (Y)",
    command=rename_transcription_file,
    state=tk.DISABLED,
    **button_style
)
rename_transcription_button.pack(pady=3)

transcribe_button = tk.Button(
    button_frame, text="Transcribe (T)", command=transcribe_audio, state=tk.DISABLED, **button_style
)
transcribe_button.pack(pady=3)

analyze_button = tk.Button(
    button_frame, text="Analyze Emotions (E)", command=analyze_emotions, state=tk.DISABLED, **button_style
)
analyze_button.pack(pady=3)

analyze_text_button = tk.Button(button_frame, text="Analyze Text", command=analyze_text_content)
analyze_text_button.pack(side=tk.LEFT, padx=5)

api_key_button = tk.Button(button_frame, text="Set API Key", command=set_api_key)
api_key_button.pack(side=tk.LEFT, padx=5)

summarize_button = tk.Button(button_frame, text="Summarize", command=summarize_text)
summarize_button.pack(side=tk.LEFT, padx=5)

query_button = tk.Button(button_frame, text="Ask Question", command=query_text)
query_button.pack(side=tk.LEFT, padx=5)

# Create a frame for transcription
transcription_frame = tk.Frame(root, bg="#2b2b2b")
transcription_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

# Transcription Label
transcription_label = tk.Label(
    transcription_frame,
    text="Transcription and Analysis",
    bg="#2b2b2b",
    fg="white",
    font=("Helvetica", 12, "bold")
)
transcription_label.pack(pady=5)

# Create a frame for the text box and scrollbar
text_container = tk.Frame(transcription_frame, bg="#2b2b2b")
text_container.pack(fill=tk.BOTH, expand=True)

# Add scrollbar
scrollbar = tk.Scrollbar(text_container)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Transcription Box
transcription_box = tk.Text(
    text_container,
    height=12,
    width=50,
    wrap=tk.WORD,
    bg="#333333",
    fg="white",
    font=("Helvetica", 11),
    yscrollcommand=scrollbar.set
)
transcription_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.config(command=transcription_box.yview)
def setup_tkdnd():
    try:
        root.tk.eval('package require tkdnd')
        root.tk.call('tkdnd::drop_target', 'register', root, ('DND_Files', 'Files'))
        logging.info("TkDND initialized successfully")
    except tk.TclError as e:
        logging.error(f"Failed to initialize TkDND: {e}")
        # Create a label to show error
        tk.Label(
            root,
            text="Drag and drop not available.\nPlease install python-tkdnd package.",
            bg="#ff6b6b",
            fg="white",
            font=("Helvetica", 10)
        ).pack(fill=tk.X, padx=10, pady=5)

setup_tkdnd()
# Add hotkey label at the bottom
hotkey_label = tk.Label(
    root,
    text="Hotkeys:\nD - Select Directory | S - Start Recording | X - Stop Recording\nT - Transcribe | R - Rename Audio | Y - Rename Transcription | E - Analyze Emotions",
    bg="#2b2b2b",
    fg="white",
    font=("Helvetica", 10),
)
hotkey_label.pack(pady=5)

root.mainloop()