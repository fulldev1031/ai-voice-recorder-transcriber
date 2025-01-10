
# 🔊 ai-voice-recorder-transcriber

This project is an interactive desktop application that allows users to record audio in real-time, save the recordings, and transcribe the audio to text using the Whisper AI model. The user-friendly interface is built with Tkinter, making it easy to start and stop recordings and generate transcriptions with just a few clicks.

This Python-based GUI application allows you to record audio, save it as a `.wav` file, and transcribe it into text using OpenAI's Whisper model. Built with `tkinter`, it features buttons to start/stop recording and transcribe audio, saving the recording as `output.wav` and the transcription as `transcription.txt`.

## 🔥 Features
1. *Real-Time Audio Recording:*
Users can start and stop audio recordings with the click of a button. Audio is captured using PyAudio, ensuring high-quality recordings.

2. *Audio File Management:*
Recorded audio is saved in WAV format for compatibility and quality retention. Automatic file saving upon stopping the recording. 

3. *AI-Powered Transcription:*
Uses Whisper, an advanced speech-to-text model, to transcribe recorded audio. Transcription results are saved to a text file for easy access and further use.

4. *User-Friendly Interface:*
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
* Start Recording: Click the "Start Recording" button to begin capturing audio. The button will be disabled while recording is in progress. 
* Stop Recording: Click the "Stop Recording" button to end the audio capture. The application saves the audio to a file and enables the transcription feature.
* Transcribe Audio: Click the "Transcribe" button to convert the recorded audio into text. The transcribed text is saved to a file named transcription.txt.


## 🙌 Contributing

Contributions are always welcome! Whether you want to report an issue, suggest a feature, or submit a pull request, your input is greatly appreciated.

### **To Contribute:**
- Fork this repository.
- Create a new branch for your feature or bug fix (`git checkout -b feature-name`).
- Commit your changes with a clear message.
- Push your branch and open a pull request.

Please ensure your contributions align with the project's goals and follow the coding style. For major changes, kindly open an issue first to discuss your ideas.

Thank you for contributing! 🎉



## ⭐️ Acknowledgements
A very big thanks to all the contributors for helping this project grow!

<a href="https://github.com/fulldev1031/ai-voice-recorder-transcriber/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=fulldev1031/ai-voice-recorder-transcriber" />
</a>
<!-- [![Contributors](https://contrib.rocks/preview?repo=fulldev1031%2Fai-voice-recorder-transcriber)](https://github.com/fulldev1031/ai-voice-recorder-transcriber/graphs/contributors) -->

