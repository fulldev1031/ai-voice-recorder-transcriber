import warnings
import torch
import threading
from tkinter import simpledialog
from recorder import AudioRecorder
from tkinter import colorchooser
recorder = AudioRecorder()

# Suppress specific warning
warnings.filterwarnings(
    "ignore",
    message=(
        "You are using `torch.load` with `weights_only=False`.*"
    ),
)

import tkinter as tk
from tkinter import filedialog, TclError, messagebox, Toplevel, ttk
import threading
import time
from recorder import AudioRecorder
from transcriber import AudioTranscriber
from emotion_analyzer import EmotionAnalyzer
from text_processor import TextProcessor
from text_analyzer import TextAnalyzer
from transformers import MarianMTModel, MarianTokenizer , AutoTokenizer, AutoModelForSeq2SeqLM
import logging
import warnings
import os
from tkinterdnd2 import TkinterDnD, DND_FILES
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import pyaudio
import hashlib
import collections
import datetime
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import seaborn as sns
import json
import csv
# Suppress FP16 warning
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
dark_theme = {
    'bg': '#2b2b2b',
    'fg': 'white',
    'button_bg': '#4caf50',
    'button_fg': 'white',
    'text_bg': '#333333',
    'text_fg': 'white',
    'plot_bg': '#2b2b2b',
    'plot_fg': 'white',
    'waveform_color': '#4caf50',
    'axis_color': 'white',
    'grid_color': '#444444'
}

light_theme = {
    'bg': '#f0f0f0',
    'fg': 'black',
    'button_bg': '#4caf50',
    'button_fg': 'white',
    'text_bg': 'white',
    'text_fg': 'black',
    'plot_bg': 'white',
    'plot_fg': 'black',
    'waveform_color': '#4caf50',
    'axis_color': 'black',
    'grid_color': '#dddddd'
}

current_theme = dark_theme

def toggle_theme():
    global current_theme
    current_theme = light_theme if current_theme == dark_theme else dark_theme
    apply_theme(current_theme)

def apply_theme(theme):
    # Update root and main frames
    root.configure(bg=theme['bg'])
    main_frame.configure(bg=theme['bg'])
    button_container.configure(bg=theme['bg'])
    waveform_frame.configure(bg=theme['bg'])
    transcription_frame.configure(bg=theme['bg'])
    text_container.configure(bg=theme['bg'])
    
    # Update all buttons in button_container
    for widget in button_container.winfo_children():
        if isinstance(widget, tk.Button):
            widget.config(bg=theme['button_bg'], fg=theme['button_fg'])
    
    # Update text boxes
    log_box.config(bg=theme['text_bg'], fg=theme['text_fg'])
    transcription_box.config(bg=theme['text_bg'], fg=theme['text_fg'])
    
    # Update labels
    transcription_label.config(bg=theme['bg'], fg=theme['fg'])
    hotkey_label.config(bg=theme['bg'], fg=theme['fg'])
    
    # Update control_frame and its children
    control_frame.configure(bg=theme['bg'])
    for child in control_frame.winfo_children():
        if isinstance(child, tk.Label):
            child.config(bg=theme['bg'], fg=theme['fg'])
    
    # Update waveform visualizer
    visualizer.update_theme(theme)
    
    # Update seaborn style
    sns.set_style("darkgrid" if theme == dark_theme else "whitegrid")
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
def update_font_size(new_size):
    """Update font size for the transcription box"""
    current_font = transcription_box.cget("font")
    font_family = current_font[0] if isinstance(current_font, tuple) else "Helvetica"
    new_font = (font_family, new_size)
    transcription_box.config(font=new_font)
    logging.info(f"Font size updated to {new_size}")

def choose_color():
    """Open color picker and set text color"""
    color = colorchooser.askcolor(title="Choose Text Color")
    if color[1]:  # User selected a color
        transcription_box.config(fg=color[1])
        logging.info(f"Text color changed to {color[1]}")
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
        visualizer.start_recording()
        start_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.NORMAL)
        transcribe_button.config(state=tk.DISABLED)
        rename_audio_button.config(state=tk.DISABLED)
        rename_transcription_button.config(state=tk.DISABLED)
        analyze_button.config(state=tk.DISABLED)  # Disable emotion analysis button

        # threading.Thread(target = plot_waveform).start()

        transcription_box.delete(1.0, tk.END)  # Clear previous transcription
        logging.info("Start recording button clicked")
    except RuntimeError as e:
        logging.error(e)
        log_box.config(state=tk.NORMAL)
        log_box.insert(tk.END, f"Error: {e}\n")
        log_box.config(state=tk.DISABLED)

