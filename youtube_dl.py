import subprocess
import random
import yt_dlp

# URLS:
#  OG minecraft parcour (GOOD): https://www.youtube.com/watch?v=n_Dv4JMiwK8
# Short satisfyig stuff (10hr)(watermark): https://www.youtube.com/watch?v=fYPC3yraYs8 (GOT CONTENT DETECTED!)
# Slightly better satisfying stuff (1hr): https://www.youtube.com/watch?v=d8vpIg1fWGA

video_url = 'https://www.youtube.com/watch?v=d8vpIg1fWGA'
blur = False
speed = 2.0

def download_clip():
    global blur
    global video_url

    

    ydl_opts = {
        'format': 'bestvideo[height<=1280]/best',
        'quiet': True,
        'no_warnings': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        video_url = info_dict.get('url', None)
        duration = info_dict.get('duration', None)

    # Calculate random start time
    start_time = random.randint(20, max(80, duration - 120))  # Ensures a 1-minute clip (and cuts out intro + outro that might not be parcour)

    ffmpeg_command = [
        'ffmpeg',
        '-y',
        '-ss', str(start_time),  # Fast seek to start
        '-t', f'{60*speed}',  # Duration of the clip
        '-i', video_url,
        # '-vf', "crop=ih*(9/16):ih",  # Crop to 9:16 aspect ratio, maintaining full height
        '-vf', f"crop=ih*(9/16):ih,setpts={1/speed}*PTS",  # Crop to 9:16 and speed up 2x
        '-r', '60',  # Set frame rate
        '-c:v', 'libx264',  # Use H.264 codec for video
        '-preset', 'slow',  # Faster encoding preset
        '-an',  # No audio
        'output/input_video.mp4'  # Output file
    ]

    # Run the command
    subprocess.run(ffmpeg_command)

    if blur:
        blur_rectangle_in_video()

from moviepy.editor import VideoFileClip, vfx
import shutil

def blur_rectangle_in_video():
    input_path = 'output/input_video.mp4'
    temp_path = 'output/temp_input_video_blurred.mp4'

    # Load the video file
    clip = VideoFileClip(input_path)

    # Apply the blur function
    blurred_clip = clip.fl_image(blur_bottom_fifth)

    # Write the result to a temporary file
    blurred_clip.write_videofile(temp_path, codec='libx264', preset="slow")

    # Overwrite the original file with the new blurred file
    shutil.move(temp_path, input_path)



from skimage.filters import gaussian
import numpy as np

def blur_bottom_fifth(image, sigma=10):
    """Blur only the bottom fifth of the image, excluding 40% of the width from the sides."""
    # Define the boundaries for the bottom fifth and the side margins
    height, width, _ = image.shape
    bottom_start = 12 * height // 13
    side_margin = width // 4  # 25% of the width from each side

    # Extract the regions: top four-fifths, bottom fifth, and side margins
    top = image[:bottom_start, :]
    bottom = image[bottom_start:, side_margin:-side_margin]

    # Apply blur to the bottom part for each color channel
    bottom_blurred = np.zeros_like(bottom)
    for i in range(3):  # Assuming RGB image
        bottom_blurred[:, :, i] = gaussian(bottom[:, :, i].astype(float), sigma=sigma)

    # Create a blank region for the side margins in the bottom part to avoid blurring them
    left_margin = image[bottom_start:, :side_margin]
    right_margin = image[bottom_start:, -side_margin:]

    # Concatenate the margins with the blurred bottom
    bottom_combined = np.concatenate((left_margin, bottom_blurred, right_margin), axis=1)

    # Concatenate the top part with the combined bottom part
    blurred_image = np.concatenate((top, bottom_combined), axis=0)

    return blurred_image



# RUNS WHEN NOT AN IMPORT:
if __name__ == "__main__":
    download_clip()
    # blur_rectangle_in_video()
