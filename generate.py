from PIL import Image, ImageDraw, ImageFont, ImageOps
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
from moviepy.video.fx.all import crop

import bubbles;

# Update these paths and values to suit your setup
input_video_path = "assets\\input_video.mp4"
output_video_path = "final_output.mp4"

# Dummy data to represent API output
post_title = "Example Question from Reddit"
comments = [
    {"user": "user1", "text": "This is a response from user1."},
    {"user": "user2", "text": "This is a longer response from user2, which may span multiple sentences. Here is the second sentence."}
]

# Video processing
clip = VideoFileClip(input_video_path)
clip_resized = clip.resize(height=1280)  # Resize to the desired height

# Crop to maintain aspect ratio and focus
x_center = clip_resized.w / 2
y_center = clip_resized.h / 2
clip_cropped = crop(clip_resized, width=720, height=1280, x_center=x_center, y_center=y_center)


# Modifications to function calls and iterations in your existing script
annotations = []
start_time = 0

# Create a bubble for the main post
main_post_img_path = bubbles.create_text_bubble(post_title, True)
main_post_clip = ImageClip(main_post_img_path).set_duration(5).set_start(start_time).set_position("center")
annotations.append(main_post_clip)
start_time += 5

# Loop over comments to create bubbles
for comment in comments:
    img_path = bubbles.create_text_bubble(comment['text'], False)
    img_clip = ImageClip(img_path).set_duration(5).set_start(start_time).set_position('center')
    annotations.append(img_clip)
    start_time += 5

# Final composition and video generation
final_clips = [clip_cropped] + annotations
final_video = CompositeVideoClip(final_clips)
final_video.write_videofile(output_video_path, fps=24, codec="libx264")