def stop_recording(event=None):
    recorder.stop_recording()
    visualizer.stop_recording()
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    transcribe_button.config(state=tk.NORMAL)
    rename_audio_button.config(state=tk.NORMAL)
    logging.info("Stop recording button clicked")



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
        # Get the current transcription text (excluding confidence scores and formatting)
        current_text = transcription_box.get("1.0", tk.END).strip()
        
        # Extract just the transcribed text, removing confidence scores and formatting
        clean_text = ""
        for line in current_text.split('\n'):
            if not any(x in line for x in ['confidence', '===', '---', 'TRANSCRIPTION']):
                if not line.startswith('[') and not line.strip() == "":
                    clean_text += line.strip() + " "
        
        if not clean_text:
            logging.warning("No transcription available for emotion analysis.")
            return
            
        # Perform emotion analysis
        emotion_analysis = emotion_analyzer.analyze(clean_text, recorder.filepath)
        
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
        # Get the path to the transcription file
        transcription_file = os.path.join(save_directory, "output_transcription.txt") if save_directory else "output_transcription.txt"
        
        if not os.path.exists(transcription_file):
            logging.warning("No transcription file found.")
            return
            
        # Read the transcription file
        with open(transcription_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
        # Extract just the transcribed text, removing timestamps, confidence scores and formatting
        clean_text = ""
        for line in content.split('\n'):
            # Skip lines with metadata and formatting
            if (not any(x in line.lower() for x in ['confidence', '=', '-', 'transcription']) and 
                not line.strip().startswith('[') and 
                line.strip()):
                clean_text += line.strip() + " "
                
        if not clean_text:
            logging.error("No text to analyze")
            return
            
        # Perform analysis
        analysis_results = text_analyzer.analyze_text(clean_text)
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
        
        # Save analysis results to file
        analysis_path = os.path.join(save_directory, "text_analysis.txt") if save_directory else "text_analysis.txt"
        with open(analysis_path, "w", encoding="utf-8") as f:
            f.write(formatted_results)
        logging.info(f"Text analysis saved to {analysis_path}")
        
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


class WaveformVisualizer:
    def __init__(self, frame):
        self.frame = frame
        self.is_recording = False
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(4, 4), dpi=100, facecolor='#2b2b2b')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#2b2b2b')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        
        # Set up the line plot with matching dimensions
        self.chunk_size = 1024
        self.x = np.arange(0, self.chunk_size)
        self.line, = self.ax.plot(self.x, np.zeros(self.chunk_size), color='#4caf50')
        
        # Configure plot appearance
        self.ax.set_ylim(-32768, 32767)
        self.ax.set_xlim(0, self.chunk_size)
        self.ax.grid(True, color='#444444')
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.configure(bg='#2b2b2b', highlightthickness=0)
        self.canvas_widget.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Audio stream configuration
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.p = None
        self.stream = None

    def start_recording(self):
        self.is_recording = True
        threading.Thread(target=self._record_stream, daemon=True).start()

    def stop_recording(self):
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.p:
            self.p.terminate()

    def _record_stream(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )

        while self.is_recording:
            try:
                data = self.stream.read(self.chunk_size)
                audio_data = np.frombuffer(data, dtype=np.int16)
                self.line.set_ydata(audio_data)
                self.canvas.draw_idle()
            except Exception as e:
                print(f"Error reading audio stream: {e}")
                break

        self.stop_recording()
    def update_theme(self, theme):
        self.fig.set_facecolor(theme['plot_bg'])
        self.ax.set_facecolor(theme['plot_bg'])
        self.line.set_color(theme['waveform_color'])
        self.ax.tick_params(axis='x', colors=theme['axis_color'])
        self.ax.tick_params(axis='y', colors=theme['axis_color'])
        self.ax.grid(True, color=theme['grid_color'])
        self.ax.xaxis.label.set_color(theme['axis_color'])
        self.ax.yaxis.label.set_color(theme['axis_color'])
        self.ax.title.set_color(theme['axis_color'])
        self.canvas.draw()


recorder = AudioRecorder()
transcriber = AudioTranscriber()
emotion_analyzer = EmotionAnalyzer()
text_processor = TextProcessor()  # Will automatically load API key from .env if available

text_analyzer = TextAnalyzer()
root = TkinterDnD.Tk()

# translation code start-----------------------------------------------------------------------------------------------------------------------------------------------------------------
MODEL_NAME = "facebook/nllb-200-distilled-600M"  # Faster version of NLLB
device = "cuda" if torch.cuda.is_available() else "cpu"

try:
    print(f"Loading NLLB-200 model ({MODEL_NAME}) on {device}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME).to(device)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Failed to load NLLB model: {e}")
    model, tokenizer = None, None

#  Dictionary of Supported Languages (Including Indian Languages)
LANGUAGES = {
    "English": "eng_Latn",
    "French": "fra_Latn",
    "Spanish": "spa_Latn",
    "German": "deu_Latn",
    "Italian": "ita_Latn",
    "Russian": "rus_Cyrl",
    "Chinese": "zho_Hans",
    # Indian Languages
    "Hindi": "hin_Deva",
    "Bengali": "ben_Beng",
    "Tamil": "tam_Taml",
    "Telugu": "tel_Telu",
    "Marathi": "mar_Deva",
    "Gujarati": "guj_Gujr",
    "Punjabi": "pan_Guru",
    "Malayalam": "mal_Mlym",
    "Kannada": "kan_Knda",
    "Odia": "ory_Orya",
    "Urdu": "urd_Arab",
}

