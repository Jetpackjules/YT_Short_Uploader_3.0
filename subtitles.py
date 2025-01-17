# import io
# from contextlib import redirect_stdout
from cv2 import VIDEOWRITER_PROP_RAW_VIDEO
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from Sub_Align import generate_srt
from helper import censor

import random
def unique_color_picker(deterministic=False):
    subtitle_colors = [
        # '#FFFF00',  # Yellow
        '#FFFFFF',  # White
        '#90EE90',  # Soft green
        '#FFC0CB',  # Pale pink
        '#87CEEB',  # Sky blue

    ]
    used_colors = set()
    last_color = None
    color_counter = 0

    def get_color():
        nonlocal used_colors, last_color, color_counter
        if deterministic:
            color = subtitle_colors[color_counter % len(subtitle_colors)]
            color_counter += 1
        else:
            if len(used_colors) == len(subtitle_colors):
                used_colors.clear()  # Reset the used colors
                used_colors.add(last_color)  # Ensure last color is not picked again immediately

            available_colors = list(set(subtitle_colors) - used_colors)
            color = random.choice(available_colors)
            used_colors.add(color)
            last_color = color
        return color

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
import textwrap


def add_subs(video_file_path="output/video_raw.mp4", output_file_path="output/video_subbed.mp4", 
             font_size=65, strokewidth=20, font='Impact', subtitle_height=0.35):

    generate_srt("output/audiofiles/combined_audio_no_music.mp3")
    subtitle_file_path="output/audiofiles/subs.srt"
    trim_srt_file(subtitle_file_path)
    get_color = unique_color_picker(deterministic=False)


    # Load the video clip
    video = VideoFileClip(video_file_path)
    vidHeight = video.h
    vidWidth = video.w*1.0
    
    # Calculate fontsize and stroke_width based on video resolution
    base_height = 1280  # Base height for original values
    scale_factor = vidHeight / base_height
    # print(scale_factor)1
    # input("TEST")
    fontsize = (font_size * scale_factor)
    stroke_width = (strokewidth * scale_factor)
    
    # Ensure subtitle_height is within the valid range
    subtitle_height = max(0.0, min(1.0, subtitle_height))
    
    # Calculate yPos based on subtitle_height
    yPos = vidHeight * (1 - subtitle_height)
    
    current_color = "white"  # Initialize with default color

    def text_generator(txt):
        nonlocal current_color  # Use the nonlocal keyword to modify the outer variable

        
        if '*' in txt:
            current_color = get_color()  # Change color if '*' found
            txt = txt.replace('*', '')  # Remove the asterisk if you don't want it displayed
        
        # Skip if its just the symbol:
        if not txt.strip():
            return ColorClip(size=(1, 1), color=(0, 0, 0, 0), duration=0.1).set_position('center').set_opacity(0)

        wrapped_text = textwrap.fill(txt, width=int(50 * scale_factor))  # Adjust 'width' based on your needs and scale it

        return TextClip(wrapped_text,
                        fontsize=fontsize,
                        font=font,
                        color=current_color,
                        size=(vidWidth*3.3/4, None),
                        method="caption",
                        align="north")

    def stroke_generator(txt):
        if '*' in txt:
            txt = txt.replace('*', '')  # Remove the asterisk if you don't want it displayed

        # Skip if its just the symbol:
        if not txt.strip():
            return ColorClip(size=(1, 1), color=(0, 0, 0, 0), duration=0.1).set_position('center').set_opacity(0)
        
        # Censor subtitles (shouldnt be necessary because we r doing this at post-level)
        txt = censor(txt)

        wrapped_text = textwrap.fill(txt, width=int(50 * scale_factor))  # Adjust 'width' based on your needs and scale it

        return TextClip(wrapped_text,
                        fontsize=fontsize,
                        font=font, 
                        color='black',  # Stroke color
                        stroke_width=stroke_width,
                        stroke_color="black",
                        size=(vidWidth*3.3/4 + stroke_width-5, None),
                        method="caption", 
                        align="north")



    # Read the SRT file with utf8 encoding.

    with open(subtitle_file_path, 'r', encoding='utf-8') as f:
        subtitles = f.read()



    subtitles = parse_srt(subtitles)

    subtitles_text = SubtitlesClip(subtitles, text_generator).set_position(('center', yPos))
    subtitles_stroke = SubtitlesClip(subtitles, stroke_generator).set_position(('center', yPos))
    
    final = CompositeVideoClip([video, subtitles_stroke, subtitles_text], size=video.size)


    # ADD CAT OVERLAY:

    # Load the cat video
    cat_video = VideoFileClip('assets/sub_cat.webm')
    cat_duration = cat_video.duration

    # Remove the grey background from the cat video
    # Adjust 'thr' and 's' parameters for better masking
    cat_video_no_bg = cat_video.fx(vfx.mask_color, color=(204, 204, 204), thr=6, s=5) #usually 5!)

    # Resize the cat video to be smaller (e.g., 25% of the main video's width)
    cat_width = final.w * 1.75
    cat_video_no_bg = cat_video_no_bg.resize(width=cat_width)

    # Position the cat video at the top right corner
    cat_video_no_bg = cat_video_no_bg.set_position(('center', 'top'))

    # Set the start time for the cat video to overlay
    start_time = final.duration - cat_duration
    cat_video_no_bg = cat_video_no_bg.set_start(start_time)

    # Create the composite video
    final_video = CompositeVideoClip([final, cat_video_no_bg], size=final.size)

# # Write the output video
# final_video.write_videofile('output/final_video.mp4', codec='libx264')



    #WRITE FINAL VIDEO:
    final_video.write_videofile(output_file_path, codec="libx264", fps=video.fps, preset="slow")

    # MIGHT NEED TO RE-INSTALL IMAGE MAGICK WITH ALL BOXES CHECKED (except last 2, but LEGACY FEATURES needs ot be installed)
    # Useful info: https://moviepy-tburrows13.readthedocs.io/en/improve-docs/ref/VideoClip/TextClip.html
    # Download: https://imagemagick.org/script/download.php#windows


# RUNS WHEN NOT AN IMPORT:
if __name__ == "__main__":
    add_subs(output_file_path="output/video_moved_subs.mp4")