import subprocess
import os
from mutagen.mp3 import MP3

def run(command):
    # Attempted fix for multiple conda locs:
    output = subprocess.run("where conda", text=True, capture_output=True).stdout
    conda_path = output.strip().split('\n')[0]
    env_name = os.environ["CONDA_PREFIX"].split(os.path.sep)[-1]


    try:
        # RESULT = subprocess.run(f'{conda_path} run -v -n -cwd{env_name} {command}', check=True, capture_output=True, text=True, shell=True)

        # I THINK THIS WORKS!!! HOLY SHIT!
        subprocess.run(['powershell', '-Command', command], check=True, capture_output=True, text=True, shell=False, encoding='utf-8')
    except subprocess.CalledProcessError as e:
        print("Command failed with return code", e.returncode)
        print("Output:", e.output)
        print("Error:", e.stderr)


def save_as_srt(entries, output_file='output\\bubbles\\usernames.srt'):
    with open(output_file, 'w', encoding='utf-8') as f:
        for index, (start, end, user) in enumerate(entries, 1):
            start_srt = format_srt_time(start)
            end_srt = format_srt_time(end)
            f.write(f"{index}\n{start_srt} --> {end_srt}\n{user}\n\n")

def format_srt_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    # SRT format requires milliseconds, so we multiply the fractional part by 1000
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{milliseconds:03}"


from mutagen.mp3 import MP3
from moviepy.editor import VideoFileClip


def get_media_duration(file_path):
    """Returns the duration of an MP3 or MP4 file in seconds."""
    if file_path.lower().endswith('.mp3'):
        media = MP3(file_path)
        duration = media.info.length
    elif file_path.lower().endswith('.mp4'):
        with VideoFileClip(file_path) as video:
            duration = video.duration
    else:
        raise ValueError("Unsupported file format")

    return duration


from moviepy.audio.AudioClip import AudioArrayClip
import numpy as np
def make_silent_audio(duration, sample_rate=44100):
    # Create a silent audio segment of the specified duration
    silent_segment = np.zeros((int(duration * sample_rate), 2))  # 2 channels for stereo
    silent_audio = AudioArrayClip(silent_segment, fps=sample_rate)
    return silent_audio

def clean(text):
    text = text.replace("*", "")
    text = text.replace("/", " or ")
    text = text.replace("…", "...")
    text = text.replace("’", "'")
    text = text.replace(" i ", " I ")    
    text = text.replace("i'", "I'")
    return text

import re
def contains_link(text):
    # Regular expression pattern to find URLs
    pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
    # Search for the pattern in the text
    match = re.search(pattern, text)
    # Return True if a match is found, False otherwise
    return match is not None


import random

def generate_title():
    words = ['CRAZY', 'UNBELIEVABLE', 'SHOCKING', 'HILARIOUS', 'EPIC', 'SAD', 'AMAZING', 'WOW', 'WHAT?!', 'HOW?!', 'NO WAY!', 'INSANE', 'MIND-BLOWING']
    emojis = ['💀', '🤣', '😱', '👍', '😂', '😭', '🔥', '💯', '🌟', '👀', '🙌', '💥', '😜', '🎉', '🤔', '🧐', '🤯', '😕', '🙄', '🤓']

    # Randomly pick 1 or 2 words and 1 to 3 emojis
    chosen_words = ' '.join(random.sample(words, k=1))
    chosen_emojis = ''.join(random.sample(emojis, k=random.randint(1, 3)))

    return f"{chosen_words} {chosen_emojis}"

