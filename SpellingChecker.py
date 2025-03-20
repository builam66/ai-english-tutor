import os
import json
import eng_to_ipa as ipa
from openai import OpenAI
from Common import create_base_prompt, create_prompt, INIT_QUESTION, INIT_ANSWER, calc_match_percent

class AIChecker:
    def __init__(self, configs, update_transcript, update_suggest, update_status):
        self.model = None
        self.update_transcript = update_transcript
        self.update_suggest = update_suggest
        self.update_status = update_status
        self.configs = configs
        self.current_question = INIT_QUESTION
        self.current_answer = INIT_ANSWER
        
        if self.configs.checker_model == "gpt-4o-mini":
            self.model = OpenAIChecker(configs=self.configs)
        # TODO: DEEPSEEK
        
        self.update_status(f"[INFO] AIChecker: {self.configs.checker_model} - {self.configs.eng_level}")
        
    def get_response(self, generated_question = "", transcript_answer = ""):
        if self.model is None :
            return ""
        if transcript_answer == "":
            return ""
        if generated_question == "":
            generated_question = INIT_QUESTION
        
        self.current_question = generated_question
        self.current_answer = transcript_answer
        
        generated_response = self.model.generate_response(
            question=self.current_question,
            answer=self.current_answer)
        corrected_answer = self.process_response(response=generated_response)
        
        return corrected_answer
        
    def process_response(self, response: str):
        json_response = json.loads(response)
        
        corrected_answer = json_response["corrected_answer"]
        corrected_answer_ipa = ipa.convert(corrected_answer)
        self.update_transcript(
            transcript_text=corrected_answer,
            transcript_ipa=corrected_answer_ipa)
        
        transcribe_answer = self.current_answer
        transcribe_answer_ipa = ipa.convert(transcribe_answer)
        suggested_answer = json_response["suggested_answer"]
        suggested_answer_ipa = ipa.convert(suggested_answer)
        suggested_answer_description = json_response["suggested_answer_description"]
        matching_percent = calc_match_percent(corrected_answer_ipa, transcribe_answer_ipa) * 100
        self.update_suggest(
            suggest_text=suggested_answer,
            suggest_ipa=suggested_answer_ipa,
            suggest_explain=suggested_answer_description,
            transcript_text=transcribe_answer,
            transcript_ipa=transcribe_answer_ipa,
            point=matching_percent)
            
        return corrected_answer
    
        
class OpenAIChecker:
    def __init__(self, configs):
        self.configs = configs
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)

    def generate_response(self, question, answer):
        try:
            response = self.client.chat.completions.create(
                model=self.configs.checker_model,
                messages=[
                    {
                        "role": "developer",
                        "content": create_base_prompt(self.configs.eng_level),
                    },
                    {
                        "role": "user",
                        "content": create_prompt(question, answer),
                    }
                ],
                temperature=0.0,
                stream=False)
        except Exception as e:
            print(f"[ERROR] {e}")
            return ''
            
        return response.choices[0].message.content