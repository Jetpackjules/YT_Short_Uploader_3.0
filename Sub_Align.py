# NEED TO DOWNLOAD ESPEAK: https://espeak.sourceforge.net/download.html
# NEVERMIND!!! ABOVE IS SHIT


# NEED TO DOWNLOAD NODE JS!: https://nodejs.org/en/downloads
# For echogarden: https://github.com/echogarden-project/echogarden OR: npm install echogarden -g
# ALSO RUN THIS IN POWERSHELL AS ADMIN to fix permissions: Set-ExecutionPolicy RemoteSigned

import subprocess
import os


def prepare_transcript(original_path, modified_path):
    """
    Splits the transcript into lines with two words each.
    """
    with open(original_path, 'r') as original, open(modified_path, 'w') as modified:
        for line in original:
            words = line.split()
            for i in range(0, len(words), 2):
                if (words[i] != "&#x200B;"):
                    modified.write(' '.join(words[i:i + 2])) 


def generate_srt(audio_path):
    original_transcript_path = "output\\audiofiles\\transcript.txt"
    modified_transcript_path = "output\\audiofiles\\transcript_MOD.txt"
    output_directory = "output\\audiofiles"

    prepare_transcript(original_transcript_path, modified_transcript_path)
    # modified_transcript_path = original_transcript_path

    # path = os.getcwd()
    # print(path + "-------------------------------------------------")
    conda_path = subprocess.run("where conda", text=True, capture_output=True).stdout.strip()
    env_name = os.environ["CONDA_PREFIX"].split(os.path.sep)[-1]


    command = f"echogarden align {audio_path} {modified_transcript_path} {output_directory}\\subs.srt --overwrite"
    print("ALIGNING TRANSCRIPT TO AUDIO FOR SRT...")
    # try:
    #     print(f'{conda_path} run -n {env_name} {command}')
    # except:
    # out = subprocess.run(f'{command}', check=True, capture_output=True, text=True, shell=True)
    try:
        # Run your command and capture output and errors
        result = subprocess.run(f'{command}', check=True, capture_output=True, text=True, shell=True)
    except subprocess.CalledProcessError as e:
        print("TRYING OTHER COMMAND!")
        RESULT = subprocess.run(f'{conda_path} run -n {env_name} {command}', check=True, capture_output=True, text=True, shell=True)
    
    print("SRT files generated successfully in:", output_directory)

generate_srt("output\\video_raw.mp4")

# echogarden speak-file text.txt transcript.txt result.srt result.json
