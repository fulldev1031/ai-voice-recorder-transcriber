import os
import whisper
import logging
import librosa
import numpy as np

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

class AudioTranscriber:
    def __init__(self):
        try:
            self.model = whisper.load_model("small")
            logging.info("Whisper model loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading Whisper model: {e}")
            self.model = None

    def transcribe_audio(self, filepath, save_directory=None):
        if not self.model:
            logging.error("Whisper model is not loaded.")
            return "Error: Whisper model not loaded.\n"

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

            # Transcribe the audio data
            logging.info("Starting transcription...")
            result = self.model.transcribe(audio_data, language='en')
            transcription_text = result['text']
            logging.info("Transcription completed")

            if save_directory:
                os.makedirs(save_directory, exist_ok=True)  # Ensure the directory exists
                save_path = os.path.join(save_directory, "transcription.txt")
            else:
                save_path = "transcription.txt"

            with open(save_path, "w", encoding="utf-8") as f:
                f.write(transcription_text)
            
            logging.info(f"Transcription saved to {save_path}")
            return transcription_text
        except Exception as e:
            error_msg = f"Error during transcription: {str(e)}"
            logging.error(error_msg)
            return f"Error: {error_msg}\n"