#Optimized translation function
def translate_text_nllb(text, src_lang, tgt_lang):
    if model is None or tokenizer is None:
        return "Error: Model not loaded."

    try:
        # Convert language names to model-specific codes
        src_lang_code = LANGUAGES.get(src_lang, "eng_Latn")
        tgt_lang_code = LANGUAGES.get(tgt_lang, "hin_Deva")  # Default to Hindi

        print(f"Translating from {src_lang} ({src_lang_code}) → {tgt_lang} ({tgt_lang_code})")

        #  Set source language in tokenizer
        tokenizer.src_lang = src_lang_code

        # Encode input text
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True).to(device)

        #  Get `forced_bos_token_id` correctly
        tgt_lang_id = tokenizer.convert_tokens_to_ids(tgt_lang_code)

        if tgt_lang_id is None or tgt_lang_id == tokenizer.unk_token_id:
            print(f"Error: Invalid target language ID for {tgt_lang_code}.")
            return "Translation failed: Invalid target language."

        # Generate translation
        with torch.no_grad():
            translated_tokens = model.generate(**inputs, forced_bos_token_id=tgt_lang_id)

        translated_text = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
        return translated_text

    except Exception as e:
        print(f"Translation failed: {e}")
        return f"Translation failed: {e}"

#  Translate the output_transcription.txt file
def translate_file(src_lang, tgt_lang):
    save_directory = os.getcwd()
    transcription_file = os.path.join(save_directory, "output_transcription.txt")
    translated_file = os.path.join(save_directory, f"output_transcription_{tgt_lang}.txt")

    if not os.path.exists(transcription_file):
        messagebox.showerror("Error", "No output_transcription file found. Please transcribe some audio first.")
        return

    try:
        with open(transcription_file, "r", encoding="utf-8") as f:
            content = f.read()

        if not content.strip():
            messagebox.showerror("Error", "The output_transcription.txt file is empty.")
            return

        translated_text = translate_text_nllb(content, src_lang, tgt_lang)

        with open(translated_file, "w", encoding="utf-8") as f:
            f.write(translated_text)

        messagebox.showinfo("Success", f"Translated file saved as output_transcription_{tgt_lang}.txt")

    except Exception as e:
        messagebox.showerror("Error", f"Translation failed: {e}")

#  Asynchronous wrapper to prevent GUI from freezing
def translate_async(src_lang, tgt_lang):
    threading.Thread(target=lambda: translate_file(src_lang, tgt_lang), daemon=True).start()

#  GUI for Translation
def open_translation_dashboard():
    save_directory = os.getcwd()
    transcription_file = os.path.join(save_directory, "output_transcription.txt")

    if not os.path.exists(transcription_file):
        messagebox.showerror("Error", "No transcription file found. Please transcribe some audio first.")
        return

    # Create a new Tkinter window
    dashboard = tk.Toplevel()
    dashboard.title("Translate output_transcription.txt")
    dashboard.geometry("300x300")

    tk.Label(dashboard, text="Translate output_transcription.txt to:").pack(pady=10)

    # Dropdown for source and target languages
    tk.Label(dashboard, text="Source Language:").pack()
    src_lang_var = tk.StringVar(dashboard)
    src_lang_var.set("English")  # Default source language
    src_lang_menu = tk.OptionMenu(dashboard, src_lang_var, *LANGUAGES.keys())
    src_lang_menu.pack(pady=5)

    tk.Label(dashboard, text="Target Language:").pack()
    tgt_lang_var = tk.StringVar(dashboard)
    tgt_lang_var.set("Hindi")  # Default target language
    tgt_lang_menu = tk.OptionMenu(dashboard, tgt_lang_var, *LANGUAGES.keys())
    tgt_lang_menu.pack(pady=5)

    # Button to translate
    translate_btn = tk.Button(dashboard, text="Translate", 
                               command=lambda: translate_async(src_lang_var.get(), tgt_lang_var.get()))
    translate_btn.pack(pady=10)

    dashboard.mainloop()
MODEL_NAME = "facebook/nllb-200-distilled-600M"  # Faster version of NLLB
device = "cuda" if torch.cuda.is_available() else "cpu"

try:
    print(f"Loading NLLB-200 model ({MODEL_NAME}) on {device}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME).to(device)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Failed to load NLLB model: {e}")
    model, tokenizer = None, None

