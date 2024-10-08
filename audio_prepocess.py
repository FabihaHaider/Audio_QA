import streamlit as st
import os
import re
import sys
from lingua import LanguageDetectorBuilder
import logging
from openai import OpenAI
import json
from prompts import system_prompt2, system_prompt3
from dotenv import load_dotenv

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

lang_pattern = re.compile(r'^Detected language: (?P<lang>.+)$', flags=re.MULTILINE)
timestamp_pattern = re.compile(r'^\[\d+:\d+.\d+\s*-->\s*\d+:\d+.\d+\]\s*', flags=re.MULTILINE)
detector = LanguageDetectorBuilder.from_all_spoken_languages().build()

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
st.header("Call Center")
client = OpenAI(api_key=API_KEY)



def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as fp:
        content = fp.read()

    return content


def read_bytes(raw: bytes):
    return raw.decode(encoding='utf-8', errors='ignore')


def detect_language(text):
    match = lang_pattern.search(text)
    if match:
        lang = match.group('lang')
    else:
        logging.info(f'Whisper language data not found in the text, using lingua as fallback.')
        lang = detector.detect_language_of(text).name

    lang = lang.lower()
    logging.info(f'Detected language: {lang}')

    return lang


def trim_extras(text):
    match = timestamp_pattern.search(text)
    header_offset = match.start() if match else 0
    trimmed = timestamp_pattern.sub('', text[header_offset:])

    return trimmed

def escape_markdown(text):
    MD_SPECIAL_CHARS = "$\`*_{}[]()#+-.!"
    for char in MD_SPECIAL_CHARS:
        text = text.replace(char, "\\"+char)
    return text

def save_docs(doc, local_dir):
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    
    else:
        for filename in os.listdir(local_dir):
          # Avoid deleting the newly written file
            os.remove(os.path.join(local_dir, filename))

    file_path = os.path.join(local_dir, doc.name)
    with open(file_path, "wb") as f:
        f.write(doc.getbuffer())
        return True 
    
    return False

preset_qs = ""

def check_preset():
    if preset_qs == "":
        return False
    else:
        return True


def read_preset_questions(folder_path):
    try:
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        
        if len(files) == 1:
            # Only one file found
            file_name = files[0]
            file_path = os.path.join(folder_path, file_name)
            
            # Read and display the file
            with open(file_path, 'r') as file:
                content = file.read()
                # st.text(content)  # Display the file content
                return content
        elif len(files) == 0:
            st.info("No files found in the directory.")
        else:
            st.warning("Multiple files found. Please ensure there is only one file in the directory.")
            
    except FileNotFoundError:
        st.error(f"Folder not found: {folder_path}")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

def main():
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    
    with st.sidebar:
        st.title("Menu:")
        
        # pdf_docs = st.file_uploader("Upload your PDF Files and Click on the Submit & Process Button", accept_multiple_files=True, key="pdf_uploader")
        preset_questions = st.file_uploader("Upload your files containing Preset Questions", accept_multiple_files=False, key="preset_questions_file_uploader", type=".txt")
        submit_preset_btn =  st.button("Submit & Process")
        
        if(submit_preset_btn and preset_questions is not None):
            #save the file in a folder
            folder = "docs/preset_questions"
            if save_docs(preset_questions, folder):
                 st.success("Files saved successfully.")
            
            
            with open(f'{folder}/{preset_questions.name}', 'r') as file:
                preset_qs = file.read()
            
            # print(preset_qs)
            st.write(preset_qs)
            
            
                 
        else:
            st.write("Upload preset questions")

    # system prompt set
    
    
    conv = st.file_uploader("Upload your Transcribed Files", accept_multiple_files=False, key="conv_file_uploader", type=".txt")
    if (conv is not None):
        folder = "docs/conv"
        if save_docs(conv, folder):
            st.success("Files saved successfully.")

        with(st.spinner("Preprocessing...")):
            file_path = os.path.join(folder, conv.name)
            text = read_file(file_path)
            lang = detect_language(text)
            st.write("language detected: ", lang)
            trimmed = trim_extras(text)
            # modified_text = escape_markdown(trimmed)
            trimmed = trimmed.replace("$", "\$")
            # st.write(trimmed)
            
            
            if lang == "swedish":   
                folder_path = "docs/preset_questions" 
                preset_qs = read_preset_questions(folder_path)
                sys_prompt = system_prompt3(preset_qs)
                
            
            elif lang == "english":
                sys_prompt = system_prompt2()
            
            st.write(sys_prompt)
            
            if not any(m['role'] == 'system' for m in st.session_state.messages):
                st.session_state.messages.insert(0, {"role": "system", "content": sys_prompt})


            st.session_state.messages.append({"role": "user", "content": trimmed})
            

            # st.write([{"role": m["role"], "content": m["content"]} for m in st.session_state.messages])
            
            with st.chat_message("assistant"):
                
                stream = client.chat.completions.create(
                    model='gpt-4-turbo',
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    # stream=True,
                    response_format={'type': 'json_object'},
                    temperature=0
                )
                
                message = json.loads(stream.choices[0].message.content)
                
                # print((message))
                st.json(message)            

            # st.write("json files")

    
    
    

                


if __name__ == "__main__":
    main()