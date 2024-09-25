import subprocess
import os
from groq import Groq
import keyboard


class Hear:
    def __init__(self):
        self.recorder = None
        self.command = [
            "ffmpeg",
            "-f",
            "dshow",
            "-i",
            "audio=Headset (Jabra Elite 7 Pro)",
            "output.wav",
        ]

    def start(self, API_KEY, prompt="Specify Context", temperature=0):
        process = subprocess.Popen(self.command)
        print("press 'q to stop recording'")
        keyboard.wait("q")
        process.terminate()
        client = Groq(api_key=API_KEY)
        current_dir = os.getcwd()
        filename = current_dir + "\\output.wav"
        with open(filename, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(filename, file.read()),
                model="whisper-large-v3",
                prompt=prompt,
                response_format="json",
                language="en",
                temperature=temperature,
            )

            print(transcription.text)


if __name__ == "__main__":
    hear = Hear()
    API_KEY = "Write your own API"
    x = input(API_KEY)
    hear.start(API_KEY=x)
