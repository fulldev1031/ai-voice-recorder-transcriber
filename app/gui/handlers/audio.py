import logging
import tkinter as tk
from tkinter import simpledialog
from tkinter import Toplevel, ttk
import threading
import time
def start_recording(Recording,event=None):
    if not Recording['save_directory']:
        logging.warning("Save directory is not set. Please select a directory first.")
        return
    
    Recording['recorder'].set_save_directory(Recording['save_directory'])
    try:
        Recording['recorder'].start_recording()
        Recording['visualizer'].start_recording()
        Recording['start_button'].config(state=tk.DISABLED)
        Recording['stop_button'].config(state=tk.NORMAL)
        Recording['transcribe_button'].config(state=tk.DISABLED)
        Recording['rename_audio_button'].config(state=tk.DISABLED)
        Recording['rename_transcription_button'].config(state=tk.DISABLED)
        Recording['analyze_button'].config(state=tk.DISABLED)  # Disable emotion analysis button

        # threading.Thread(target = plot_waveform).start()

        Recording['transcription_box'].delete(1.0, tk.END)  # Clear previous transcription
        logging.info("Start recording button clicked")
    except RuntimeError as e:
        logging.error(e)
        Recording['log_box'].config(state=tk.NORMAL)
        Recording['log_box'].insert(tk.END, f"Error: {e}\n")
        Recording['log_box'].config(state=tk.DISABLED)

def stop_recording(Recording,event=None):
    Recording['recorder'].stop_recording()
    Recording['visualizer'].stop_recording()
    Recording['start_button'].config(state=tk.NORMAL)
    Recording['stop_button'].config(state=tk.DISABLED)
    Recording['transcribe_button'].config(state=tk.NORMAL)
    Recording['rename_audio_button'].config(state=tk.NORMAL)
    logging.info("Stop recording button clicked")

def transcribe_with_progress(Recording,event=None):
    """
    Automatically displays a progress tracking window during transcription.
    This function is intended to replace direct calls to transcriber.transcribe_audio()
    so that every transcription operation shows a progress bar.
    """
    if not Recording['recorder'].filepath:
        logging.warning("No audio file available for transcription.")
        Recording['transcription_box'].insert(tk.END, "No audio file available for transcription.\n")
        return

    # Create a progress window
    progress_win = Toplevel(Recording['root'])
    progress_win.title("Transcription Progress")
    progress_win.geometry("400x150")
    progress_win.configure(bg=Recording['root'].cget("bg"))

    # Status label for detailed messages
    status_label = tk.Label(progress_win, text="Initializing...", font=("Helvetica", 12),
                            bg=Recording['root'].cget("bg"), fg="white")
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
        Recording['root'].update_idletasks()

    def run_transcription():
        try:
            # Phase 1: Loading file
            update_status("Loading file...", 20)
            # Simulate delay if file loading is too fast (optional)
            time.sleep(1)

            # Phase 2: Transcribing audio
            update_status("Transcribing...", 50)
            transcription = Recording['transcriber'].transcribe_audio(Recording['recorder'].filepath, Recording['save_directory'])

            # Phase 3: Saving transcription
            update_status("Saving transcription...", 80)
            # Simulate saving delay (optional)
            time.sleep(0.5)

            # Finalize progress
            update_status("Complete", 100)
            Recording['root'].update_idletasks()

            # Display the transcription in the transcription box
            Recording['transcription_box'].delete(1.0, tk.END)
            Recording['transcription_box'].insert(tk.END, transcription)
        except Exception as e:
            Recording['transcription_box'].insert(tk.END, f"Error: {e}\n")
        finally:
            progress_win.destroy()

    # Run the transcription process in a background thread
    t = threading.Thread(target=run_transcription)
    t.start()

def rename_audio_file(Recording,event=None):
    if not Recording['recorder'].filepath:
        logging.warning("No audio file available to rename.")
        return
    
    new_name = simpledialog.askstring("Rename Audio File", "Enter new filename (without extension):")
    if new_name:
        if Recording['recorder'].rename_audio(new_name):
            logging.info(f"Audio file renamed successfully to {new_name}.wav")
        else:
            logging.error("Failed to rename audio file")