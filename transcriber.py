import os
import whisper
import logging
import shutil
import librosa
import numpy as np

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

class AudioTranscriber:
    def __init__(self):
        self.model = None
        self.current_model_size = "small"  # default model
        self.transcription_file = None

    def load_model(self, model_size):
        """Load a specific Whisper model size."""
        try:
            if model_size not in ["tiny", "base", "small", "medium", "large"]:
                raise ValueError(f"Invalid model size: {model_size}")
            self.model = whisper.load_model(model_size)
            self.current_model_size = model_size
            logging.info(f"Loaded Whisper model: {model_size}")
            return True
        except Exception as e:
            logging.error(f"Error loading Whisper model {model_size}: {e}")
            return False

    def ensure_model_loaded(self):
        """Ensures the selected model is loaded before transcription."""
        if self.model is None:
            return self.load_model(self.current_model_size)
        # Get the current loaded model size
        try:
            current_loaded_size = self.model.model_size
            if current_loaded_size != self.current_model_size:
                return self.load_model(self.current_model_size)
        except AttributeError:
            # If we can't get the model size, reload to be safe
            return self.load_model(self.current_model_size)
        return True

    def transcribe_audio(self, filepath, save_directory=None):
        if not self.ensure_model_loaded():
            logging.error("Failed to load Whisper model.")
            return "Error: Failed to load Whisper model.\n"

        try:
            if not os.path.exists(filepath):
                error_msg = f"Audio file not found at: {filepath}"
                logging.error(error_msg)
                return f"Error: {error_msg}\n"

            # Load and preprocess audio file using librosa
            logging.info(f"Loading audio file: {filepath}")
            audio_data, sr = librosa.load(filepath, sr=16000, mono=True)
            
            # Ensure audio data is float32
            audio_data = audio_data.astype(np.float32)
            logging.info(f"Audio loaded successfully. Shape: {audio_data.shape}, dtype: {audio_data.dtype}")

            # Transcribe with word timestamps
            logging.info("Starting transcription...")
            result = self.model.transcribe(
                audio_data, 
                language='en',
                word_timestamps=True
            )
            
            # Process segments
            segments = result.get('segments', [])
            
            if not segments:
                return "Error: No speech detected in the audio file.\n"
            
            transcription_text = "".join(segment['text'] for segment in segments).strip()
            logging.info("Transcription completed.")

            # Update transcription history
            self.update_transcription_history(transcription_text)

            return transcription_text
        
        except Exception as e:
            error_msg = f"Error during transcription: {str(e)}"
            logging.error(error_msg)
            return f"Error: {error_msg}\n"

    def update_transcription_history(self, text):
        """Appends the transcription to a history file."""
        history_file = "history.txt"
        try:
            with open(history_file, "a", encoding="utf-8") as f:
                f.write(text + "\n")
            logging.info(f"Transcription appended to {history_file}")
        except Exception as e:
            logging.error(f"Error updating transcription history: {e}")

    def save_transcription(self, text, save_directory=None):
        try:
            if save_directory:
                self.transcription_file = os.path.join(save_directory, "output_transcription.txt")
            else:
                self.transcription_file = "output_transcription.txt"

            with open(self.transcription_file, "w", encoding="utf-8") as f:
                f.write(text)
            logging.info(f"Transcription saved to {self.transcription_file}")
            return True
        except Exception as e:
            logging.error(f"Error saving transcription: {e}")
            return False

    def rename_transcription(self, new_name):
        if not self.transcription_file or not os.path.exists(self.transcription_file):
            logging.error("No transcription file exists to rename")
            return False
        
        directory = os.path.dirname(self.transcription_file)
        new_filepath = os.path.join(directory, f"{new_name}_transcription.txt")
        
        try:
            shutil.move(self.transcription_file, new_filepath)
            self.transcription_file = new_filepath
            logging.info(f"Transcription file renamed to {new_filepath}")
            return True
        except Exception as e:
            error_msg = f"Error renaming transcription file: {str(e)}"
            logging.error(error_msg)
            return f"Error: {error_msg}\n"
