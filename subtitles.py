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
    
    with open('output\\audiofiles\\subs.srt', 'w') as srt_file:
        srt_file.write(srt_content)
    print("SRT Generated!")

import random
def unique_color_picker():
    subtitle_colors = [
        # '#FFFFFF',  # White
        '#FFFF00',  # Yellow
        # '#ADD8E6',  # Light blue
        '#90EE90',  # Soft green
        '#FFC0CB',  # Pale pink
        # '#E6E6FA',  # Lavender
        '#F5F5DC',  # Beige
        # '#D3D3D3',  # Light gray
        '#F5FFFA',  # Mint cream
        '#87CEEB'   # Sky blues
    ]
    used_colors = set()

    def get_color():
        nonlocal used_colors
        if len(used_colors) == len(subtitle_colors):
            used_colors.clear()  # Reset the used colors

        available_colors = list(set(subtitle_colors) - used_colors)
        color = random.choice(available_colors)
        used_colors.add(color)
        return color

    return get_color




def add_subs(video_file_path="output\\video_raw.mp4", output_file_path="output\\video_subbed.mp4", 
             font='Impact', 
             fontsize=60, stroke_width=25):
            # OG: fontsize=34, stroke_width=5
    
    generate_srt("output\\video_raw.mp4")
    subtitle_file_path="output\\audiofiles\\subs.srt"
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
            # txt = "BLANK"
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

    subtitles_text = SubtitlesClip(subtitle_file_path, text_generator).set_position(('center', yPos))
    subtitles_stroke = SubtitlesClip(subtitle_file_path, stroke_generator).set_position(('center', yPos))

    final = CompositeVideoClip([video, subtitles_stroke, subtitles_text], size=video.size)
    final.write_videofile(output_file_path, codec="libx264", fps=video.fps)

    # MIGHT NEED TO RE-INSTALL IMAGE MAGICK WITH ALL BOXES CHECKED (except last 2, but LEGACY FEATURES needs ot be installed)
    # Useful info: https://moviepy-tburrows13.readthedocs.io/en/improve-docs/ref/VideoClip/TextClip.html
    # Download: https://imagemagick.org/script/download.php#windows


    # subtitles_text = SubtitlesClip(subtitle_file_path, text_generator).set_position(('center', yPos))
    # subtitles_stroke = SubtitlesClip(subtitle_file_path, stroke_generator).set_position(('center', yPos))

    # # Layer the stroke subtitles behind the actual subtitles
    # final = CompositeVideoClip([video, subtitles_stroke, subtitles_text], size=video.size)

    # # Write the result to file
    # final.write_videofile(output_file_path, codec="libx264", fps=video.fps)


# RUNS WHEN NOT AN IMPORT:
if __name__ == "__main__":
    add_subs()