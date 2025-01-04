import whisper
import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


class AudioTranscriber:
    def __init__(self):
        self.model = whisper.load_model("small")

    def transcribe_audio(self, filepath):
        result = self.model.transcribe(filepath)
        with open("transcription.txt", "w") as f:
            f.write(result["text"])
        logging.info("Transcription saved to transcription.txt")
