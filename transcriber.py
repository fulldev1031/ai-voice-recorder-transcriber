import os
import whisper
import logging

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
            result = self.model.transcribe(filepath)
            transcription_text = result['text']

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
            logging.error(f"Error during transcription: {e}")
            return f"Error: {e}\n"
