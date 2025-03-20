import os
import torch
from openai import OpenAI
from faster_whisper import WhisperModel as whisper
from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)

def get_transcriber(configs, update_status):
    return WhisperTranscriber(configs, update_status)

class WhisperTranscriber:
    def __init__(self, configs, update_status):
        self.configs = configs
        # audio_model = whisper.load_model(os.path.join(os.getcwd(), 'tiny.en.pt'))
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # self.recognize_model = "small.en"
        self.recognize_model = "medium.en"
        if self.configs.recognize_level == "medium":
            self.recognize_model = "base.en"
        if self.configs.recognize_level == "hard":
            self.recognize_model = "tiny.en"
        
        self.model = whisper(self.recognize_model, device=device) # compute_type="float32"
        update_status(f"[INFO] Offline Whisper loaded... {device} - {self.configs.recognize_level} - {self.recognize_model}")

    def get_transcription(self, wav_file_path):
        try:
            segments, info = self.model.transcribe(wav_file_path, beam_size=5, language="en") # task="translate"
            transcribe_text = "".join(segment.text.strip() for segment in segments)
        except Exception as e:
            print(f"[ERROR] {e}")
            return ''
        return transcribe_text