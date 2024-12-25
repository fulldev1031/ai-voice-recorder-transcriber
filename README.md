# ai-voice-recorder-transcriber

This project is an interactive desktop application that allows users to record audio in real-time, save the recordings, and transcribe the audio to text using the Whisper AI model. The user-friendly interface is built with Tkinter, making it easy to start and stop recordings and generate transcriptions with just a few clicks.

Features:

Real-Time Audio Recording:

Users can start and stop audio recordings with the click of a button.
Audio is captured using PyAudio, ensuring high-quality recordings.
Audio File Management:

Recorded audio is saved in WAV format for compatibility and quality retention.
Automatic file saving upon stopping the recording.
AI-Powered Transcription:

Uses Whisper, an advanced speech-to-text model, to transcribe recorded audio.
Transcription results are saved to a text file for easy access and further use.
User-Friendly Interface:

Built with Tkinter, the application provides a simple, clean, and responsive interface.
Buttons are styled for ease of use and accessibility.
How It Works:

Start Recording:

Click the "Start Recording" button to begin capturing audio.
The button will be disabled while recording is in progress.
Stop Recording:

Click the "Stop Recording" button to end the audio capture.
The application saves the audio to a file and enables the transcription feature.
Transcribe Audio:

Click the "Transcribe" button to convert the recorded audio into text.
The transcribed text is saved to a file named transcription.txt.
Technical Implementation:

The application uses PyAudio for audio capture and handling, ensuring seamless recording functionality.
Whisper AI, a state-of-the-art speech recognition model, is used for transcription, providing accurate and reliable text conversion.
Tkinter is used to create a user-friendly graphical interface, making the application accessible to users with no technical background.

This Python-based GUI application allows you to record audio, save it as a `.wav` file, and transcribe it into text using OpenAI's Whisper model. Built with `tkinter`, it features buttons to start/stop recording and transcribe audio, saving the recording as `output.wav` and the transcription as `transcription.txt`. To run, install Python 3.8+ and required packages (`pyaudio` and `whisper`) using `pip install pyaudio whisper`. If `pyaudio` installation fails, download a pre-built wheel from [https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio). Whisper downloads its models on the first run; ensure an active internet connection. Customize the Whisper model by modifying `whisper.load_model("small")` in the code (options: tiny, base, small, medium, large). For more on Whisper, visit [https://github.com/openai/whisper](https://github.com/openai/whisper). Run the application with `python audio_recorder.py`, and use the GUI to record and transcribe audio seamlessly.