#  Dictionary of Supported Languages (Including Indian Languages)
LANGUAGES = {
    "English": "eng_Latn",
    "French": "fra_Latn",
    "Spanish": "spa_Latn",
    "German": "deu_Latn",
    "Italian": "ita_Latn",
    "Russian": "rus_Cyrl",
    "Chinese": "zho_Hans",
    # Indian Languages
    "Hindi": "hin_Deva",
    "Bengali": "ben_Beng",
    "Tamil": "tam_Taml",
    "Telugu": "tel_Telu",
    "Marathi": "mar_Deva",
    "Gujarati": "guj_Gujr",
    "Punjabi": "pan_Guru",
    "Malayalam": "mal_Mlym",
    "Kannada": "kan_Knda",
    "Odia": "ory_Orya",
    "Urdu": "urd_Arab",
}

#  Optimized translation function
def translate_text_nllb(text, src_lang, tgt_lang):
    if model is None or tokenizer is None:
        return "Error: Model not loaded."

    try:
        # Convert language names to model-specific codes
        src_lang_code = LANGUAGES.get(src_lang, "eng_Latn")
        tgt_lang_code = LANGUAGES.get(tgt_lang, "hin_Deva")  # Default to Hindi

        print(f"Translating from {src_lang} ({src_lang_code}) → {tgt_lang} ({tgt_lang_code})")

        # Set source language in tokenizer
        tokenizer.src_lang = src_lang_code

        # Encode input text
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True).to(device)

        #  Get `forced_bos_token_id` correctly
        tgt_lang_id = tokenizer.convert_tokens_to_ids(tgt_lang_code)

        if tgt_lang_id is None or tgt_lang_id == tokenizer.unk_token_id:
            print(f"Error: Invalid target language ID for {tgt_lang_code}.")
            return "Translation failed: Invalid target language."

        # Generate translation
        with torch.no_grad():
            translated_tokens = model.generate(**inputs, forced_bos_token_id=tgt_lang_id)

        translated_text = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
        return translated_text

    except Exception as e:
        print(f"Translation failed: {e}")
        return f"Translation failed: {e}"

# Translate the output_transcription.txt file
def translate_file(src_lang, tgt_lang):
    save_directory = os.getcwd()
    transcription_file = os.path.join(save_directory, "output_transcription.txt")
    translated_file = os.path.join(save_directory, f"output_transcription_{tgt_lang}.txt")

    if not os.path.exists(transcription_file):
        messagebox.showerror("Error", "No output_transcription file found. Please transcribe some audio first.")
        return

    try:
        with open(transcription_file, "r", encoding="utf-8") as f:
            content = f.read()

        if not content.strip():
            messagebox.showerror("Error", "The output_transcription.txt file is empty.")
            return

        translated_text = translate_text_nllb(content, src_lang, tgt_lang)

        with open(translated_file, "w", encoding="utf-8") as f:
            f.write(translated_text)

        messagebox.showinfo("Success", f"Translated file saved as output_transcription_{tgt_lang}.txt")

    except Exception as e:
        messagebox.showerror("Error", f"Translation failed: {e}")

# Asynchronous wrapper to prevent GUI from freezing
def translate_async(src_lang, tgt_lang):
    threading.Thread(target=lambda: translate_file(src_lang, tgt_lang), daemon=True).start()

#  GUI for Translation
def open_translation_dashboard():
    save_directory = os.getcwd()
    transcription_file = os.path.join(save_directory, "output_transcription.txt")

    if not os.path.exists(transcription_file):
        messagebox.showerror("Error", "No transcription file found. Please transcribe some audio first.")
        return

    # Create a new Tkinter window
    dashboard = tk.Toplevel()
    dashboard.title("Translate output_transcription.txt")
    dashboard.geometry("300x300")

    tk.Label(dashboard, text="Translate output_transcription.txt to:").pack(pady=10)

    # Dropdown for source and target languages
    tk.Label(dashboard, text="Source Language:").pack()
    src_lang_var = tk.StringVar(dashboard)
    src_lang_var.set("English")  # Default source language
    src_lang_menu = tk.OptionMenu(dashboard, src_lang_var, *LANGUAGES.keys())
    src_lang_menu.pack(pady=5)

    tk.Label(dashboard, text="Target Language:").pack()
    tgt_lang_var = tk.StringVar(dashboard)
    tgt_lang_var.set("Hindi")  # Default target language
    tgt_lang_menu = tk.OptionMenu(dashboard, tgt_lang_var, *LANGUAGES.keys())
    tgt_lang_menu.pack(pady=5)

    # Button to translate
    translate_btn = tk.Button(dashboard, text="Translate", 
                               command=lambda: translate_async(src_lang_var.get(), tgt_lang_var.get()))
    translate_btn.pack(pady=10)

    dashboard.mainloop()

#translation code end

