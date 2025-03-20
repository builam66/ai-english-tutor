import io
import edge_tts
import pyaudiowpatch as pyaudio
from pydub import AudioSegment

def get_speaker(configs):
    return EdgeTTSSpeaker(configs)

class EdgeTTSSpeaker:
    def __init__(self, configs):
        self.configs = configs
        self.chunk = pyaudio.get_sample_size(pyaudio.paInt16)
        self.is_speaking = False

    async def speak_text(self, text):
        if not self.is_speaking:
            self.is_speaking = True
            bytestream = io.BytesIO()
            communicate = edge_tts.Communicate(text, self.configs.voice_model)
            async for chunk in communicate.stream():
                if "data" in chunk:
                    bytestream.write(chunk["data"])
            bytestream.seek(0)
            # Convert MP3 to raw PCM
            audio_segment = AudioSegment.from_file(bytestream, format="mp3")
            raw_audio = audio_segment.raw_data
            # Play audio using PyAudio
            pya = pyaudio.PyAudio()
            stream = pya.open(format=pya.get_format_from_width(audio_segment.sample_width),
                              channels=audio_segment.channels,
                              rate=audio_segment.frame_rate,
                              output=True)
            stream.write(raw_audio)
            stream.stop_stream()
            stream.close()
            pya.terminate()
            self.is_speaking = False