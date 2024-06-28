import langchain
from deep_translator import GoogleTranslator
import deepl
import datetime
import os
from module.voicevox import Voicevox
import pathlib
import textwrap
from IPython.display import display
from IPython.display import Markdown
import threading
import concurrent.futures
from langchain import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)
from langchain.chat_models import ChatOpenAI

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

def speak_voicevox(text):
    voicevox = Voicevox()
    voicevox.speak(text=text)

def translate_to_japanese(text):
    translator = GoogleTranslator(source="auto", target="ja")
    result = translator.translate_text(text, target_lang="ja")
    return result.text

def process_voice(translated_text):
    speak_voicevox(translated_text)

def main(input_prompt):
    input = input_prompt
    model= ChatOpenAI(model_name="gpt-3.5-turbo",temperature=0.3)

    messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": input},
        ]

    response = model.generate_content(input, stream=True,
                                          safety_settings={
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
                    future = executor.submit(translate_to_japanese, full_response)
                
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

