from PIL import Image, ImageDraw, ImageFont, ImageOps
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
from moviepy.video.fx.all import crop
from reddit import scrape_questions_and_answers
from bubbles import create_text_bubble
from youtube_dl import download_clip
# Update these paths and values to suit your setup
# input_video_path = "assets\\input_video.mp4"
# input_video_path = "random_minute.webm"
input_video_path = "output\\input_video.webm"
output_video_path = "output\\video_raw.mp4"



def make_vid(post):
    # Video processing
    clip = VideoFileClip(input_video_path)
    clip_resized = clip.resize(height=1280)  # Resize to the desired height

    # Crop to maintain aspect ratio and focus
    x_center = clip_resized.w / 2
    y_center = clip_resized.h / 2
    clip_cropped = crop(clip_resized, width=720, height=1280, x_center=x_center, y_center=y_center)
    yPos=0.2

    # Modifications to function calls and iterations in your existing script
    annotations = []
    start_time = 0



    # Create a bubble for the main post
    main_post_img_path = create_text_bubble(post['post'], post['user'], "AskReddit")
    main_post_clip = ImageClip(main_post_img_path).set_duration(5).set_start(start_time).set_position(("center", yPos), relative=True)
    annotations.append(main_post_clip)
    start_time += 5

    # Loop over comments to create bubbles
    for comment in post['comments']:
        img_path = create_text_bubble(comment['text'], comment['user'], "AskReddit")
        img_clip = ImageClip(img_path).set_duration(4).set_start(start_time).set_position('center')
        annotations.append(img_clip)
        start_time += 4.5

    # Final composition and video generation
    final_clips = [clip_cropped] + annotations
    final_video = CompositeVideoClip(final_clips)
    final_video.write_videofile(output_video_path, fps=24, codec="libx264", preset="fast")


# Dummy data to represent API output
redditPull = scrape_questions_and_answers()
print("REDDIT SCRAPED! Generating video...")
# Grab yt minecraft gameplay:
download_clip()
# Add bubbles and compile:
for post_id, pInfo in redditPull.items():
    make_vid(pInfo)