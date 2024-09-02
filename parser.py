import json
import sys

def parse_transcripts(json_data):
    results = json_data['results']['channels'][0]['alternatives'][0]['words']
    output_lines = []
    current_speaker = None
    current_speech = []

    for word_info in results:
        speaker = word_info['speaker']
        word = word_info['punctuated_word']
        
        if speaker != current_speaker:
            if current_speaker is not None:
                output_lines.append(f"[Speaker:{current_speaker}] {' '.join(current_speech)}")
            current_speaker = speaker
            current_speech = [word]
        else:
            current_speech.append(word)

    # Add the last speaker's speech
    if current_speaker is not None:
        output_lines.append(f"[Speaker:{current_speaker}] {' '.join(current_speech)}")
    
    return '\n'.join(output_lines)

def save_to_file(output_lines, filename="outs_parser2.txt"):
    with open(filename, "w") as file:
        file.write(output_lines)




if __name__ == '__main__':
        
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <filename.json> <outputs.txt>")
        sys.exit(1)

    with open(f'../data/{sys.argv[1]}', 'r', encoding='utf-8') as file:
        json_data = json.load(file)    
        
    output_lines = parse_transcripts(json_data)
    
    print(output_lines)
    # outs = '\n'.join(output_lines)
    # print(outs)
    # [print(lines) for lines in output_lines]
    save_to_file(output_lines)