
import deepl
import datetime
import os
from module.voicevox import Voicevox
import pathlib
import textwrap
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from IPython.display import display
from IPython.display import Markdown
import threading
import concurrent.futures


def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

# Or use `os.getenv('GOOGLE_API_KEY')` to fetch an environment variable.
GOOGLE_API_KEY="AIzaSyCPV3eMDl_q-gFYngxy1xmJNv7tq8jStBc"
DEEPL_API_KEY="12a41666-9fe3-400f-ada1-3c1d0a32b1a7:fx"
client = genai.configure(api_key=GOOGLE_API_KEY)

def speak_voicevox(text):
    voicevox = Voicevox()
    voicevox.speak(text=text)

def translate_to_japanese(text, deepl_api_key):
    translator = deepl.Translator(deepl_api_key)
    result = translator.translate_text(text, target_lang="JA")
    return result.text

def process_voice(translated_text):
    speak_voicevox(translated_text)

def main(input_prompt):
    input_to_gemini = input_prompt
    model= genai.GenerativeModel('gemini-pro')

    messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": input_to_gemini},
        ]

    response = model.generate_content(input_to_gemini, stream=True,
                                          safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    })
    # print(input_prompt)
    full_response = ""
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = None
        for res in response:
            try:
                print(res.text, end="")
                full_response += res.text
                
                if future is None:
                    future = executor.submit(translate_to_japanese, full_response, DEEPL_API_KEY)
                
            except:
                res.prompt_feedback
                res.candidates[0].finish_reason
                res.candidates[0].safety_ratings
                print(res.text, end="")
                full_response += res.text
                to_markdown(res.text)
                
        if future:
            translated_response = future.result()
            executor.submit(process_voice, translated_response)
        
    print("\n")
    

if __name__ == "__main__":
    while True:
        user_input = input('Prompt: ')
        if user_input.lower() == 'exit':
            main(input_prompt="Goodbye")
            break
        main(input_prompt=user_input)

