import warnings
import torch
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from recorder import AudioRecorder
from transcriber import AudioTranscriber
from emotion_analyzer import EmotionAnalyzer
import logging
import os
import sys
from typing import Optional

# Suppress specific warnings
warnings.filterwarnings("ignore", message="You are using `torch.load` with `weights_only=False`.*")
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

class AudioRecorderUI:
    def __init__(self):
        self.setup_logging()
        self.save_directory: Optional[str] = None
        self.setup_components()
        self.initialize_ui()
        
    def setup_logging(self):
        """Initialize logging configuration with error handling"""
        try:
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler("audio_recorder.log"),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        except Exception as e:
            print(f"Failed to initialize logging: {e}")
            sys.exit(1)

    def setup_components(self):
        """Initialize recorder, transcriber and analyzer with error handling"""
        try:
            self.recorder = AudioRecorder()
            self.transcriber = AudioTranscriber()
            self.emotion_analyzer = EmotionAnalyzer()
            self.save_directory = os.getcwd()
            logging.info(f"Default save directory set to: {self.save_directory}")
        except Exception as e:
            self.show_error("Component Initialization Error", f"Failed to initialize components: {e}")
            sys.exit(1)

    def show_error(self, title: str, message: str):
        """Display error message to user"""
        messagebox.showerror(title, message)
        logging.error(message)

    def show_info(self, title: str, message: str):
        """Display info message to user"""
        messagebox.showinfo(title, message)
        logging.info(message)

    def browse_directory(self, event=None):
        """Handle directory selection with error checking"""
        try:
            directory = filedialog.askdirectory(title="Select Directory")
            if directory:
                if not os.access(directory, os.W_OK):
                    raise PermissionError(f"No write permission for directory: {directory}")
                self.save_directory = directory
                self.recorder.set_save_directory(directory)
                self.show_info("Directory Selected", f"Save directory set to: {directory}")
            else:
                logging.info(f"No directory selected. Using current: {self.save_directory}")
        except Exception as e:
            self.show_error("Directory Selection Error", str(e))

    def start_recording(self, event=None):
        """Handle recording start with error checking"""
        if not self.save_directory:
            self.show_error("Configuration Error", "Save directory not set")
            return

        try:
            self.recorder.start_recording()
            self.update_button_states(recording=True)
            self.transcription_box.delete(1.0, tk.END)
            logging.info("Recording started successfully")
        except Exception as e:
            self.show_error("Recording Error", f"Failed to start recording: {e}")
            self.update_button_states(recording=False)

    def stop_recording(self, event=None):
        """Handle recording stop with error checking"""
        try:
            self.recorder.stop_recording()
            self.update_button_states(recording=False)
            self.rename_audio_button.config(state=tk.NORMAL)
            logging.info("Recording stopped successfully")
        except Exception as e:
            self.show_error("Recording Error", f"Failed to stop recording: {e}")
            self.update_button_states(recording=False)

    def rename_audio_file(self, event=None):
        """Handle audio file renaming"""
        if not self.recorder.filepath:
            logging.warning("No audio file available to rename.")
            return
        
        new_name = simpledialog.askstring("Rename Audio File", "Enter new filename (without extension):")
        if new_name:
            if self.recorder.rename_audio(new_name):
                logging.info(f"Audio file renamed successfully to {new_name}.wav")
            else:
                logging.error("Failed to rename audio file")

    def rename_transcription_file(self, event=None):
        """Handle transcription file renaming"""
        if not hasattr(self.transcriber, 'transcription_file') or not self.transcriber.transcription_file:
            logging.warning("No transcription file available to rename.")
            return
        
        new_name = simpledialog.askstring("Rename Transcription File", "Enter new filename (without extension):")
        if new_name:
            if self.transcriber.rename_transcription(new_name):
                logging.info(f"Transcription file renamed successfully to {new_name}_transcription.txt")
            else:
                logging.error("Failed to rename transcription file")

    def transcribe_audio(self, event=None):
        """Handle audio transcription with error checking"""
        try:
            if not hasattr(self.recorder, 'filepath') or not self.recorder.filepath:
                raise ValueError("No audio file available for transcription")
            
            if not os.path.exists(self.recorder.filepath):
                raise FileNotFoundError(f"Audio file not found: {self.recorder.filepath}")

            self.transcribe_button.config(state=tk.DISABLED)
            self.root.update()

            transcription = self.transcriber.transcribe_audio(
                self.recorder.filepath, self.save_directory
            )
            
            if transcription.startswith("Error:"):
                raise RuntimeError(transcription)

            # Save transcription and update UI
            if self.transcriber.save_transcription(transcription, self.save_directory):
                self.rename_transcription_button.config(state=tk.NORMAL)
            
            self.update_transcription_box(transcription)
            self.analyze_button.config(state=tk.NORMAL)
            logging.info("Transcription completed successfully")

        except Exception as e:
            self.show_error("Transcription Error", str(e))
        finally:
            self.transcribe_button.config(state=tk.NORMAL)

    def analyze_emotions(self, event=None):
        """Handle emotion analysis with error checking"""
        try:
            if not self.recorder.filepath or not os.path.exists(self.recorder.filepath):
                raise ValueError("No audio file available for emotion analysis")
            
            current_text = self.transcription_box.get("1.0", tk.END).strip()
            if not current_text:
                raise ValueError("No transcription available for emotion analysis")
                
            if current_text.startswith("Transcription:"):
                current_text = current_text.replace("Transcription:", "", 1).strip()
                
            emotion_analysis = self.emotion_analyzer.analyze(current_text, self.recorder.filepath)
            
            # Save emotion analysis
            emotion_path = os.path.join(self.save_directory, "emotion_analysis.txt")
            with open(emotion_path, "w", encoding="utf-8") as f:
                f.write(f"Emotion Analysis:\n{emotion_analysis}")
            
            self.transcription_box.insert(tk.END, "\n\nEmotion Analysis:\n" + emotion_analysis)
            logging.info(f"Emotion analysis completed and saved to {emotion_path}")
            
        except Exception as e:
            self.show_error("Emotion Analysis Error", str(e))

    def update_button_states(self, recording: bool):
        """Update UI button states safely"""
        try:
            self.start_button.config(state=tk.DISABLED if recording else tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL if recording else tk.DISABLED)
            self.transcribe_button.config(state=tk.DISABLED if recording else tk.NORMAL)
            self.browse_button.config(state=tk.DISABLED if recording else tk.NORMAL)
            self.rename_audio_button.config(state=tk.DISABLED if recording else tk.DISABLED)
            self.rename_transcription_button.config(state=tk.DISABLED)
            self.analyze_button.config(state=tk.DISABLED)
        except Exception as e:
            logging.error(f"Failed to update button states: {e}")

    def update_transcription_box(self, text: str):
        """Update transcription box safely"""
        try:
            self.transcription_box.delete(1.0, tk.END)
            self.transcription_box.insert(tk.END, text)
        except Exception as e:
            logging.error(f"Failed to update transcription box: {e}")

    def initialize_ui(self):
        """Initialize UI components with error handling"""
        try:
            self.root = tk.Tk()
            self.root.title("Audio Recorder & Emotion Analyzer")
            self.root.geometry("500x900")
            self.root.configure(bg="#2b2b2b")

            self.setup_bindings()
            self.create_ui_elements()
            
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            self.root.mainloop()
        except Exception as e:
            self.show_error("UI Initialization Error", f"Failed to initialize UI: {e}")
            sys.exit(1)

    def setup_bindings(self):
        """Set up keyboard bindings safely"""
        try:
            self.root.bind("<d>", self.browse_directory)
            self.root.bind("<s>", self.start_recording)
            self.root.bind("<x>", self.stop_recording)
            self.root.bind("<t>", self.transcribe_audio)
            self.root.bind("<r>", self.rename_audio_file)
            self.root.bind("<y>", self.rename_transcription_file)
            self.root.bind("<e>", self.analyze_emotions)
        except Exception as e:
            logging.error(f"Failed to set up keyboard bindings: {e}")

    def create_ui_elements(self):
        """Create UI elements with error handling"""
        try:
            self.create_log_box()
            self.create_buttons()
            self.create_transcription_box()
            self.create_hotkey_label()
        except Exception as e:
            self.show_error("UI Creation Error", f"Failed to create UI elements: {e}")
            sys.exit(1)

    def on_closing(self):
        """Handle application shutdown"""
        try:
            if hasattr(self, 'recorder') and self.recorder.recording:
                self.recorder.stop_recording()
            self.root.destroy()
        except Exception as e:
            logging.error(f"Error during shutdown: {e}")
            self.root.destroy()

    def create_log_box(self):
        """Create log box with error handling"""
        try:
            self.log_box = tk.Text(
                self.root,
                height=10,
                width=60,
                wrap=tk.WORD,
                state=tk.DISABLED,
                bg="#333333",
                fg="white",
                font=("Helvetica", 10)
            )
            self.log_box.pack(pady=10)
            
            log_handler = TextBoxLogHandler(self.log_box)
            log_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            )
            logging.getLogger().addHandler(log_handler)
        except Exception as e:
            logging.error(f"Failed to create log box: {e}")
            raise

    def create_buttons(self):
        """Create UI buttons with error handling"""
        try:
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

            self.browse_button = tk.Button(
                self.root,
                text="Browse Directory",
                command=self.browse_directory,
                **button_style
            )
            self.browse_button.pack(pady=10)

            self.start_button = tk.Button(
                self.root,
                text="Start Recording",
                command=self.start_recording,
                **button_style
            )
            self.start_button.pack(pady=10)

            self.stop_button = tk.Button(
                self.root,
                text="Stop Recording",
                command=self.stop_recording,
                state=tk.DISABLED,
                **button_style
            )
            self.stop_button.pack(pady=10)

            self.rename_audio_button = tk.Button(
                self.root,
                text="Rename Audio (R)",
                command=self.rename_audio_file,
                state=tk.DISABLED,
                **button_style
            )
            self.rename_audio_button.pack(pady=5)

            self.rename_transcription_button = tk.Button(
                self.root,
                text="Rename Transcription (Y)",
                command=self.rename_transcription_file,
                state=tk.DISABLED,
                **button_style
            )
            self.rename_transcription_button.pack(pady=5)

            self.transcribe_button = tk.Button(
                self.root,
                text="Transcribe (T)",
                command=self.transcribe_audio,
                state=tk.DISABLED,
                **button_style
            )
            self.transcribe_button.pack(pady=5)

            self.analyze_button = tk.Button(
                self.root,
                text="Analyze Emotions (E)",
                command=self.analyze_emotions,
                state=tk.DISABLED,
                **button_style
            )
            self.analyze_button.pack(pady=10)
        except Exception as e:
            logging.error(f"Failed to create buttons: {e}")
            raise

    def create_transcription_box(self):
        """Create transcription box with error handling"""
        try:
            self.transcription_box = tk.Text(
                self.root,
                height=15,
                width=50,
                wrap=tk.WORD
            )
            self.transcription_box.pack(pady=10)
        except Exception as e:
            logging.error(f"Failed to create transcription box: {e}")
            raise

    def create_hotkey_label(self):
        """Create hotkey label with error handling"""
        try:
            self.hotkey_label = tk.Label(
                self.root,
                text="Hotkeys:\nD - Select Directory\nS - Start Recording\n"
                     "X - Stop Recording\nT - Transcribe\nR - Rename Audio\n"
                     "Y - Rename Transcription\nE - Analyze Emotions",
                bg="#2b2b2b",
                fg="white",
                font=("Helvetica", 10)
            )
            self.hotkey_label.pack(pady=10)
        except Exception as e:
            logging.error(f"Failed to create hotkey label: {e}")
            raise

