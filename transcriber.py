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
        self.confidence_file = None

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
            
            # Process segments
            segments = result.get('segments', [])
            
            if not segments:
                return "Error: No speech detected in the audio file.\n"
            
            # Prepare both clean transcription and detailed version
            clean_transcription = []
            detailed_transcription = []
            
            # Add header to detailed version
            detailed_transcription.extend([
                "TRANSCRIPTION WITH CONFIDENCE SCORES",
                "=" * 40,
                ""
            ])

            for segment in segments:
                # Clean version just has the text
                clean_transcription.append(segment['text'].strip())
                
                # Detailed version has timestamps and confidence
                timestamp = f"[{self._format_time(segment['start'])} - {self._format_time(segment['end'])}]"
                confidence = self._calculate_segment_confidence(segment)
                confidence_str = f"({confidence:.1%} confidence)"
                
                detailed_transcription.extend([
                    timestamp,
                    confidence_str,
                    segment['text'].strip(),
                    "-" * 40,
                    ""
                ])
            
            # Save both versions
            if save_directory:
                clean_file = os.path.join(save_directory, "output_transcription.txt")
                conf_file = os.path.join(save_directory, "output_transcription_detailed.txt")
            else:
                clean_file = "output_transcription.txt"
                conf_file = "output_transcription_detailed.txt"
                
            # Save clean version
            with open(clean_file, "w", encoding="utf-8") as f:
                f.write("\n".join(clean_transcription))
            self.transcription_file = clean_file
                
            # Save detailed version
            with open(conf_file, "w", encoding="utf-8") as f:
                f.write("\n".join(detailed_transcription))
            self.confidence_file = conf_file
            
            logging.info(f"Transcription saved to {clean_file}")
            logging.info(f"Detailed transcription saved to {conf_file}")
            
            # Return the detailed version for display
            return "\n".join(detailed_transcription)
            
        except Exception as e:
            error_msg = f"Error during transcription: {str(e)}"
            logging.error(error_msg)
            return f"Error: {error_msg}\n"

    def _calculate_segment_confidence(self, segment):
        """Calculate confidence score for a segment based on word-level probabilities."""
        if 'words' in segment and segment['words']:
            word_probs = []
            for word in segment['words']:
                prob = word.get('probability', word.get('confidence', 0.0))
                word_probs.append(prob)
            return sum(word_probs) / len(word_probs) if word_probs else 0.75
        return 0.75

    def _format_time(self, seconds):
        """Convert seconds to MM:SS format"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def save_transcription(self, text, save_directory=None):
        """This method is kept for compatibility but now only updates the files if needed"""
        try:
            if save_directory and self.transcription_file:
                new_file = os.path.join(save_directory, os.path.basename(self.transcription_file))
                if new_file != self.transcription_file:
                    shutil.copy2(self.transcription_file, new_file)
                    self.transcription_file = new_file
                    
            if save_directory and self.confidence_file:
                new_conf_file = os.path.join(save_directory, os.path.basename(self.confidence_file))
                if new_conf_file != self.confidence_file:
                    shutil.copy2(self.confidence_file, new_conf_file)
                    self.confidence_file = new_conf_file
                    
            return True
        except Exception as e:
            logging.error(f"Error saving transcription: {e}")
            return False

    def rename_transcription(self, new_name):
        try:
            if not self.transcription_file or not os.path.exists(self.transcription_file):
                logging.error("No transcription file exists to rename")
                return False
            
            directory = os.path.dirname(self.transcription_file)
            
            # Rename clean transcription
            new_filepath = os.path.join(directory, f"{new_name}_transcription.txt")
            shutil.move(self.transcription_file, new_filepath)
            self.transcription_file = new_filepath
            
            # Rename detailed transcription if it exists
            if self.confidence_file and os.path.exists(self.confidence_file):
                new_conf_filepath = os.path.join(directory, f"{new_name}_transcription_detailed.txt")
                shutil.move(self.confidence_file, new_conf_filepath)
                self.confidence_file = new_conf_filepath
            
            logging.info(f"Transcription files renamed with prefix: {new_name}")
            return True
            
        except Exception as e:
            error_msg = f"Error renaming transcription file: {str(e)}"
            logging.error(error_msg)
            return False