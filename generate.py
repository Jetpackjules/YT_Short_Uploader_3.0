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
from youtube_dl import download_clip, download_random_clip
import tts
from subtitles import add_subs
from upload_video import upload_video
import helper
import random
from ai import gen_description, gen_tags

# The function to use for TTS, changes often:
# OPTIONS: googleTTS | freeSpeak | openAItts
tts_function = tts.openAItts


input_video_path = "output\\input_video.mp4"
output_video_path = "output\\video_raw.mp4"

music_volume = 0
transcript = ""
def make_vid(post):
    global music_volume
    global transcript
    comment_pause = 0.35

    clip = VideoFileClip(input_video_path)
    yPos=0.2
    annotations = []
    start_time = 0
    audio_clips = []


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
        if ((start_time >= min_len)):
            break
        if ((comment['text'] == "[removed]") | (helper.contains_link(comment['text']))):
            continue
        
        duration = tts_function(f"comment_{idx}", comment['text'])
        comment_audio_path = f"output\\audiofiles\\comment_{idx}.mp3"  # Unique path for each comment
        if (((start_time + duration) >= 55) | ((start_time + duration) >= clip_len)):
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
    with open("output\\audiofiles\\transcript.txt", "w", encoding="utf-8") as file:
        file.write(transcript)

    # Concatenate all audio clips together
    combined_audio = concatenate_audioclips(audio_clips)
    combined_audio.write_audiofile("output\\audiofiles\\combined_audio_no_music.mp3")


    # 66% chance of adding background music
    if random.random() < 0.66:
        # Select a random background music file from the folder:
        background_music_folder = "assets\\background_music"
        background_music_files = [f for f in os.listdir(background_music_folder) if f.endswith('.mp3')]
        random_music_file = random.choice(background_music_files)
        background_music_path = os.path.join(background_music_folder, random_music_file)
        background_music = AudioFileClip(background_music_path).set_duration(combined_audio.duration)

        
        music_volume = random.uniform(0.01, 0.17)  # Change this value to adjust the volume of the music
        music_volume = round(music_volume, 3)
        
        background_music = AudioFileClip(background_music_path).set_duration(combined_audio.duration).volumex(music_volume)

        finalAudio = CompositeAudioClip([background_music, combined_audio])

        combined_audio = finalAudio



    # Final composition and video generation
    final_clips = [clip] + annotations
    final_video = CompositeVideoClip(final_clips)


    if audio_clips:
        final_video = final_video.set_audio(combined_audio)
        audio_duration = combined_audio.duration
        video_duration = audio_duration -0.17 #(- 0.23) <- THIS WAS MAIN # + 0.5  # 0.5 seconds longer than audio (COMMENTING THIS DOES NOT IMPROVE THE TIME ERRORS ON RENDER!!!)
        final_video = final_video.set_duration(video_duration)

    
    final_video.write_videofile(output_video_path, fps=60, codec="libx264", preset="slow")
    add_subs()

clip_name = ""
def generate(vidName = "", pubTime="default", upload=True):
    global clip_name
    global music_volume
    global transcript
    # Scrape reddit
    redditPull = get_unprocessed_post("AskReddit")  # Get an unprocessed post
    print("REDDIT SCRAPED! Generating video...")
    # Grab yt minecraft gameplay:
    if (vidName != ""):
        download_clip(vidName)
    else:
        clip_name = download_random_clip()

    # Add bubbles and compile:
    make_vid(redditPull)

    #Make thumbnail:
    helper.save_first_frame_as_png()

    # Send clip to YT:
    if upload==True:
        try:
            upload_video("output\\video_subbed.mp4", description=gen_description(transcript) + "\n\n Vol: " + str(round(music_volume, 3)), keywords=gen_tags(transcript), title=helper.generate_title(), publishTime=pubTime) #for tts typem add to desc: \n\nUsed: " + tts_function.__name__
        except:
            input("QUOTA REACHED CANCEL PROGRAM! __ ")


#How long min video length should be (wont go far over this!)
#DEFAULT: 45
#Until 6/25: 28
min_len = 34

# RUNS WHEN NOT AN IMPORT:
if __name__ == "__main__":
    generate(upload=False)