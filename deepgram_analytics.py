# main.py (python example)

import os
from dotenv import load_dotenv
import streamlit as st

from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)

load_dotenv()
API_KEY = os.getenv("DG_API_KEY")

def read_audio_file_path(folder_path):
    try:
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        
        if len(files) == 1:
            # Only one file found
            file_name = files[0]
            file_path = os.path.join(folder_path, file_name)
            
            return file_path
        elif len(files) == 0:
            return("No audio files found in the directory.")
        else:
            return("Multiple audio files found. Please ensure there is only one audio file in the directory.")
            
    except FileNotFoundError:
        return(f"Audio folder not found: {folder_path}")
    except Exception as e:
        return(f"An error occurred: {str(e)}")



def diarize_audio_file(folder_path):
    try:
        # STEP 1 Create a Deepgram client using the API key
        deepgram = DeepgramClient(API_KEY)

        AUDIO_FILE = read_audio_file_path(folder_path)
        with open(AUDIO_FILE, "rb") as file:
            buffer_data = file.read()

        payload: FileSource = {
            "buffer": buffer_data,
        }

        #STEP 2: Configure Deepgram options for audio analysis
        options = PrerecordedOptions(
            model="whisper",
            smart_format=True,
            language="sv",
            diarize=True,
        )

        # STEP 3: Call the transcribe_file method with the text payload and options
        response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)

        # STEP 4: Print the response
        conv = ""
        data = response
        for channel in data['results']['channels']:
            for alternative in channel['alternatives']:
                print(alternative['paragraphs']['transcript'])
                conv = alternative['paragraphs']['transcript']

        with open('docs/conv/diarize.txt', 'w', encoding='utf-8') as f:
            f.write(conv)
            return True

    except Exception as e:
        st.write(f"Exception: {e}")

