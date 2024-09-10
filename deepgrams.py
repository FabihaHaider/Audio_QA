from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)
from dotenv import load_dotenv
import os
import json
from parser import parse_transcripts

load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
# print(DEEPGRAM_API_KEY)

def transcribe(FILE_PATH: str):
    try:
        deepgram = DeepgramClient(DEEPGRAM_API_KEY)

        with open(FILE_PATH, "rb") as file:
            buffer_data = file.read()
                
        payload: FileSource = {
            "buffer": buffer_data,
        }

        options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
            language="sv",
            utterances=True,
            punctuate=True,
            diarize=True
        )

        response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)
        # print(response.to_json(indent=4))

        with open("docs/conv/outputs.json", 'w') as json_file:
            json_file.write(response.to_json(indent=4))
            
        with open('docs/conv/outputs.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        return parse_transcripts(data)
    
    except Exception as e:
        print(f"Exception: {e}")

    
if __name__ == "__main__":
    
    filepath = "docs/conv/audio/file.mp3"
    json_text = transcribe(FILE_PATH=filepath)
    
    print(json_text)

