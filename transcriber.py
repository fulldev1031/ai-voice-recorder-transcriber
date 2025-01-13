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
        try:
            self.model = whisper.load_model("small")
            logging.info("Whisper model loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading Whisper model: {e}")
            self.model = None
        self.transcription_file = None
        self.segments_with_confidence = []

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

            # Transcribe with word timestamps
            logging.info("Starting transcription...")
            result = self.model.transcribe(
                audio_data, 
                language='en',
                word_timestamps=True
            )
            
            # Process segments with confidence scores
            segments = result.get('segments', [])
            
            if not segments:
                return "Error: No speech detected in the audio file.\n"
            
            # Format output with confidence scores
            output_lines = []
            output_lines.append("TRANSCRIPTION WITH CONFIDENCE SCORES")
            output_lines.append("=" * 40)
            output_lines.append("")

            for segment in segments:
                timestamp = f"[{self._format_time(segment['start'])} - {self._format_time(segment['end'])}]"
                
                # Calculate confidence for this segment
                confidence = self._calculate_segment_confidence(segment)
                confidence_str = f"({confidence:.1%} confidence)"
                
                text = segment['text'].strip()
                
                output_lines.extend([
                    timestamp,
                    confidence_str,
                    text,
                    "-" * 40,
                    ""
                ])
            
            return "\n".join(output_lines)
            
        except Exception as e:
            error_msg = f"Error during transcription: {str(e)}"
            logging.error(error_msg)
            return f"Error: {error_msg}\n"

    def _calculate_segment_confidence(self, segment):
        """Calculate confidence score for a segment based on word-level probabilities."""
        if 'words' in segment and segment['words']:
            # If word-level probabilities are available, use their average
            word_probs = []
            for word in segment['words']:
                # Handle both possible formats of word confidence
                prob = word.get('probability', word.get('confidence', 0.0))
                word_probs.append(prob)
            return sum(word_probs) / len(word_probs) if word_probs else 0.75
        return 0.75  # Default confidence if no word-level data available

    def _format_time(self, seconds):
        """Convert seconds to MM:SS format"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

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