class TextBoxLogHandler(logging.Handler):
    """Custom log handler for displaying logs in the UI"""
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

def emit(self, record):
    try:
        msg = self.format(record)
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.config(state=tk.DISABLED)
        self.text_widget.see(tk.END)
    except Exception as e:
        print(f"Error in log handler: {e}")

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

def analyze_emotions(event=None):
    if not recorder.filepath or not os.path.exists(recorder.filepath):
        logging.warning("No audio file available for emotion analysis.")
        transcription_box.insert(tk.END, "\nNo audio file available for emotion analysis.")
        return

try:
    app = AudioRecorderUI()
except Exception as e:
    print(f"Fatal error: {e}")
    sys.exit(1)

recorder = AudioRecorder()
transcriber = AudioTranscriber()
emotion_analyzer = EmotionAnalyzer()
root = tk.Tk()
root.title("Audio Recorder & Emotion Analyzer")
root.geometry("500x900")
root.configure(bg="#2b2b2b")

# Configure logging to display in the log box
log_box = tk.Text(root, height=10, width=60, wrap=tk.WORD, state=tk.DISABLED, bg="#333333", fg="white", font=("Helvetica", 10))
log_box.pack(pady=10)

log_handler = TextBoxLogHandler(log_box)
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(log_handler)
logging.getLogger().setLevel(logging.DEBUG)

# Other UI elements (buttons, labels, etc.) can be added here as needed.

root.mainloop()

