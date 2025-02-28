import logging
from tkinter import filedialog, simpledialog
import tkinter as tk
import os
from tkinter import messagebox
import threading
import time
from tkinter import Toplevel, ttk
def browse_directory(Files,event=None):
    directory = filedialog.askdirectory(title="Select Directory")
    if directory:
        Files['save_directory'] = directory
        logging.info(f"Save directory selected: {Files['save_directory']}")
    else:
        logging.info(f"No directory selected. Using default: {Files['save_directory']}")

def rename_transcription_file(Files,event=None):
    if not Files['transcriber'].transcription_file:
        logging.warning("No transcription file available to rename.")
        return
    
    new_name = simpledialog.askstring("Rename Transcription File", "Enter new filename (without extension):")
    if new_name:
        if Files['transcriber'].rename_transcription(new_name):
            logging.info(f"Transcription file renamed successfully to {new_name}_transcription.txt")
        else:
            logging.error("Failed to rename transcription file")

    Files['analyze_button'].config(state=tk.NORMAL)  # Enable emotion analysis after transcription
    logging.info("Transcription displayed in the UI.")

def browse_multiple_files(Files):
    """Allow users to select multiple audio files for batch processing."""
    filepaths = filedialog.askopenfilenames(
        title="Select Audio Files", 
        filetypes=[("Audio Files", "*.wav;*.mp3;*.m4a;*.flac")]
    )
    if filepaths:
        process_batch_transcription(Files,filepaths)

def process_batch_transcription(Files,filepaths):
    """
    Processes multiple audio files and appends transcriptions to a single file (batch_transcription.txt)
    while showing a progress bar with detailed status messages.
    """
    batch_file = os.path.join(Files['save_directory'], "batch_transcription.txt")
    Files['transcription_box'].delete(1.0, tk.END)
    Files['transcription_box'].insert(tk.END, "Processing batch transcription...\n")
    Files['root'].update_idletasks()

    # Create progress window
    progress_win = Toplevel(Files['root'])
    progress_win.title("Batch Transcription Progress")
    progress_win.geometry("400x150")
    progress_win.configure(bg=Files['root'].cget("bg"))

    status_label = tk.Label(progress_win, text="Initializing...", font=("Helvetica", 12),
                              bg=Files['root'].cget("bg"), fg="white")
    status_label.pack(pady=(20, 10))

    progress_bar = ttk.Progressbar(progress_win, orient="horizontal", length=300, mode="determinate")
    progress_bar.pack(pady=10)
    progress_bar["maximum"] = 100
    progress_bar["value"] = 0

    def update_status(message, value):
        status_label.config(text=message)
        progress_bar["value"] = value
        Files['root'].update_idletasks()

    total_files = len(filepaths)
    progress_increment = 100 / (total_files + 1) if total_files > 0 else 100

    def run_batch():
        try:
            with open(batch_file, "a", encoding="utf-8") as f:
                for i, filepath in enumerate(filepaths, start=1):
                    base_name = os.path.basename(filepath)
                    update_status(f"Processing {base_name} ({i}/{total_files})...", progress_increment * i)
                    transcription = Files['transcriber'].transcribe_audio(filepath, Files['save_directory'])
                    if transcription.startswith("Error:"):
                        Files['transcription_box'].insert(tk.END, f"Skipped {base_name} (Error)\n")
                        continue
                    f.write(f"---- Transcription: {base_name} ----\n")
                    f.write(transcription + "\n\n")
                    Files['transcription_box'].insert(tk.END, f"Processed {base_name}\n")
                    Files['root'].update_idletasks()
                    # (Optional: add a small delay for smoother UI updates)
                    time.sleep(0.2)
            Files['transcription_box'].insert(tk.END, f"\nBatch transcription saved to: {batch_file}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Batch transcription failed: {e}")
        finally:
            progress_win.destroy()

    threading.Thread(target=run_batch).start()