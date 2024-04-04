from PIL import Image, ImageDraw, ImageFont, ImageOps
from moviepy.editor import AudioFileClip, concatenate_audioclips
import os
import moviepy as mp
from moviepy.audio.AudioClip import AudioClip
from moviepy.editor import CompositeAudioClip
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
from moviepy.video.fx.all import crop
from reddit import scrape_questions_and_answers, get_unprocessed_post
from bubbles import create_text_bubble
from youtube_dl import download_clip
import tts
from subtitles import add_subs
from upload_video import upload_video
import helper

# The function to use for TTS, changes often:
# OPTIONS: googleTTS | freeSpeak | 
tts_function = tts.freeSpeak


input_video_path = "output\\input_video.mp4"
output_video_path = "output\\video_raw.mp4"

def make_vid(post):
    comment_pause = 0.35

    clip = VideoFileClip(input_video_path)
    yPos=0.2
    annotations = []
    start_time = 0
    audio_clips = []
    transcript = ""


    # Create a bubble for the main post
    main_post_img_path = create_text_bubble(post['post'], post['user'], "AskReddit")
    post['post'] = helper.clean(post['post'])
    duration = tts_function("post", post['post'])
    transcript += post['post']

    main_post_audio_path = f"output\\audiofiles\\post.mp3"  # Assuming 'id' is available in 'post'

    main_post_clip = ImageClip(main_post_img_path).set_duration(duration).set_start(start_time).set_position(("center", yPos), relative=True)
    annotations.append(main_post_clip)

    if os.path.exists(main_post_audio_path):
        main_post_audio = AudioFileClip(main_post_audio_path).set_duration(duration).set_start(start_time)
        audio_clips.append(main_post_audio)

    start_time += (duration + comment_pause)
    
    user_times = []
    # Loop over comments to create bubbles and audio clips
    clip_len = helper.get_media_duration(input_video_path)
    for idx, comment in enumerate(post['comments']):
        # Clean up comment:
        print(comment["text"])
        comment["text"] = helper.clean(comment['text'])

        # Ignore the rest if the vid is already at least 45 secs long
        if (start_time >= 45):
            break
        duration = tts_function(f"comment_{idx}", comment['text'])
        comment_audio_path = f"output\\audiofiles\\comment_{idx}.mp3"  # Unique path for each comment
        if (((start_time + duration) >= 55) | ((start_time + duration) >= clip_len) | ((comment['text'] == "[removed]") | (helper.contains_link(comment['text'])))):
            continue


        user = comment['user']
        user_times.append((start_time, start_time+duration+comment_pause, user))


        if os.path.exists(comment_audio_path):
            comment_audio = AudioFileClip(comment_audio_path).set_duration(duration).set_start(start_time).set_end(start_time+duration -0.15)
            audio_clips.append(comment_audio)
            # Insert a silent audio clip between the comments
            if idx < len(post['comments']) - 1:  # Check if it's not the last comment
                silent_audio = helper.make_silent_audio(comment_pause)
                audio_clips.append(silent_audio)

        start_time += (duration+comment_pause)
        transcript += ("\n\n"+"*"+comment['text'])

    # print("USER TIMES:")
    helper.save_as_srt(user_times)

    # Concatenate all audio clips together
    combined_audio = concatenate_audioclips(audio_clips)


    with open("output\\audiofiles\\transcript.txt", "w", encoding="utf-8") as file:
        file.write(transcript)

    # Final composition and video generation
    final_clips = [clip] + annotations
    final_video = CompositeVideoClip(final_clips)


    if audio_clips:
        final_video = final_video.set_audio(combined_audio)
        audio_duration = combined_audio.duration
        video_duration = audio_duration # + 0.5  # 0.5 seconds longer than audio
        final_video = final_video.set_duration(video_duration)

    final_video.write_videofile(output_video_path, fps=60, codec="libx264", preset="slow")
    add_subs()


# Scrape reddit
# redditPull = scrape_questions_and_answers()
redditPull = get_unprocessed_post()  # Get an unprocessed post
print("REDDIT SCRAPED! Generating video...")
# Grab yt minecraft gameplay:
download_clip()
# Add bubbles and compile:
make_vid(redditPull)
# Send clip to YT:
# upload_video("output\\video_subbed.mp4", description=redditPull['post'] + "\n\nPlease like and subscribe for more reddit stories!!", title=helper.generate_title())