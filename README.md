# 🔊 ai-voice-recorder-transcriber

This project is an interactive desktop application that allows users to record audio in real-time, save the recordings, and transcribe the audio to text using the Whisper AI model. The user-friendly interface is built with Tkinter, making it easy to start and stop recordings and generate transcriptions with just a few clicks.

This Python-based GUI application allows you to record audio, save it as a `.wav` file, and transcribe it into text using OpenAI's Whisper model. Built with `tkinter`, it features buttons to start/stop recording and transcribe audio, saving the recording as `output.wav` and the transcription as `transcription.txt`.

## 🔥 Features

1. _Real-Time Audio Recording:_
   Users can start and stop audio recordings with the click of a button. Audio is captured using PyAudio, ensuring high-quality recordings.

2. _Audio File Management:_
   Recorded audio is saved in WAV format for compatibility and quality retention. Automatic file saving upon stopping the recording.

3. _AI-Powered Transcription:_
   Uses Whisper, an advanced speech-to-text model, to transcribe recorded audio. Transcription results are saved to a text file for easy access and further use.

4. _User-Friendly Interface:_
   Built with Tkinter, the application provides a simple, clean, and responsive interface. Buttons are styled for ease of use and accessibility.

## 🛠️ Installation

1. **Fork this repository:** Fork the `fulldev1031/ai-voice-recorder-transcriber` repository. Follow these instructions on [how to fork a repository](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo)

2. **Clone the project:** `git clone git@github.com:your-username/ai-voice-recorder-transcriber`

3. **Required downloads:**

```bash
  cd ai-voice-recorder-transcriber
  pip install -r requirements.txt
```

4. **Alternative ways to download the dependencies:**

- To run, install Python 3.8+ and required packages (`pyaudio` and `whisper`) using

```bash
pip install pyaudio whisper
```

- Whisper downloads its models on the first run; ensure an active internet connection. Customize the Whisper model by modifying `whisper.load_model("small")` in the code (options: tiny, base, small, medium, large).

- For more on Whisper, visit https://github.com/openai/whisper.

5. **Running the project:**
   Run the application with :

```bash
   python ui.py
```

## 🚀 How It Works

- Start Recording: Click the "Start Recording" button to begin capturing audio. The button will be disabled while recording is in progress.
- Stop Recording: Click the "Stop Recording" button to end the audio capture. The application saves the audio to a file and enables the transcription feature.
- Transcribe Audio: Click the "Transcribe" button to convert the recorded audio into text. The transcribed text is saved to a file named transcription.txt.

## 🙌 Contributing

Contributions are always welcome! Whether you want to report an issue, suggest a feature, or submit a pull request, your input is greatly appreciated.

## 🧑💻 Contributor's Guide

Welcome, contributors! Here's how you can help improve this project:

### **Getting Started**
1. **Fork the Repository**: Click "Fork" at the top right of the GitHub repository page.
2. **Clone Your Fork**:
```bash
git clone https://github.com/your-username/ai-voice-recorder-transcriber.git
```
3. **Create a Feature Branch**:
```bash
git checkout -b feature/your-feature-name
```

### **Coding Guidelines**
- Follow PEP 8 style guidelines for Python code.
- Add comments for complex logic.
- Write tests for new features (if applicable).
-Test changes locally before submitting a pull request.

### **Pull Request Process**
- Ensure your branch is updated with the latest `main` branch.
- Submit a PR to the original repository's `main` branch.
- Describe your changes clearly in the PR description.
- Address any review feedback promptly.

## 📚 Examples & Tutorials

### **Changing the Whisper Model Size**
Modify `ui.py` to use a different model (e.g., "medium"):
```python
model = whisper.load_model("medium")  # Instead of "small"
```

### **Customizing File Save Paths**
Change where files are saved by editing these lines in `ui.py`:
```python
# For audio files
wf = wave.open("custom_folder/output.wav", 'wb')

# For transcriptions
with open("custom_folder/transcription.txt", "w") as f:
```

## ❓ FAQ (Troubleshooting)
**Q: I get errors installing PyAudio on Windows.**
A: Try installing using pre-built binaries:
```bash
pip install pipwin
pipwin install pyaudio
```

**Q: Whisper fails to download models.**
A: Ensure you have an active internet connection. If blocked by a firewall, manually download the model from OpenAI's repository and place it in `~/.cache/whisper/`.

**Q: "Permission denied" when saving files.**
A: Run the app as administrator/root, or change the save directory to a location with write permissions.

## 🛡️ Error-Handling Best Practices
- **User Feedback**: The GUI shows error messages in alerts instead of console logs.
- **Exception Handling**: Contributors should wrap risky operations in try-except blocks:
```python
try:
    # Risky code
except Exception as e:
    messagebox.showerror("Error", str(e))
```
- **Logging**: Consider adding logging for debugging (PRs welcome!).

## 🚧 Future Features & Roadmap
### **Planned Features**
- Real-time transcription while recording.
- Support for MP3 and other audio formats.
- Language selection for transcription.
- Progress bar during transcription.

### **In Progress**
- GUI dark/light theme toggle (WIP by @contributor).

## ⭐️ Acknowledgements

A very big thanks to all the contributors for helping this project grow. Your efforts are greatly appreciated!
