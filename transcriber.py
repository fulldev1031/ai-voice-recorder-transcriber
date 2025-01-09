import os
import whisper
import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

class AudioTranscriber:
    def __init__(self):
        self.model = whisper.load_model("small")

    def transcribe_audio(self, filepath, save_directory=None):
        result = self.model.transcribe(filepath)
        if save_directory:
            os.makedirs(save_directory, exist_ok=True)  # Ensure the directory exists
            save_path = os.path.join(save_directory, "transcription.txt")
        else:
            save_path = "transcription.txt"

        with open(save_path, "w") as f:
            f.write(result["text"])
        
        logging.info(f"Transcription saved to {save_path}")