def open_annotation_window():
    # Create a new top-level window for annotations
    annotation_win = tk.Toplevel(root)
    annotation_win.title("Annotate Transcription")
    annotation_win.geometry("600x400")

    # Create a frame for layout
    frame = tk.Frame(annotation_win, padx=10, pady=10, bg="#2b2b2b")
    frame.pack(fill=tk.BOTH, expand=True)

    # Label for transcription display
    transcription_label = tk.Label(frame, text="Transcription", bg="#2b2b2b", fg="white", font=("Helvetica", 12, "bold"))
    transcription_label.pack(anchor="w")

    font_size_label = tk.Label(control_frame, text="Font Size:", bg="#2b2b2b", fg="white")
    font_size_label.pack(side=tk.LEFT, padx=5)

    font_sizes = [8, 10, 11, 12, 14, 16, 18, 20]
    font_size_var = tk.IntVar(value=11)  # Default size matches initial setting
    font_size_dropdown = tk.OptionMenu(control_frame, font_size_var, *font_sizes, command=update_font_size)
    font_size_dropdown.config(bg="#4caf50", fg="white", activebackground="#45a049")
    font_size_dropdown.pack(side=tk.LEFT, padx=5)

    color_button = tk.Button(
        control_frame, 
        text="Choose Color", 
        command=choose_color,
        bg="#4caf50",
        fg="white",
        activebackground="#45a049"
    )
    color_button.pack(side=tk.LEFT, padx=5)

    # Adding tooltips for better UX
    def create_tooltip(widget, text):
        tooltip = tk.Toplevel(widget)
        tooltip.withdraw()
        tooltip.wm_overrideredirect(True)
        
        label = tk.Label(tooltip, text=text, bg="#ffffe0", relief="solid", borderwidth=1)
        label.pack()
        
        def enter(event):
            x = widget.winfo_rootx() + widget.winfo_width() + 5
            y = widget.winfo_rooty()
            tooltip.geometry(f"+{x}+{y}")
            tooltip.deiconify()
        
        def leave(event):
            tooltip.withdraw()
        
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    create_tooltip(font_size_dropdown, "Adjust font size for the transcription text")
    create_tooltip(color_button, "Change base text color for the transcription")
    # Read-only text widget to display the current transcription
    transcription_display = tk.Text(frame, height=10, wrap=tk.WORD)
    transcription_display.pack(fill=tk.BOTH, expand=True, pady=(0,10))
    transcription_text = transcription_box.get("1.0", tk.END).strip()
    transcription_display.insert(tk.END, transcription_text)
    transcription_display.config(state=tk.DISABLED)

    # Label for annotation input
    annotation_label = tk.Label(frame, text="Enter your comments/annotations:", bg="#2b2b2b", fg="white", font=("Helvetica", 12, "bold"))
    annotation_label.pack(anchor="w")

    # Text widget for user annotations
    annotation_text_widget = tk.Text(frame, height=5, wrap=tk.WORD)
    annotation_text_widget.pack(fill=tk.BOTH, expand=True, pady=(0,10))

    # Function to save annotated transcription
    def save_annotation():
        comments = annotation_text_widget.get("1.0", tk.END).strip()
        if not transcription_text:
            messagebox.showwarning("Warning", "No transcription available to annotate.")
            return

        # Generate a unique filename based on the transcription content
        transcription_hash = hashlib.md5(transcription_text.encode()).hexdigest()[:8]  # Short hash for uniqueness
        annotated_file = os.path.join(save_directory, f"annotated_transcription_{transcription_hash}.txt")

        # Save both the transcription and the comments
        try:
            with open(annotated_file, "a", encoding="utf-8") as f:
                if os.path.getsize(annotated_file) == 0:  # If it's a new file, add transcription
                    f.write(f"Transcription:\n{transcription_text}\n\n")
                f.write(f"User Comments:\n{comments}\n\n")  # Append new comments
                
            messagebox.showinfo("Success", f"Annotated transcription saved to {annotated_file}")
            annotation_win.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save annotation: {e}")


    # Save Annotation button
    save_button = tk.Button(frame, text="Save Annotation", command=save_annotation, bg="#4caf50", fg="white", font=("Helvetica", 12, "bold"), bd=3, relief=tk.RAISED)
    save_button.pack(pady=5)

