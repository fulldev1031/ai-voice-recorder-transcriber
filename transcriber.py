import os
import whisper
import logging
import shutil
import librosa
import numpy as np
import torch
from typing import Optional, Tuple

class AudioTranscriber:
    def __init__(self):
        self.model = None
        self.transcription_file = None
        self.setup_logging()
        self.initialize_model()

    def setup_logging(self):
        """Initialize logging with error handling"""
        try:
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler("transcriber.log"),
                    logging.StreamHandler()
                ]
            )
        except Exception as e:
            print(f"Failed to initialize logging: {e}")
            raise

    def initialize_model(self):
        """Initialize Whisper model with error handling"""
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logging.info(f"Using device: {device}")

            if device == "cuda":
                free_memory = torch.cuda.get_device_properties(0).total_memory
                if free_memory < 2_000_000_000:  # 2GB
                    logging.warning("Low GPU memory, falling back to CPU")
                    device = "cpu"

            self.model = whisper.load_model("small").to(device)
            logging.info("Whisper model loaded successfully")
        except Exception as e:
            logging.error(f"Error loading Whisper model: {e}")
            self.model = None
            raise RuntimeError(f"Failed to initialize Whisper model: {e}")

    def validate_file(self, filepath: str) -> None:
        """Validate audio file exists and is accessible"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Audio file not found: {filepath}")
        
        if not os.path.isfile(filepath):
            raise ValueError(f"Path is not a file: {filepath}")
        
        if not os.access(filepath, os.R_OK):
            raise PermissionError(f"No read permission for file: {filepath}")

    def validate_save_directory(self, save_directory: str) -> None:
        """Validate save directory exists and is writable"""
        if not os.path.exists(save_directory):
            try:
                os.makedirs(save_directory)
            except Exception as e:
                raise PermissionError(f"Cannot create save directory: {e}")
        
        if not os.access(save_directory, os.W_OK):
            raise PermissionError(f"No write permission for directory: {save_directory}")

    def load_audio(self, filepath: str) -> Tuple[np.ndarray, int]:
        """Load and preprocess audio file using librosa"""
        try:
            logging.info(f"Loading audio file: {filepath}")
            audio_data, sr = librosa.load(filepath, sr=16000, mono=True)
            audio_data = audio_data.astype(np.float32)
            logging.info(f"Audio loaded successfully. Shape: {audio_data.shape}, dtype: {audio_data.dtype}")
            return audio_data, sr
        except Exception as e:
            logging.error(f"Error loading audio file: {e}")
            raise RuntimeError(f"Failed to load audio file: {e}")

    def transcribe_audio(self, filepath: str, save_directory: Optional[str] = None) -> str:
        """
        Transcribe audio file with comprehensive error handling
        
        Args:
            filepath: Path to audio file
            save_directory: Optional directory to save transcription
            
        Returns:
            str: Transcribed text or error message
        """
        try:
            if not self.model:
                raise RuntimeError("Whisper model not initialized")

            self.validate_file(filepath)

            if save_directory:
                self.validate_save_directory(save_directory)

            file_size = os.path.getsize(filepath)
            if file_size > 1_000_000_000:  # 1GB
                raise ValueError("Audio file too large (>1GB)")
            
            # Load and preprocess audio
            audio_data, _ = self.load_audio(filepath)
            
            # Transcribe the audio
            logging.info("Starting transcription...")
            result = self.model.transcribe(audio_data, language='en')
            transcription_text = result['text'].strip()
            logging.info("Transcription completed")

            if not transcription_text:
                return "Error: No speech detected in the audio file."

            return transcription_text

        except FileNotFoundError as e:
            logging.error(f"File not found error: {e}")
            return f"Error: Audio file not found - {e}"
        except PermissionError as e:
            logging.error(f"Permission error: {e}")
            return f"Error: Permission denied - {e}"
        except ValueError as e:
            logging.error(f"Value error: {e}")
            return f"Error: Invalid input - {e}"
        except RuntimeError as e:
            logging.error(f"Runtime error: {e}")
            return f"Error: Processing failed - {e}"
        except Exception as e:
            logging.error(f"Unexpected error during transcription: {e}")
            return f"Error: Unexpected error - {e}"

    def save_transcription(self, text: str, save_directory: Optional[str] = None) -> bool:
        """Save transcription to file"""
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

    def rename_transcription(self, new_name: str) -> bool:
        """Rename transcription file"""
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
            logging.error(f"Error renaming transcription file: {e}")
            return False

    def __del__(self):
        """Cleanup resources"""
        try:
            if hasattr(self, 'model') and self.model:
                del self.model
            torch.cuda.empty_cache()
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")