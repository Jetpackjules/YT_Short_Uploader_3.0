# NEED TO DOWNLOAD NODE JS!: https://nodejs.org/en/downloads
# For echogarden: https://github.com/echogarden-project/echogarden OR: npm install echogarden -g
# ALSO RUN THIS IN POWERSHELL AS ADMIN to fix permissions: Set-ExecutionPolicy RemoteSigned

import helper

def prepare_transcript(original_path, modified_path):
    with open(original_path, 'r', encoding='utf-8') as original, open(modified_path, 'w', encoding='utf-8') as modified:
        for line in original:
            words = line.split()
            for i in range(0, len(words), 3):
                if (words[i] != "&#x200B;"):
                    new_tex = ' '.join(words[i:i + 3])+" "
                    # Adding line breaks after each comment:
                    new_tex = new_tex.replace('*', "\n\n*")

                    new_tex = new_tex.replace("‘", "'").replace("’", "'")
                    new_tex = new_tex.replace("‚", ",")
                    new_tex = new_tex.replace("“", '"').replace("”", '"')

                    new_tex = new_tex.replace('",', ",\n\n")
                    new_tex = new_tex.replace('"', "\n\n")
                    # Replace curly double quotes
                    # Replace curly commas (if any exist; they are less common)
                    new_tex = new_tex.replace("ï¿½", "").replace("(", "").replace(")", "")
                    modified.write(new_tex) 

def generate_srt(audio_path):
    original_transcript_path = "output\\audiofiles\\transcript.txt"
    modified_transcript_path = "output\\audiofiles\\transcript_MOD.txt"
    output_directory = "output\\audiofiles"

    prepare_transcript(original_transcript_path, modified_transcript_path)
    # modified_transcript_path = original_transcript_path 

    print("ALIGNING TRANSCRIPT TO AUDIO FOR SRT...")
    command = f"echogarden align {audio_path} {modified_transcript_path} {output_directory}\\subs.srt --overwrite --subtitles.minWordsInLine=1 --language=en-US --subtitles.maxLineCount=1 --subtitles.maxLineWidth=20"
    helper.run(command)

    print("SRT files generated successfully in:", output_directory)



        
# RUNS WHEN NOT AN IMPORT:
if __name__ == "__main__":
    generate_srt("output\\video_raw.mp4")

