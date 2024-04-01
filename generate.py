from PIL import Image, ImageDraw, ImageFont, ImageOps
from moviepy.editor import AudioFileClip, concatenate_audioclips
import os
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
from moviepy.video.fx.all import crop
from reddit import scrape_questions_and_answers, get_unprocessed_post
from bubbles import create_text_bubble
from youtube_dl import download_clip
from tts import speak, speak11
from subtitles import add_subs
from upload_video import upload_video
import helper

input_video_path = "output\\input_video.mp4"
output_video_path = "output\\video_raw.mp4"

def make_vid(post):
    # Video processing
    clip = VideoFileClip(input_video_path)
    # REMOVE: ALL DONE IN FFMPEG COMMAND:


    # clip_resized = clip.resize(height=1280)  # Resize to the desired height

    # # Crop to maintain aspect ratio and focus
    # x_center = clip_resized.w / 2
    # y_center = clip_resized.h / 2
    # clip_cropped = crop(clip_resized, width=720, height=1280, x_center=x_center, y_center=y_center)
    yPos=0.2

    annotations = []
    start_time = 0
    audio_clips = []

    transcript = ""
    # Create a bubble for the main post
    main_post_img_path = create_text_bubble(post['post'], post['user'], "AskReddit")
    duration = speak("post", post['post'])
    transcript += post['post']

    main_post_audio_path = f"output\\audiofiles\\post.mp3"  # Assuming 'id' is available in 'post'

    main_post_clip = ImageClip(main_post_img_path).set_duration(duration).set_start(start_time).set_position(("center", yPos), relative=True)
    annotations.append(main_post_clip)

    if os.path.exists(main_post_audio_path):
        main_post_audio = AudioFileClip(main_post_audio_path).set_duration(duration).set_start(start_time)
        audio_clips.append(main_post_audio)

    start_time += (duration)
    
    user_times = []
    # Loop over comments to create bubbles and audio clips
    clip_len = helper.get_media_duration("output\\input_video.mp4")
    for idx, comment in enumerate(post['comments']):
        # Ignore the rest if the vid is already at least 45 secs long
        if (start_time >= 45):
            break

        duration = speak(f"comment_{idx}", comment['text'])
        comment_audio_path = f"output\\audiofiles\\comment_{idx}.mp3"  # Unique path for each comment
        if (((start_time + duration) >= clip_len) | ((comment['text'] == "[removed]"))):
            continue
        print(comment["text"])
        comment["text"] = comment['text'].replace("/", " or ")


        # img_path = create_text_bubble(comment['text'], comment['user'], "AskReddit")
        # img_clip = ImageClip(img_path).set_duration(duration).set_start(start_time).set_position(("center", yPos), relative=True)
        # annotations.append(img_clip)
        start_time = start_time  # Assuming `start_time` is in seconds
        user = comment['user']
        user_times.append((start_time, start_time+duration, user))


        if os.path.exists(comment_audio_path):
            comment_audio = AudioFileClip(comment_audio_path).set_duration(duration).set_start(start_time).set_end(start_time+duration-0.05)
            audio_clips.append(comment_audio)

        start_time += (duration)
        transcript += ("\n\n"+"*"+comment['text'])

    print("USER TIMES:")
    print(user_times)
    helper.save_as_srt(user_times)
    # Concatenate all audio clips together
    if audio_clips:
        combined_audio = concatenate_audioclips(audio_clips)
    with open("output\\audiofiles\\transcript.txt", "w") as file:
        file.write(transcript)

    # Final composition and video generation
    final_clips = [clip] + annotations
    final_video = CompositeVideoClip(final_clips)


    if audio_clips:
        final_video = final_video.set_audio(combined_audio)
        audio_duration = combined_audio.duration
        video_duration = audio_duration # + 0.5  # 0.5 seconds longer than audio
        final_video = final_video.set_duration(video_duration)

    final_video.write_videofile(output_video_path, fps=59, codec="libx264", preset="medium")
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
# upload_video("output\\video_subbed.mp4")
