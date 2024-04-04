from deepgram import Deepgram
import io
from contextlib import redirect_stdout
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from Sub_Align import generate_srt

deepgram = Deepgram("73bfe43e53a979195482bdaf19865b539429e7e0")

def generate_captions(file_url):
    # Assuming 'file_path' is the path to your local audio file
    with open(file_url, 'rb') as audio_file:
        file_content = audio_file.read()

    source = {
            'buffer': file_content,
            'mimetype': 'audio/mp4'  # Replace with the correct MIME type for your audio file
    }

    # Request transcript with utterances for creating captions
    response = deepgram.transcription.sync_prerecorded(source, {'smart_format': True,
                                                                'punctuation': True, 
                                                                'utterances': True,
                                                                'paragraphs': True,
                                                                'numerals': True})
    
    # Capture the printed output
    f = io.StringIO()
    with redirect_stdout(f):
        deepgram.extra.to_SRT(response)
    srt_content = f.getvalue()
    
    with open('output\\audiofiles\\subs.srt', 'w', encoding='utf-8') as srt_file:
        srt_file.write(srt_content)
    print("SRT Generated!")

import random
def unique_color_picker():
    subtitle_colors = [
        '#FFFF00',  # Yellow
        '#90EE90',  # Soft green
        # '#FFC0CB',  # Pale pink
        # '#87CEEB'   # Sky blue
    ]
    used_colors = set()
    last_color = None

    def get_color():
        nonlocal used_colors, last_color
        if len(used_colors) == len(subtitle_colors):
            used_colors.clear()  # Reset the used colors
            used_colors.add(last_color)  # Ensure last color is not picked again immediately

        available_colors = list(set(subtitle_colors) - used_colors)
        color = random.choice(available_colors)
        used_colors.add(color)
        last_color = color
        return color

    return get_color
    return get_color

def trim_srt_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.readlines()

    # Find the line with the first asterisk
    asterisk_line = next((i for i, line in enumerate(content) if '*' in line), None)

    if asterisk_line is not None and asterisk_line >= 2:
        # Keep everything from two lines before the first asterisk onwards
        trimmed_content = content[asterisk_line - 2:]
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(trimmed_content)
    else:
        print("Asterisk not found or too close to the start of the file.")

import re
def srt_time_to_seconds(time_str):
    """Convert a time string from SRT to seconds."""
    hours, minutes, seconds = time_str.split(':')
    seconds, milliseconds = seconds.split(',')
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000

def parse_srt(srt_content):
    # Split content into blocks separated by blank lines
    blocks = re.split(r'\n\n+', srt_content.strip())
    
    subtitles = []
    for block in blocks:
        lines = block.split('\n')
        if len(lines) >= 3:
            # Second line contains the start and end times
            times = lines[1].split(' --> ')
            if len(times) == 2:
                start_time = srt_time_to_seconds(times[0])
                end_time = srt_time_to_seconds(times[1])
                # All remaining lines are part of the subtitle text
                text = ' '.join(lines[2:])
                subtitles.append(((start_time, end_time), text))
    
    return subtitles


def add_subs(video_file_path="output\\video_raw.mp4", output_file_path="output\\video_subbed.mp4", 
             font='Impact', 
             fontsize=60, stroke_width=25):
            # OG: fontsize=34, stroke_width=5
    
    generate_srt("output\\video_raw.mp4")
    subtitle_file_path="output\\audiofiles\\subs.srt"
    trim_srt_file(subtitle_file_path)
    get_color = unique_color_picker()


    # Load the video clip
    video = VideoFileClip(video_file_path)
    vidHeight = video.h
    vidWidth = video.w*1.0
    yPos = vidHeight * 4/9
    
    current_color = "white"  # Initialize with default color

    def text_generator(txt):
        nonlocal current_color  # Use the nonlocal keyword to modify the outer variable

        
        if '*' in txt:
            current_color = get_color()  # Change color if '*' found
            txt = txt.replace('*', '')  # Remove the asterisk if you don't want it displayed
        
        # Skip if its just the symbol:
        if not txt.strip():
            return ColorClip(size=(1, 1), color=(0, 0, 0, 0), duration=0.1).set_position('center').set_opacity(0)

        return TextClip(txt,
                        fontsize=fontsize,
                        font=font,
                        color=current_color,
                        size=(vidWidth*3/4, None),
                        method="caption",
                        align="north")

    def stroke_generator(txt):
        if '*' in txt:
            txt = txt.replace('*', '')  # Remove the asterisk if you don't want it displayed
        # Skip if its just the symbol:
        if not txt.strip():
            # txt = "BLANK"
            return ColorClip(size=(1, 1), color=(0, 0, 0, 0), duration=0.1).set_position('center').set_opacity(0)
        

        return TextClip(txt,
                        fontsize=fontsize,
                        font=font, 
                        color='black',  # Stroke color
                        stroke_width=stroke_width,
                        stroke_color="black",
                        size=(vidWidth*3/4 + stroke_width, None),
                        method="caption", 
                        align="north")



    # Read the SRT file with utf8 encoding.

    with open(subtitle_file_path, 'r', encoding='utf-8') as f:
        subtitles = f.read()



    subtitles = parse_srt(subtitles)

    subtitles_text = SubtitlesClip(subtitles, text_generator).set_position(('center', yPos))
    subtitles_stroke = SubtitlesClip(subtitles, stroke_generator).set_position(('center', yPos))
    
    final = CompositeVideoClip([video, subtitles_stroke, subtitles_text], size=video.size)
    final.write_videofile(output_file_path, codec="libx264", fps=video.fps)

    # MIGHT NEED TO RE-INSTALL IMAGE MAGICK WITH ALL BOXES CHECKED (except last 2, but LEGACY FEATURES needs ot be installed)
    # Useful info: https://moviepy-tburrows13.readthedocs.io/en/improve-docs/ref/VideoClip/TextClip.html
    # Download: https://imagemagick.org/script/download.php#windows


# RUNS WHEN NOT AN IMPORT:
if __name__ == "__main__":
    add_subs()