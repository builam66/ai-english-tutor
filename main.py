import asyncio
import os
import sys
import tempfile
import threading
import wave
import eng_to_ipa as ipa
import customtkinter as ctk
import pyaudiowpatch as pyaudio
from dotenv import load_dotenv
from ChatResponder import AIResponder
from Common import INIT_QUESTION
from Speaker import EdgeTTSSpeaker
from SpellingChecker import AIChecker
from SettingFrame import SettingFrame
from Transcriber import get_transcriber

# A bigger audio buffer gives better accuracy
# but also increases latency in response.
# AUDIO_BUFFER = 5

class LanguageApp(ctk.CTk):
    def __init__(self, default_micro, pya):
        super().__init__()

        
        self.title("Language Input App")
        self.geometry("1200x600")
        
        self.stream = None
        self.record_thread = threading.Event()
        self.frames = []
        self.filename = ''
        self.configs = None
        self.default_micro = default_micro
        self.pya = pya
        
        self.transcriber = None
        self.checker = None
        self.responder = None
        self.speaker = None
        
        self.question = INIT_QUESTION
        self.answer = ""
        
        self.messages = []
        
        # Language Input Frame
        self.setting_frame = SettingFrame(self)
        self.setting_frame.pack(padx=10, pady=5, fill="x")

        # Row 5: Record and Clear Buttons Frame
        self.row5_frame = ctk.CTkFrame(self)
        self.row5_frame.pack(padx=10, pady=5, fill="x")

        self.init_button = ctk.CTkButton(self.row5_frame, text="Initialize", command=self.initialize)
        self.init_button.pack(side="left", padx=10)
        
        self.record_button = ctk.CTkButton(self.row5_frame, text="Record", command=self.toggle_record)
        self.record_button.pack(side="left", padx=10)

        self.clear_button = ctk.CTkButton(self.row5_frame, text="Test Voice", command=self.test_speaker_voice)
        self.clear_button.pack(side="left", padx=10)
        
        self.status_box = ctk.CTkTextbox(self.row5_frame, height=1, state="disabled")
        self.status_box.pack(side="left", padx=10, fill="both", expand=True)

        # Row 6: Textboxes for output Frame
        self.row6_frame = ctk.CTkFrame(self)
        self.row6_frame.pack(padx=10, pady=5, fill="both", expand=True)

        # self.response_box = ctk.CTkTextbox(self.row6_frame, font=("Arial", 16), height=10)
        # self.response_box.pack(side="left", padx=10, pady=10, fill="both", expand=True)
        # self.transcript_box = ctk.CTkTextbox(self.row6_frame, font=("Arial", 16), width=300, height=10)
        # self.transcript_box.pack(side="left", padx=10, pady=10, fill="both")
        
        # Chat Display Area
        self.chat_frame = ctk.CTkScrollableFrame(self.row6_frame, width=600)
        self.chat_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)
        
        self.suggest_box = ctk.CTkTextbox(self.row6_frame, font=("Arial", 16), height=10)
        self.suggest_box.pack(side="left", padx=10, pady=10, fill="both", expand=True)
        
        # Row 7: Textboxes for ipa
        self.row7_frame = ctk.CTkFrame(self)
        self.row7_frame.pack(padx=10, pady=5, fill="x")
        self.selected_ipa_box = ctk.CTkTextbox(self.row7_frame, font=("Arial", 12), height=50)
        self.selected_ipa_box.pack(side="left", padx=10, fill="both", expand=True)
        
        # Bind the "`" key to toggle_record
        self.bind_all("`", lambda event: self.record_button.invoke())

    def toggle_record(self):
        current_text = self.record_button.cget("text")
        new_text = "Stop" if current_text == "Record" else "Record"
        self.record_button.configure(text=new_text)
        
        if new_text == "Stop":
            self.update_status("[INFO] Recording...")
            
            audio_format = pyaudio.paInt16
            channels = self.default_micro["maxInputChannels"]
            frame_rate = int(self.default_micro["defaultSampleRate"])
            chunk = pyaudio.get_sample_size(pyaudio.paInt16)
            device_index = self.default_micro["index"]
            # record_seconds = 10

            self.stream = self.pya.open(
                format=audio_format,
                channels=channels,
                rate=frame_rate,
                frames_per_buffer=chunk,
                input=True,
                input_device_index=device_index,
                # stream_callback=callback,
            )
            
            self.record_thread.set()
            threading.Thread(target=self.record_loop).start()
            
        else:
            self.update_status("[INFO] Transcribing...")
            self.record_thread.clear()
            
    def record_loop(self):
        while self.record_thread.is_set():
            data = self.stream.read(pyaudio.get_sample_size(pyaudio.paInt16))
            self.frames.append(data)
        
        self.stream.stop_stream()
        self.stream.close()
        self.stream = None
        
        with tempfile.NamedTemporaryFile(suffix=".wav", dir="D:\\TEMP\\transcribe", delete=False) as f:
            self.filename = f.name
            wave_file = wave.open(f.name, "wb")
            wave_file.setnchannels(self.default_micro["maxInputChannels"])
            wave_file.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
            wave_file.setframerate(int(self.default_micro["defaultSampleRate"]))
            wave_file.writeframes(b''.join(self.frames))
            wave_file.close()
            
        transcribe_text = self.transcriber.get_transcription(self.filename)
        # check for spelling and response
        if self.checker is not None and self.responder is not None:
            self.answer = self.checker.get_response(self.question, transcribe_text)
            self.question = self.responder.get_response(self.answer)
            self.update_response(self.question, ipa.convert(self.question))
            
        os.remove(self.filename)
        self.filename = ''
        self.frames = []
        self.update_status("")
        
        
    def initialize(self):
        # Load env
        load_dotenv()
        # Get all configs
        self.configs = self.setting_frame.get_values()
        print(str(self.configs))
        # transcriber
        self.transcriber = get_transcriber(self.configs, self.update_status)
        # checker
        if self.configs.checker_model != "none":
            self.checker = AIChecker(
                configs=self.configs,
                update_transcript=self.update_transcript,
                update_suggest=self.update_suggest,
                update_status=self.update_status)
        else:
            self.checker = None
        # responder
        if self.configs.ai_model != "none":
            self.responder = AIResponder(
                configs=self.configs,
                update_response=self.update_response,
                update_status=self.update_status)
        else:
            self.responder = None
        self.speaker = EdgeTTSSpeaker(configs=self.configs)
            
        self.update_response(INIT_QUESTION, ipa.convert(INIT_QUESTION))

    def test_speaker_voice(self):
        threading.Thread(target=lambda: asyncio.run(self.speaker.speak_text(INIT_QUESTION)), daemon=True).start()
        # self.transcript_box.delete("1.0", ctk.END)
        # self.response_box.delete("1.0", ctk.END)
        # self.suggest_box.delete("1.0", ctk.END)
        
    def update_response(self, response_text, response_ipa):
        if response_text is None:
            return
        # self.response_box.delete("1.0", ctk.END)
        # self.response_box.insert(ctk.END, f"[TUTOR] {response_text} \n")
        # self.response_box.insert(ctk.END, f"[====>] {response_ipa} \n\n")
        self.display_message(sender="AI", message=response_text)
        threading.Thread(target=lambda: asyncio.run(self.speaker.speak_text(response_text)), daemon=True).start()
        
    def update_transcript(self, transcript_text, transcript_ipa):
        if transcript_text is None:
            return
        # self.transcript_box.delete("1.0", ctk.END)
        # self.transcript_box.insert(ctk.END, f"[YOU] {transcript_text} \n")
        # self.transcript_box.insert(ctk.END, f"[==>] {transcript_ipa} \n\n")
        self.display_message(sender="YOU", message=transcript_text)
        
    def update_suggest(self, point, transcript_text, transcript_ipa, suggest_text, suggest_ipa, suggest_explain):
        if suggest_text is None:
            return
        self.suggest_box.delete("1.0", ctk.END)
        self.suggest_box.insert(ctk.END, f"[POINT] {point}% \n\n")
        self.suggest_box.insert(ctk.END, f"[TRANSCRIPT] {transcript_text} \n")
        self.suggest_box.insert(ctk.END, f"[=========>] {transcript_ipa} \n\n")
        self.suggest_box.insert(ctk.END, f"[SUGGEST] {suggest_text} \n")
        self.suggest_box.insert(ctk.END, f"[======>] {suggest_ipa} \n\n")
        self.suggest_box.insert(ctk.END, f"[======>] {suggest_explain} \n\n")
        
    def update_status(self, status):
        print(status)
        self.status_box.configure(state="normal")
        self.status_box.delete("1.0", ctk.END)
        self.status_box.insert(ctk.END, status)
        self.status_box.configure(state="disabled")
        
    def display_message(self, sender, message):
        message_frame = ctk.CTkFrame(self.chat_frame, fg_color="black" if sender == "AI" else "blue", corner_radius=10)
        message_frame.pack(pady=5, padx=5, anchor="w" if sender == "AI" else "e")

        max_wrap_length = self.chat_frame.winfo_width() - 50
        label = ctk.CTkLabel(message_frame, text=f"{message}", font=("Arial", 16), text_color="white", wraplength=max_wrap_length, anchor="w", justify="left")
        label.pack(padx=5, pady=5)

        label.bind("<Button-1>", lambda e, msg=message: self.show_selected_ipa(e, msg))

        self.messages.append(message_frame)
        self.chat_frame.update_idletasks()
        self.chat_frame._parent_canvas.yview_moveto(1)
        self.chat_frame._parent_canvas.update_idletasks()
    
    def show_selected_ipa(self, event, message):
        message_ipa = ipa.convert(message)
        self.selected_ipa_box.delete("1.0", ctk.END)
        self.selected_ipa_box.insert(ctk.END, f"{message_ipa}")
        threading.Thread(target=lambda: asyncio.run(self.speaker.speak_text(message)), daemon=True).start()

        
def main():
    with pyaudio.PyAudio() as pya: # Create PyAudio instance via context manager.
        try:
            wasapi_info = pya.get_host_api_info_by_type(pyaudio.paWASAPI) # Get default WASAPI info
        except OSError:
            print("[ERROR] Looks like WASAPI is not available on the system. Exiting...")
            sys.exit()
        
        default_micro_index = pya.get_default_input_device_info()['index']
        default_micro = pya.get_device_info_by_index(default_micro_index)

        print(f"[INFO] Recording from: {default_micro['name']} ({default_micro['index']})\n")

        app = LanguageApp(default_micro, pya)
        app.mainloop()
    

if __name__ == "__main__":
    main()