def transcribe_with_progress(event=None):
    """
    Automatically displays a progress tracking window during transcription.
    This function is intended to replace direct calls to transcriber.transcribe_audio()
    so that every transcription operation shows a progress bar.
    """
    if not recorder.filepath:
        logging.warning("No audio file available for transcription.")
        transcription_box.insert(tk.END, "No audio file available for transcription.\n")
        return

    # Create a progress window
    progress_win = Toplevel(root)
    progress_win.title("Transcription Progress")
    progress_win.geometry("400x150")
    progress_win.configure(bg=root.cget("bg"))
    
    # Status label for detailed messages
    status_label = tk.Label(progress_win, text="Initializing...", font=("Helvetica", 12),
                            bg=root.cget("bg"), fg="white")
    status_label.pack(pady=(20, 10))
    
    # Create a determinate progress bar
    progress_bar = ttk.Progressbar(progress_win, orient="horizontal", length=300, mode="determinate")
    progress_bar.pack(pady=10)
    progress_bar["maximum"] = 100
    progress_bar["value"] = 0

    def update_status(message, value):
        """Updates the status message and progress bar value."""
        status_label.config(text=message)
        progress_bar["value"] = value
        root.update_idletasks()

    def run_transcription():
        try:
            # Phase 1: Loading file
            update_status("Loading file...", 20)
            # Simulate delay if file loading is too fast (optional)
            time.sleep(1)
            
            # Phase 2: Transcribing audio
            update_status("Transcribing...", 50)
            transcription = transcriber.transcribe_audio(recorder.filepath, save_directory)
            
            # Phase 3: Saving transcription
            update_status("Saving transcription...", 80)
            # Simulate saving delay (optional)
            time.sleep(0.5)
            
            # Finalize progress
            update_status("Complete", 100)
            root.update_idletasks()
            
            # Display the transcription in the transcription box
            transcription_box.delete(1.0, tk.END)
            transcription_box.insert(tk.END, transcription)
        except Exception as e:
            transcription_box.insert(tk.END, f"Error: {e}\n")
        finally:
            progress_win.destroy()

    # Run the transcription process in a background thread
    t = threading.Thread(target=run_transcription)
    t.start()

root.title("Audio Recorder & Emotion Analyzer")
root.geometry("1000x900")
root.configure(bg="#2b2b2b")
# root.tk.eval('package require tkdnd')

# Bind hotkeys
root.bind("<d>", browse_directory)
root.bind("<s>", start_recording)
root.bind("<x>", stop_recording)
root.bind("<t>", transcribe_with_progress)

root.bind("<r>", rename_audio_file)
root.bind("<y>", rename_transcription_file)
root.bind("<e>", analyze_emotions)

