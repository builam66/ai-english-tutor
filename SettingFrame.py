import json
from pathlib import Path
import customtkinter as ctk
from Common import recognize_levels, ai_response_models, ai_checker_models

class SettingFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.row1_frame = ctk.CTkFrame(self)
        self.row1_frame.pack(padx=10, pady=5, fill="x")

        self.topic = ctk.CTkEntry(self.row1_frame, placeholder_text="Topic: software engineer working environment") # state='disabled'
        self.topic.pack(side="left", padx=10, fill="x", expand=True)
        
        self.eng_level = ctk.CTkEntry(self.row1_frame, placeholder_text="Eng Level: A0 to B2") # state='disabled'
        self.eng_level.pack(side="left", padx=10, fill="x", expand=True)

        self.row2_frame = ctk.CTkFrame(self)
        self.row2_frame.pack(padx=10, pady=5, fill="x")
        
        self.recognize_levels_label = ctk.CTkLabel(self.row2_frame, text="Recognize Level:")
        self.recognize_levels_label.pack(side="left", padx=10)
        default_recognize_level = ctk.StringVar(value=recognize_levels[0])
        self.recognize_levels = ctk.CTkOptionMenu(self.row2_frame, values=recognize_levels, variable=default_recognize_level)
        self.recognize_levels.pack(side="left", padx=[0, 10])
        
        self.ai_checker_label = ctk.CTkLabel(self.row2_frame, text="Checker Model:")
        self.ai_checker_label.pack(side="left", padx=10)
        default_ai_checker = ctk.StringVar(value=ai_checker_models[0])
        self.ai_checker_dropdown = ctk.CTkOptionMenu(self.row2_frame, values=ai_checker_models, variable=default_ai_checker)
        self.ai_checker_dropdown.pack(side="left", padx=[0, 10])
        
        self.ai_api_label = ctk.CTkLabel(self.row2_frame, text="Response Model:")
        self.ai_api_label.pack(side="left", padx=10)
        default_ai_response = ctk.StringVar(value=ai_response_models[0])
        self.ai_api_dropdown = ctk.CTkOptionMenu(self.row2_frame, values=ai_response_models, variable=default_ai_response)
        self.ai_api_dropdown.pack(side="left", padx=[0, 10])
        
        self.voice_model_label = ctk.CTkLabel(self.row2_frame, text="Voice Model:")
        self.voice_model_label.pack(side="left", padx=10)
        voices_data = json.loads(Path('en_voices.json').read_text())
        voices_options = [item['ShortName'] for item in voices_data]
        default_voice_option = ctk.StringVar(value=voices_options[0])
        self.voice_model_dropdown = ctk.CTkOptionMenu(self.row2_frame, values=voices_options, variable=default_voice_option)
        self.voice_model_dropdown.pack(side="left", padx=[0, 10])
        
    def get_values(self):
        topic = self.topic.get()
        eng_level = self.eng_level.get()
        recognize_level = self.recognize_levels.get()
        checker_model = self.ai_checker_dropdown.get()
        ai_model = self.ai_api_dropdown.get()
        voice_model = self.voice_model_dropdown.get()

        return Setting(topic, eng_level, recognize_level, checker_model, ai_model, voice_model)
        
class Setting:
    def __init__(self, topic, eng_level, recognize_level, checker_model, ai_model, voice_model):
        self.topic = topic
        self.eng_level = eng_level
        self.recognize_level = recognize_level
        self.checker_model = checker_model
        self.ai_model = ai_model
        self.voice_model = voice_model