import subprocess
import random
import yt_dlp

def download_clip():
    video_url = 'https://www.youtube.com/watch?v=n_Dv4JMiwK8'

    ydl_opts = {
        'format': 'bestvideo[height<=1280]',
        'quiet': True,
        'no_warnings': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        video_url = info_dict.get('url', None)
        duration = info_dict.get('duration', None)

    # Calculate random start time
    start_time = random.randint(20, max(80, duration - 120))  # Ensures a 1-minute clip (and cuts out intro + outro that might not be parcour)

    # ffmpeg_command = [
    #     'ffmpeg',
    #     '-y',
    #     '-ss', str(start_time),
    #     '-i', video_url,
    #     '-c', 'copy',
    #     '-t', '50', # A little less than a min cuz it tends to overshoot duration
    #     '-an',
    #     '-vf', 'scale=720:1280,fps=24',  # Set resolution and frame rate
    #     '-hide_banner',
    #     'output\\input_video.webm'
    # ]
    ffmpeg_command = [
        'ffmpeg',
        '-y',
        '-ss', str(start_time),  # Fast seek to start
        '-t', '50',  # Duration of the clip
        '-i', video_url,
        '-vf', 'scale=-2:1280,crop=720:1280',  # Scale to 1280 height and crop to 720x1280
        '-r', '59',  # Set frame rate
        '-c:v', 'libx264',  # Use H.264 codec for video
        # '-crf', '28',  # CRF for a balance between quality and size
        '-preset', 'medium',  # Faster encoding preset
        # '-b:v', '2000k',  # Limit video bitrate
        '-an',  # No audio
        'output/input_video.mp4'  # Output file
    ]



    # Run the command
    subprocess.run(ffmpeg_command)

# RUNS WHEN NOT AN IMPORT:
if __name__ == "__main__":
    download_clip()