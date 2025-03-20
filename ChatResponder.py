import os
from google import genai
from google.genai import types
from Common import create_chat_prompt

class AIResponder:
    def __init__(self, configs, update_response, update_status):
        self.model = None
        self.update_response = update_response
        self.update_status = update_status
        self.configs = configs

        # if ai_model == "gpt-4o-mini":
        #     self.model = OpenAIResponder(model_name=ai_model)
        if self.configs.ai_model == "gemini-2.0-flash":
            self.model = GeminiAIResponder(configs=self.configs)
        # TODO: DEEPSEEK
        
        self.update_status(f"[INFO] AIResponder: {self.configs.ai_model}")

    def get_response(self, message):
        if self.model is None :
            return ""

        generated_response = self.model.generate_response(message=message)
        return generated_response


class GeminiAIResponder:
    def __init__(self, configs):
        self.configs = configs
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key)

    def generate_response(self, message):
        try:
            response = self.client.models.generate_content(
                model=self.configs.ai_model,
                config=types.GenerateContentConfig(
                    system_instruction=create_chat_prompt(self.configs.topic, self.configs.eng_level),
                    # max_output_tokens=500,
                    temperature=0.0,
                ),
                contents=[message])
        except Exception as e:
            print(f"[ERROR] {e}")
            return ''

        return response.text