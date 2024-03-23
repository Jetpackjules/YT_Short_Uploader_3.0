from deepgram import Deepgram
import io
from contextlib import redirect_stdout
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip

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



def add_subs(video_file_path="output\\video_raw.mp4", output_file_path="output\\video_subbed.mp4", 
             font='Impact', color='white', 
             fontsize=34, stroke_width=5):
    
    generate_captions(video_file_path)
    subtitle_file_path="output\\audiofiles\\subs.srt"
    # Load the video clip
    video = VideoFileClip(video_file_path)
    vidHeight = video.h
    vidWidth = video.w
    yPos = vidHeight * 4/9
    
    # Define the generator for the stroke (background text)
    stroke_generator = lambda txt: TextClip(  txt,
                                            fontsize=fontsize,
                                            font=font, 
                                            color=color,
                                            stroke_width=stroke_width,
                                            stroke_color="black",
                                            size=(vidWidth*3/4 + stroke_width, None),
                                            method="caption", 
                                            align="north")
    
    # Define the generator for the actual text
    text_generator = lambda txt: TextClip(  txt,
                                            fontsize=fontsize,
                                            font=font,
                                            color=color,
                                            size=(vidWidth*3/4, None),
                                            method="caption", 
                                            align="north")

    # Create the subtitle clips:
    # MIGHT NEED TO RE-INSTALL IMAGE MAGICK WITH ALL BOXES CHECKED (except last 2, but LEGACY FEATURES needs ot be installed)
    # Useful info: https://moviepy-tburrows13.readthedocs.io/en/improve-docs/ref/VideoClip/TextClip.html
    # Download: https://imagemagick.org/script/download.php#windows
    subtitles_text = SubtitlesClip(subtitle_file_path, text_generator).set_position(('center', yPos))
    subtitles_stroke = SubtitlesClip(subtitle_file_path, stroke_generator).set_position(('center', yPos))

    # Layer the stroke subtitles behind the actual subtitles
    final = CompositeVideoClip([video, subtitles_stroke, subtitles_text], size=video.size)

    # Write the result to file
    final.write_videofile(output_file_path, codec="libx264", fps=video.fps)



# Example usage
# generate_captions('output\\video_raw.mp4')
# add_subs()