def open_new_dashboard():
    """Opens a modern dashboard window displaying usage statistics from history.txt."""
    history_file = os.path.join(save_directory, "history.txt")
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        messagebox.showerror("Error", "No history file found. Please transcribe some audio first.")
        return

    num_transcriptions = len(lines)
    word_counts = [len(line.split()) for line in lines]
    total_words = sum(word_counts)
    avg_words = total_words / num_transcriptions if num_transcriptions > 0 else 0

    all_words = []
    for line in lines:
        all_words.extend(line.lower().split())
    common_words = collections.Counter(all_words).most_common(5)

    summary_text = (
        f"Total Transcriptions: {num_transcriptions}\n"
        f"Total Words: {total_words}\n"
        f"Average Words per Transcription: {avg_words:.2f}\n"
        f"Last Transcription: {lines[-1][:50] + '...' if lines else 'N/A'}\n"
        f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    dash_win = tk.Toplevel(root)
    dash_win.title("Usage Statistics Dashboard")
    dash_win.geometry("1100x750")  # Increased size for better readability
    dash_win.configure(bg="#2b2b2b")

    title_label = tk.Label(dash_win, text="Usage Statistics Dashboard", bg="#2b2b2b", fg="white", font=("Helvetica", 18, "bold"))
    title_label.pack(pady=10)

    main_frame = tk.Frame(dash_win, bg="#2b2b2b")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    summary_frame = tk.Frame(main_frame, bg="#2b2b2b")
    summary_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
    summary_label = tk.Label(summary_frame, text=summary_text, justify="left", bg="#2b2b2b", fg="white", font=("Helvetica", 12))
    summary_label.pack(anchor="n")

    graphs_frame = tk.Frame(main_frame, bg="#2b2b2b")
    graphs_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

    sns.set_style("darkgrid", {"axes.facecolor": "#2b2b2b", "grid.color": "gray"})
    fig = plt.Figure(figsize=(12, 8), dpi=100, facecolor="#2b2b2b", constrained_layout=True)

    ax1 = fig.add_subplot(221)
    ax1.bar(range(1, num_transcriptions + 1), word_counts, color="#4CAF50")
    ax1.set_xlabel("Transcription #", color="white")
    ax1.set_ylabel("Word Count", color="white")
    ax1.set_title("Words per Transcription", color="white")
    ax1.tick_params(axis="x", colors="white")
    ax1.tick_params(axis="y", colors="white")

    ax2 = fig.add_subplot(222)
    if common_words:
        labels = [f"{word} ({count})" for word, count in common_words]
        counts = [count for word, count in common_words]
        ax2.pie(counts, labels=labels, colors=sns.color_palette("pastel"), autopct='%1.1f%%', textprops={'color': 'white'})
    ax2.set_title("Frequent Words", color="white")

    ax3 = fig.add_subplot(223)
    sns.histplot(word_counts, bins=15, kde=True, color="#FFA726", ax=ax3)
    ax3.set_xlabel("Word Count", color="white")
    ax3.set_ylabel("Frequency", color="white")
    ax3.set_title("Transcription Length Distribution", color="white")
    ax3.tick_params(axis="x", colors="white")
    ax3.tick_params(axis="y", colors="white")

    ax4 = fig.add_subplot(224)
    ax4.plot(range(1, num_transcriptions + 1), word_counts, marker='o', linestyle='-', color="#FF5722")
    ax4.set_xlabel("Transcription #", color="white")
    ax4.set_ylabel("Word Count", color="white")
    ax4.set_title("Transcription Trend", color="white")
    ax4.tick_params(axis="x", colors="white")
    ax4.tick_params(axis="y", colors="white")

    canvas = FigureCanvasTkAgg(fig, master=graphs_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    close_btn = tk.Button(dash_win, text="Close Dashboard", command=dash_win.destroy, bg="#F44336", fg="white", font=("Helvetica", 12, "bold"))
    close_btn.pack(pady=5)

import threading
import time
from tkinter import Toplevel, ttk, filedialog, messagebox

def browse_multiple_files():
    """Allow users to select multiple audio files for batch processing."""
    filepaths = filedialog.askopenfilenames(
        title="Select Audio Files", 
        filetypes=[("Audio Files", "*.wav;*.mp3;*.m4a;*.flac")]
    )
    if filepaths:
        process_batch_transcription(filepaths)

def process_batch_transcription(filepaths):
    """
    Processes multiple audio files and appends transcriptions to a single file (batch_transcription.txt)
    while showing a progress bar with detailed status messages.
    """
    batch_file = os.path.join(save_directory, "batch_transcription.txt")
    transcription_box.delete(1.0, tk.END)
    transcription_box.insert(tk.END, "Processing batch transcription...\n")
    root.update_idletasks()

    # Create progress window
    progress_win = Toplevel(root)
    progress_win.title("Batch Transcription Progress")
    progress_win.geometry("400x150")
    progress_win.configure(bg=root.cget("bg"))
    
    status_label = tk.Label(progress_win, text="Initializing...", font=("Helvetica", 12),
                              bg=root.cget("bg"), fg="white")
    status_label.pack(pady=(20, 10))
    
    progress_bar = ttk.Progressbar(progress_win, orient="horizontal", length=300, mode="determinate")
    progress_bar.pack(pady=10)
    progress_bar["maximum"] = 100
    progress_bar["value"] = 0

    def update_status(message, value):
        status_label.config(text=message)
        progress_bar["value"] = value
        root.update_idletasks()

    total_files = len(filepaths)
    progress_increment = 100 / (total_files + 1) if total_files > 0 else 100

    def run_batch():
        try:
            with open(batch_file, "a", encoding="utf-8") as f:
                for i, filepath in enumerate(filepaths, start=1):
                    base_name = os.path.basename(filepath)
                    update_status(f"Processing {base_name} ({i}/{total_files})...", progress_increment * i)
                    transcription = transcriber.transcribe_audio(filepath, save_directory)
                    if transcription.startswith("Error:"):
                        transcription_box.insert(tk.END, f"Skipped {base_name} (Error)\n")
                        continue
                    f.write(f"---- Transcription: {base_name} ----\n")
                    f.write(transcription + "\n\n")
                    transcription_box.insert(tk.END, f"Processed {base_name}\n")
                    root.update_idletasks()
                    # (Optional: add a small delay for smoother UI updates)
                    time.sleep(0.2)
            transcription_box.insert(tk.END, f"\nBatch transcription saved to: {batch_file}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Batch transcription failed: {e}")
        finally:
            progress_win.destroy()

    threading.Thread(target=run_batch).start()


def export_transcription():
    """
    Exports the current transcription segments (from transcriber.segments_with_confidence)
    to JSON or CSV with time stamps.
    """
    # Check if transcription data is available
    if not hasattr(transcriber, "segments_with_confidence") or not transcriber.segments_with_confidence:
        messagebox.showwarning("Export Error", "No transcription data available to export.")
        return

    # Ask the user to select format (Yes = JSON, No = CSV)
    fmt_choice = messagebox.askquestion("Select Format", "Export as JSON? (Select 'No' for CSV)")
    export_format = "json" if fmt_choice.lower() == "yes" else "csv"
    file_extension = ".json" if export_format == "json" else ".csv"

    # Open a file save dialog
    file_path = filedialog.asksaveasfilename(
        defaultextension=file_extension,
        filetypes=[("JSON Files", "*.json")] if export_format == "json" else [("CSV Files", "*.csv")],
        title="Save Transcription Export"
    )
    if not file_path:
        return  # User cancelled

    try:
        data = transcriber.segments_with_confidence  # List of dictionaries with transcription details
        if export_format == "json":
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        else:
            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["timestamp", "text", "confidence"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for segment in data:
                    writer.writerow({
                        "timestamp": segment.get("timestamp", ""),
                        "text": segment.get("text", ""),
                        "confidence": segment.get("confidence", "")
                    })
        messagebox.showinfo("Export Success", f"Transcription exported successfully to {file_path}")
    except Exception as e:
        messagebox.showerror("Export Error", f"Failed to export transcription: {e}")


# Create a new horizontal frame
main_frame = tk.Frame(root, bg="#2b2b2b")
main_frame.pack(fill=tk.X, padx=10, pady=5)

button_container = tk.Frame(root, bg="#2b2b2b")
button_container.pack(in_=main_frame, side=tk.LEFT, fill=tk.Y)

waveform_frame = tk.Frame(root, bg="#2b2b2b")
waveform_frame.pack(in_=main_frame, side=tk.RIGHT, padx=5)

visualizer = WaveformVisualizer(waveform_frame)

# Export Transcription Button
export_button = tk.Button(
    waveform_frame,
    text="Export Transcription",
    command=export_transcription,
    bg="#008CBA",
    fg="white",
    font=("Helvetica", 12, "bold"),
    bd=3, width=20,
    height= 1,
    relief=tk.RAISED
)
export_button.pack(pady=3)

# Create log box
log_box = tk.Text(button_container, height=8, width=60, wrap=tk.WORD, state=tk.DISABLED, bg="#333333", fg="white", font=("Helvetica", 10))
log_box.pack(pady=5)

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
    "height": 1, 
}
theme_button = tk.Button(
    button_container, 
    text="Toggle Theme", 
    command=toggle_theme, 
    **button_style
)
theme_button.pack(pady=3)
browse_button = tk.Button(
    button_container, text="Browse Directory (D)", command=browse_directory, **button_style
)
browse_button.pack(pady=3)

# Batch Transcription Button
batch_button = tk.Button(
    button_container, 
    text="Batch Transcription", 
    command=browse_multiple_files, 
    bg="#FFA500", bd=3, relief=tk.RAISED, width=20,
    height= 1, font=("Helvetica", 12, "bold"), fg="white"
    
)
batch_button.pack(pady=3)

start_button = tk.Button(
    button_container, text="Start Recording (S)", command=start_recording, **button_style
)
start_button.pack(pady=3)

stop_button = tk.Button(
    button_container,
    text="Stop Recording (X)",
    command=stop_recording,
    state=tk.DISABLED,
    **button_style
)
stop_button.pack(pady=3)

rename_audio_button = tk.Button(
    button_container,
    text="Rename Audio (R)",
    command=rename_audio_file,
    state=tk.DISABLED,
    **button_style
)
rename_audio_button.pack(pady=3)

rename_transcription_button = tk.Button(
    button_container,
    text="Rename Transcription (Y)",
    command=rename_transcription_file,
    state=tk.DISABLED,
    **button_style
)
rename_transcription_button.pack(pady=3)

transcribe_button = tk.Button(
    button_container, text="Transcribe (T)", command=transcribe_with_progress, state=tk.DISABLED, **button_style
)
transcribe_button.pack(pady=3)

analyze_button = tk.Button(
    button_container, text="Analyze Emotions (E)", command=analyze_emotions, state=tk.DISABLED, **button_style
)
analyze_button.pack(pady=3)

#Usage Dashboard Button
dashboard_button = tk.Button(button_container, text="Usage Dashboard", command=open_new_dashboard, **button_style)
dashboard_button.pack(pady=3)

analyze_text_button = tk.Button(button_container, text="Analyze Text", command=analyze_text_content, bg="#4caf50", fg="white", font=("Helvetica", 9, "bold"), bd=3)
analyze_text_button.pack(side=tk.LEFT, padx=5)

api_key_button = tk.Button(button_container, text="Set API Key", command=set_api_key, bg="#4caf50", fg="white", font=("Helvetica", 9, "bold"), bd=3)
api_key_button.pack(side=tk.LEFT, padx=5)

summarize_button = tk.Button(button_container, text="Summarize", command=summarize_text, bg="#4caf50", fg="white", font=("Helvetica", 9, "bold"), bd=3)
summarize_button.pack(side=tk.LEFT, padx=5)

query_button = tk.Button(button_container, text="Ask Question", command=query_text, bg="#4caf50", fg="white", font=("Helvetica", 9, "bold"), bd=3)
query_button.pack(side=tk.LEFT, padx=5)

# translate button
translation_btn = tk.Button(button_container, text="Translate", command=open_translation_dashboard)
translation_btn.pack(side=tk.LEFT, padx=5)

# Annotate Transcription Button
annotate_button = tk.Button(button_container, text="Annotate Transcription", command=open_annotation_window, bg="#4caf50", fg="white", font=("Helvetica", 9, "bold"), bd=3, relief=tk.RAISED)
annotate_button.pack(pady=3)

# Create a frame for transcription
transcription_frame = tk.Frame(root, bg="#2b2b2b")
transcription_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
control_frame = tk.Frame(transcription_frame, bg="#2b2b2b")
control_frame.pack(fill=tk.X, pady=5)

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
