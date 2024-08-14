import subprocess
import random
import yt_dlp

# URLS:
#  OG minecraft parcour (GOOD): https://www.youtube.com/watch?v=n_Dv4JMiwK8
# Short satisfyig stuff (10hr)(watermark): https://www.youtube.com/watch?v=fYPC3yraYs8 (GOT CONTENT DETECTED!)
# Slightly better satisfying stuff (1hr): https://www.youtube.com/watch?v=d8vpIg1fWGA


# FIND SOURCE OF THIS BACKGROUND!: https://www.youtube.com/shorts/1fEXqv7FkrU?feature=share
# A little narrow aspect ratio?? https://www.youtube.com/watch?v=OOpcXTTKZaA&t=213s # THIS ONE IS GODDAM BROKEN!
#1 HR COOKING DECENT WITH CC - https://www.youtube.com/watch?v=uFHfyqOztvg
videos = {
    # "satisfying_1hr": {"url": "https://www.youtube.com/watch?v=d8vpIg1fWGA", "length": 60, "speed": 2.0, "blur": False},
    "SAT-22": {"url": "https://www.youtube.com/watch?v=GOxi2-3fVIo", "length": 22, "speed": 2.0, "blur": False},
    "3D-60": {"url": "https://www.youtube.com/watch?v=Lx2yQ-CVoxQ", "length": 60, "speed": 2.0, "blur": False}, #GOOD
    # "SAND-30": {"url": "https://www.youtube.com/watch?v=OOpcXTTKZaA", "length": 30, "speed": 2.0, "blur": False}, #GOOD #error??? #Error! #ERRRORORORORORO!! #DISCONTINUED
    "SAT-10": {"url": "https://www.youtube.com/watch?v=j9lPiUVZ9_c", "length": 10, "speed": 2.0, "blur": False},
    "SAT-20": {"url": "https://www.youtube.com/watch?v=6ff4SkmB_4A", "length": 20, "speed": 2.0, "blur": False},
    "COK-60": {"url": "https://www.youtube.com/watch?v=uFHfyqOztvg", "length": 60, "speed": 2.0, "blur": False}

}
#MAYBE ADD THIS 1HR one?? https://www.youtube.com/watch?v=orBT5NJkjrw (Not as good but works in a pinch and CC!)


def download_clip(name):
    video_info = videos.get(name)
    if not video_info:
        print(f"No video found with name: {name}")
        stall = input("NO VIDEO FOUND! Press enter to continue...")
        return

    video_url = video_info["url"]
    blur = video_info["blur"]
    speed = video_info["speed"]
    
    

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
    start_time = random.randint(20, max(85, duration - 120))  # Ensures a 1-minute clip (and cuts out intro + outro that might not be parcour)

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
        'output\\input_video.mp4'  # Output file
    ]

    # Run the command
    subprocess.run(ffmpeg_command)

    if blur:
        blur_rectangle_in_video()

# Global variable to store the selected video name
selected_video = None
def download_random_clip():
    global selected_video
    # Generate a list of video names and weights based on their length
    video_names = list(videos.keys())
    weights = [video["length"] for video in videos.values()]

    # Select a video based on its length (as weight)
    selected_video = random.choices(video_names, weights=weights, k=1)[0]
    print(selected_video)
    # Download the selected clip
    download_clip(selected_video)
    return selected_video


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

import subprocess as sp
from realesrgan_ncnn_py import Realesrgan

def ai_upscale_video(input_path, output_path, target_width=608, target_height=1080, gpuid=0):
    """
    Upscales the video using Real-ESRGAN and resizes it back to the original resolution.
    """
    # Initialize the Real-ESRGAN model
    realesrgan = Realesrgan(gpuid=gpuid)


    # FFmpeg commands to read the video and write the output
    ffmpeg_command_in = [
        'ffmpeg',
        '-i', input_path,
        '-f', 'rawvideo',
        '-pix_fmt', 'rgb24',
        '-'
    ]
    
    ffmpeg_command_out = [
        'ffmpeg',
        '-y',
        '-f', 'rawvideo',
        '-pix_fmt', 'rgb24',
        '-s', f'{target_width}x{target_height}',
        '-r', '60',
        '-i', '-',
        '-vf', f'scale={target_width}:{target_height}',
        '-c:v', 'libx264',
        '-preset', 'slow',
        output_path
    ]

    # Open subprocesses for FFmpeg
    pipe_in = sp.Popen(ffmpeg_command_in, stdout=sp.PIPE)
    pipe_out = sp.Popen(ffmpeg_command_out, stdin=sp.PIPE)

    # Process the video frame by frame
    while True:
        raw_frame = pipe_in.stdout.read(target_width * target_height * 3)  # Read one frame
        if not raw_frame:
            break
        # Use Real-ESRGAN to upscale the frame
        upscaled_frame = realesrgan.process_bytes(raw_frame, target_width, target_height, 3)
        # Write the upscaled frame to FFmpeg output
        pipe_out.stdin.write(upscaled_frame)

    # Close the FFmpeg processes
    pipe_in.stdout.close()
    pipe_out.stdin.close()
    pipe_in.wait()
    pipe_out.wait()

# Example usage:
# ai_upscale_video('output\\input_video.mp4', 'output\\input_video_upscaled.mp4')


# RUNS WHEN NOT AN IMPORT:
if __name__ == "__main__":
    # download_clip("SAT-60")
    # download_random_clip()
    # blur_rectangle_in_video()
    ai_upscale_video('output/input_video.mp4', 'output/input_video_upscaled.mp4')
