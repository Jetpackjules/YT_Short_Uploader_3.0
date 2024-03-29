import subprocess
import random
import yt_dlp

def download_clip():
    video_url = 'https://www.youtube.com/watch?v=n_Dv4JMiwK8'

    ydl_opts = {
        'format': 'bestvideo',
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
        '-ss', str(start_time),
        '-i', video_url,
        '-c', 'copy',
        '-t', '53', # A little less than a min cuz it tends to overshoot duration
        '-an',
        '-hide_banner',
        'output\\input_video.webm'
        
    ]

    # Run the command
    subprocess.run(ffmpeg_command)