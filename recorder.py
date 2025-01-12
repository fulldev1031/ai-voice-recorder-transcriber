import pyaudio
import wave
import threading
import logging
import os
from typing import Optional, List
import time

class AudioRecorder:
    def __init__(self):
        self.setup_logging()
        self.initialize_audio()
        self.stream: Optional[pyaudio.Stream] = None
        self.frames: List[bytes] = []
        self.recording: bool = False
        self.audio_thread: Optional[threading.Thread] = None
        self.save_directory: Optional[str] = None
        self.filepath: Optional[str] = None
        self.error_occurred: bool = False

    def setup_logging(self):
        """Initialize logging configuration"""
        try:
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler("recorder.log"),
                    logging.StreamHandler()
                ]
            )
        except Exception as e:
            print(f"Failed to initialize logging: {e}")
            raise

    def initialize_audio(self):
        """Initialize PyAudio with error handling"""
        try:
            self.audio = pyaudio.PyAudio()
            
            test_stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=1024,
            )
            test_stream.close()
        except Exception as e:
            logging.error(f"Failed to initialize audio: {e}")
            raise RuntimeError(f"Audio initialization failed: {e}")

    def set_save_directory(self, directory: str):
        """Set save directory with validation"""
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
            if not os.access(directory, os.W_OK):
                raise PermissionError(f"No write permission for directory: {directory}")
            self.save_directory = directory
            logging.info(f"Save directory set to: {directory}")
        except Exception as e:
            logging.error(f"Failed to set save directory: {e}")
            raise

    def start_recording(self):
        """Start audio recording with error handling"""
        if self.recording:
            raise RuntimeError("Recording is already in progress")

        try:
            self.error_occurred = False
            self.frames = []
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=1024,
                stream_callback=self._audio_callback
            )
            
            self.recording = True
            self.audio_thread = threading.Thread(target=self._monitor_recording)
            self.audio_thread.start()
            logging.info("Recording started successfully")
        
        except Exception as e:
            self.recording = False
            if hasattr(self, 'stream') and self.stream:
                try:
                    self.stream.close()
                except:
                    pass
            logging.error(f"Failed to start recording: {e}")
            raise RuntimeError(f"Failed to start recording: {e}")

    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Handle audio stream callback"""
        try:
            if status:
                logging.warning(f"Audio stream status: {status}")
            if self.recording:
                self.frames.append(in_data)
                return (in_data, pyaudio.paContinue)
            return (in_data, pyaudio.paComplete)
        except Exception as e:
            logging.error(f"Audio callback error: {e}")
            self.error_occurred = True
            return (in_data, pyaudio.paAbort)

    def _monitor_recording(self):
        """Monitor recording for errors"""
        while self.recording:
            if self.error_occurred:
                self.stop_recording()
                break
            time.sleep(0.1)

    def stop_recording(self):
        """Stop recording with error handling"""
        if not self.recording:
            logging.warning("No recording in progress")
            return

        try:
            self.recording = False
            
            if self.audio_thread and self.audio_thread.is_alive():
                self.audio_thread.join(timeout=2.0)
                if self.audio_thread.is_alive():
                    logging.warning("Audio thread failed to stop gracefully")

            if self.stream:
                try:
                    self.stream.stop_stream()
                    self.stream.close()
                except Exception as e:
                    logging.error(f"Error closing audio stream: {e}")

            self.save_recording()
            logging.info("Recording stopped successfully")

        except Exception as e:
            logging.error(f"Error stopping recording: {e}")
            raise RuntimeError(f"Failed to stop recording: {e}")

    def save_recording(self):
        """Save recording with error handling"""
        if not self.frames:
            raise ValueError("No audio data to save")

        try:
            
            if self.save_directory:
                self.filepath = os.path.join(self.save_directory, "output.wav")
            else:
                self.filepath = "output.wav"

            
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)

            
            with wave.open(self.filepath, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(44100)
                wf.writeframes(b"".join(self.frames))

            logging.info(f"Recording saved to {self.filepath}")

        except Exception as e:
            logging.error(f"Failed to save recording: {e}")
            raise IOError(f"Failed to save recording: {e}")

    def __del__(self):
        """Cleanup resources"""
        try:
            if hasattr(self, 'recording') and self.recording:
                self.stop_recording()
            
            if hasattr(self, 'stream') and self.stream:
                self.stream.close()
            
            if hasattr(self, 'audio'):
                self.audio.terminate()
                
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")