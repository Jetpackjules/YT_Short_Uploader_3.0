import subprocess
import random
import yt_dlp

# URLS:
#  OG minecraft parcour (GOOD): https://www.youtube.com/watch?v=n_Dv4JMiwK8
# Short satisfyig stuff: https://www.youtube.com/watch?v=G1XGfIqHd4o




def download_clip():
    video_url = 'https://www.youtube.com/watch?v=G1XGfIqHd4o'

    

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
        '-t', '60',  # Duration of the clip
        '-i', video_url,
        '-vf', "crop=ih*(9/16):ih",  # Crop to 9:16 aspect ratio, maintaining full height
        '-r', '60',  # Set frame rate
        '-c:v', 'libx264',  # Use H.264 codec for video
        '-preset', 'slow',  # Faster encoding preset
        '-an',  # No audio
        'output/input_video.mp4'  # Output file
    ]

    # Run the command
    subprocess.run(ffmpeg_command)

# RUNS WHEN NOT AN IMPORT:
if __name__ == "__main__":
    download_clip()