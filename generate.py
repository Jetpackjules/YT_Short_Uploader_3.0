# from PIL import Image, ImageDraw, ImageFont, ImageOps
from moviepy.editor import AudioFileClip, concatenate_audioclips
import os
# import moviepy as mp
# from moviepy.audio.AudioClip import AudioClip
from moviepy.editor import CompositeAudioClip
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
from moviepy.video.fx.all import crop
from reddit import get_unprocessed_post
from bubbles import create_text_bubble
from youtube_dl import download_clip, download_random_clip
import tts
from subtitles import add_subs
from upload_video import upload_video
from helper import clean, contains_link, save_as_srt, make_silent_audio, generate_title, get_media_duration
import random
from ai import gen_description, gen_tags

# The function to use for TTS, changes often:
# OPTIONS: googleTTS | freeSpeak | openAItts
tts_function = tts.openAItts


input_video_path = "output/input_video.mp4"
output_video_path = "output/video_raw.mp4"



def make_vid(post, read_post=False):
    music_volume = 0.00
    transcript = "" 
    comment_pause = 0.35

    clip = VideoFileClip(input_video_path)
    yPos=0.2
    annotations = []
    start_time = 0
    audio_clips = []


    # Create a bubble for the main post
    main_post_img_path = create_text_bubble(post['post'], post['user'], "AskReddit", video_height=clip.h)
    post['post'] = clean(post['post'])
    duration = tts_function("post", post['post'])
    transcript += post['post']

    main_post_audio_path = f"output/audiofiles/post.mp3"  # Assuming 'id' is available in 'post'

    main_post_clip = ImageClip(main_post_img_path).set_duration(duration).set_start(start_time).set_position(("center", yPos), relative=True)
    annotations.append(main_post_clip)

    if os.path.exists(main_post_audio_path):
        main_post_audio = AudioFileClip(main_post_audio_path)
        actual_duration = main_post_audio.duration
        if abs(actual_duration - duration) > 0.1:  # Allow for a small difference
            print(f"Warning: Expected duration {duration} doesn't match actual duration {actual_duration} for main post")
            duration = actual_duration  # Use the actual duration instead
        main_post_audio = main_post_audio.set_duration(duration).set_start(start_time)
        audio_clips.append(main_post_audio)

    start_time += (duration + comment_pause)
    
    user_times = []
    
    if not read_post:
        # Loop over comments to create bubbles and audio clips
        clip_len = get_media_duration(input_video_path)
        for idx, comment in enumerate(post['comments']):
            # Clean up comment:
            # print(comment["text"])
            comment["text"] = clean(comment['text'])

            # Ignore the rest if the vid is already at least 45 secs long
            if ((start_time >= min_len)):
                break
            if ((comment['text'] == "[removed]") | (contains_link(comment['text']))):
                continue
            
            duration = tts_function(f"comment_{idx}", comment['text'])
            comment_audio_path = f"output/audiofiles/comment_{idx}.mp3"  # Unique path for each comment
            if (((start_time + duration) >= 55) | ((start_time + duration) >= clip_len)):
                continue

            user = comment['user']
            user_times.append((start_time, start_time+duration+comment_pause, user))

            if os.path.exists(comment_audio_path):
                comment_audio = AudioFileClip(comment_audio_path)
                actual_duration = comment_audio.duration
                if abs(actual_duration - duration) > 0.1:  # Allow for a small difference
                    print(f"Warning: Expected duration {duration} doesn't match actual duration {actual_duration} for comment {idx}")
                    duration = actual_duration  # Use the actual duration instead

                comment_audio = comment_audio.set_duration(duration).set_start(start_time).set_end(start_time+duration -0.15)
                audio_clips.append(comment_audio)
                # Insert a silent audio clip between the comments
                if idx < len(post['comments']) - 1:  # Check if it's not the last comment
                    silent_audio = make_silent_audio(comment_pause)
                    audio_clips.append(silent_audio)

            start_time += (duration+comment_pause)
            transcript += ("\n\n"+"*"+comment['text'])
    else:
        # For "read post" videos, add the post description
        
        post_desc = post["body"]
        if post_desc:
            post_desc = clean(post_desc)
            duration = tts_function("post_desc", post_desc)
            post_desc_audio_path = f"output/audiofiles/post_desc.mp3"
            
            if os.path.exists(post_desc_audio_path):
                post_desc_audio = AudioFileClip(post_desc_audio_path)
                actual_duration = post_desc_audio.duration
                if abs(actual_duration - duration) > 0.1:
                    print(f"Warning: Expected duration {duration} doesn't match actual duration {actual_duration} for post description")
                    duration = actual_duration
                
                post_desc_audio = post_desc_audio.set_duration(duration).set_start(start_time)
                audio_clips.append(post_desc_audio)
            
            transcript += ("\n\n" + "*" + post_desc)
            start_time += duration

    # print("USER TIMES:")
    save_as_srt(user_times)
    with open("output/audiofiles/transcript.txt", "w", encoding="utf-8") as file:
        file.write(transcript)

    # Concatenate all audio clips together
    combined_audio = concatenate_audioclips(audio_clips)
    combined_audio.write_audiofile("output/audiofiles/combined_audio_no_music.mp3")


    # 66% chance of adding background music
    randomNum = random.random()
    print("RANDOM NUM: " + str(randomNum))
    if randomNum < 0.66:
        # Select a random background music file from the folder:
        background_music_folder = "assets/background_music"
        background_music_files = [f for f in os.listdir(background_music_folder) if f.endswith('.mp3')]
        random_music_file = random.choice(background_music_files)
        background_music_path = os.path.join(background_music_folder, random_music_file)
        background_music = AudioFileClip(background_music_path).set_duration(combined_audio.duration)

        
        music_volume = random.uniform(0.01, 0.14)  # Change this value to adjust the volume of the music
        music_volume = round(music_volume, 3)
        
        background_music = AudioFileClip(background_music_path).set_duration(combined_audio.duration).volumex(music_volume)

        finalAudio = CompositeAudioClip([background_music, combined_audio])

        combined_audio = finalAudio
        print("ADDED MUSIC")
    else:
        print("NO MUSIC ADDED")



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

    return transcript, music_volume


def generate(vidName="", pubTime="default", subreddit="AskReddit", upload=True, download=True, process=True, read_post=False):
    # Scrape reddit
    
    redditPull = get_unprocessed_post(subreddit, process=process)  # Get an unprocessed post #dont process if not uploading
    print("REDDIT SCRAPED! Generating video...")
    # Grab yt minecraft gameplay:
    if download:
        if (vidName != ""):
            download_clip(vidName)
        else:
            clip_name = download_random_clip()

    # Add bubbles and compile:
    transcript, music_volume = make_vid(redditPull, read_post)

    #Make thumbnail:
    # save_first_frame_as_png()

    # Send clip to YT:
    if upload==True:
        try:
            upload_video("output/video_subbed.mp4", description=gen_description(transcript) + "\n\n Vol: " + str(round(music_volume, 3)), keywords=gen_tags(transcript), title=generate_title(), publishTime=pubTime) #for tts typem add to desc: \n\nUsed: " + tts_function.__name__
        except:
            input("QUOTA REACHED CANCEL PROGRAM! __ ")


#How long min video length should be (wont go far over this!)
#DEFAULT: 45
#Until 6/25: 28
min_len = 30

# RUNS WHEN NOT AN IMPORT:
if __name__ == "__main__":
    generate(upload=False, download=False, process=False, subreddit="offmychest", read_post=True)
