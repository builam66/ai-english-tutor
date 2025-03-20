import re
from difflib import SequenceMatcher

speech_to_text_models = ["offline", "openai-whisper", "deepgram"]
recognize_levels = ["easy", "medium", "hard"] # small - base - tiny
ai_checker_models = ["gpt-4o-mini", "none", "gpt-4o", "deepseek-chat", "gemini-2.0-flash"]
ai_response_models = ["gemini-2.0-flash", "none", "gpt-4o-mini", "gpt-4o", "deepseek-chat"]

INIT_QUESTION = "Hi! How are you today?"
INIT_ANSWER = "I am fine. And you?"

def calc_match_percent(str1, str2):
    format_str1 = re.sub(r'[.,?:; ]', '', str1).strip().replace(" ", "").lower()
    format_str2 = re.sub(r'[.,?:; ]', '', str2).strip().replace(" ", "").lower()
    return SequenceMatcher(None, format_str1, format_str2).ratio()
    
def create_base_prompt(level):
    if level == "" or level is None:
        level = "A0 to B2"
        
    return f"""I want you to act as a speaking teacher and spelling expert. I will provide an original question and its original answer. The original answer is transcribed from an English learner's sound, so it may have some mismatches, spelling issues, and pronunciation issues.

    YOUR TASKS are: 
    Correct the answer by REPLACE OR REMOVE the wrong words with the CLOSEST alphabet, phonetic, pronunciation, intonation, and stress words but MORE SUITABLE. DO NOT CHECK OR CHANGE GRAMMAR.
    - Suggest an answer to the original question. The suggested answer must be longer, more complete, and better than the corrected answer but retain the same meaning as the corrected answer.
    - ONLY USE [{level}] vocabulary.
    - YOU MUST FOLLOW THE OUTPUT FORMAT.
    
    // OUTPUT FORMAT
    {{"corrected_answer": "<.correct input answer>", "suggested_answer": "<.suggest new answer>", "suggested_answer_description": "<.descript suggested answer>"}}
    
    // INPUT FORMAT
    {{"original_question": "<input question>", "original_answer": "<input answer>"}}"""
    
def create_prompt(question, answer):
    return f"""{{"original_question": "{question}", "original_answer": "{answer}"}}"""
    
def create_chat_prompt(topic, level):
    if topic == "" or topic is None:
        topic = "software engineer working environment"
    if level == "" or level is None:
        level = "A0 to B2"
        
    return f"""I want you to act as a CHAT PERSON. We are talking about [{topic}]. ONLY USE [{level}] vocabulary. MAKE SURE ASK A QUESTION AT LAST. MUST reply to me NATURALLY in UNDER 100 words."""

# def create_base_prompt(topic, level):
#     if topic == "" or topic is None:
#         topic = "software engineer working environment"
#     if level == "" or level is None:
#         level = "A0 to B2"
#         
#     return f"""I want you to act as a grammar teacher and spelling expert. We are talking about [{topic}] and I will provide a question and its answer.
# 
#     YOUR TASK is to reply in THREE PARAGRAPHS with the requirements below. YOU MUST FOLLOW THE FORMAT, AND STOP GENERATING ADDITIONAL INFO.
#     THE FIRST paragraph format: 
#     + ONLY the corrected version of this answer IN BRACES (based on the question and answer, correct the spelling and grammar of the answer based on the question). If my answer is already correct and suitable to my question, return "none".
#     THE SECOND paragraph:
#     + First sentence format: ONLY suggested answer in braces (suggest an answer by using [{level}] vocabulary. The suggested answer must be longer, more complete, and better than the corrected answer but retain the same meaning as the corrected answer).
#     + Last sentence format: ONLY explain what was improved in the suggested answer.
#     THE THIRD paragraph:
#     + Reply to me by using [{level}] vocabulary, NOT LIMIT the number of not-question sentences. The last sentence MUST BE ONLY ONE random question IN BRACES (MUST BE a question about [{topic}]) to continue our conversation."""
    
# def create_prompt(question, answer):
#     return f"""My question and answer about are:
#     - Question: {question}?
#     - Answer: {answer}."""
    
# def create_base_prompt(topic, level):
#     return f"""I want you to act as a grammar teacher and spelling expert. We are talking about [{topic}] and I will provide a question and its answer.
# 
#     Your task is to reply to me in three paragraphs with the below requirements and put each paragraph in square brackets.
#     THE FIRST paragraph: Based on the question and answer, correct the spelling and grammar of the answer based on the question. Return the corrected version of this answer in braces to make it easier to read; put its pronunciation in parentheses after that; lastly include explanations of what was incorrect.
#     THE SECOND paragraph: Suggest an answer to me by using [{level}] vocabulary. The suggested answer must be longer, more complete, and better than the corrected answer but retain the same meaning as the corrected answer. Return the suggested answer in braces to make it easier to read.
#     THE THIRD paragraph: Reply to me by using [{level}] vocabulary. Put your last sentence in braces, this sentence MUST BE a random question about [{topic}] to continue our conversation.
#     ."""


# + Last sentence format: ONLY explanations of what was incorrect.

### RESPONSE FORMAT
# {I am fine. And you?}
# 
# {I am doing well today, thank you for asking. How about you?} This suggested answer is improved because it provides a more complete response and uses a more polite and engaging tone.
# 
# It's great to hear that you are fine! In an IT working environment, communication is very important. Clear and friendly exchanges can help build good relationships among team members. (What tools do you use for communication in your workplace?)


### OLD
# def init_response(self):
#     if self.model is None :
#         return ""
# 
#     generated_response = self.model.generate_response(
#         question=INIT_QUESTION,
#         answer=INIT_ANSWER,
#     )
#     self.process_response(
#         response=generated_response,
#         is_init=True,
#     )
#     # return generated_response
# def process_response(self, response, is_init = False):
#     # split each paragraph
#     paragraphs = list(filter(None, response.split('\n')))
#     print(f"paragraphs: {paragraphs}")
# 
#     # handle tutor question from response
#     tutor_response = paragraphs[2].replace("(", "").replace(")", "")
#     tutor_response_ipa = ipa.convert(tutor_response)
#     tutor_question = re.findall(r'\{(.*?)\}', paragraphs[2])[0]
#     self.current_question = tutor_question
#     self.update_response(
#         response_text=tutor_response,
#         response_ipa="",
#     )
# 
#     if is_init:
#         return
# 
#     # handle correct answer from response
#     correct_answer = re.findall(r'\{(.*?)\}', paragraphs[0])[0]
#     correct_answer_ipa = ipa.convert(correct_answer)
#     self.update_transcript(
#         transcript_text=correct_answer,
#         transcript_ipa=correct_answer_ipa,
#     )
# 
#     # handle suggested answer from response
#     suggested_response = paragraphs[1]
#     suggested_answer = re.findall(r'\{(.*?)\}', suggested_response)[0]
#     suggested_answer_ipa = ipa.convert(suggested_answer)
#     suggested_answer_explain = re.split(r'\{.*?\}', suggested_response)[1]
#     transcribe_answer = self.current_answer
#     transcribe_answer_ipa = ipa.convert(transcribe_answer)
#     matching_percent = calc_match_percent(correct_answer_ipa, transcribe_answer_ipa) * 100
#     self.update_suggest(
#         suggest_text=suggested_answer,
#         suggest_ipa=suggested_answer_ipa,
#         suggest_explain=suggested_answer_explain,
#         transcript_text=transcribe_answer,
#         transcript_ipa=transcribe_answer_ipa,
#         point=matching_percent,
#     )