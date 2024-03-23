import subprocess
import random
import yt_dlp

def download_clip():
    video_url = 'https://www.youtube.com/watch?v=n_Dv4JMiwK8'

    # Use yt-dlp to get the direct video URL
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

    # FFmpeg command to download the segment
    ffmpeg_command = [
        'ffmpeg',
        '-y',
        '-ss', str(start_time),
        '-i', video_url,
        # '-c:v', 'libvpx-vp9', 
        '-c', 'copy',
        '-t', '60',  # duration to capture
        '-an',  # Audio codec for WebM
        '-hide_banner',
        'output\\input_video.webm'
        
    ]

    # Run the command
    subprocess.run(ffmpeg_command)

# download_clip()