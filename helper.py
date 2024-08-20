import subprocess
import os
from mutagen.mp3 import MP3

def run(command):
    # Attempted fix for multiple conda locs:
    output = subprocess.run("where conda", text=True, capture_output=True).stdout
    conda_path = output.strip().split('\n')[0]
    env_name = os.environ["CONDA_PREFIX"].split(os.path.sep)[-1]


    try:
        # RESULT = subprocess.run(f'{conda_path} run -v -n -cwd{env_name} {command}', check=True, capture_output=True, text=True, shell=True)

        # I THINK THIS WORKS!!! HOLY SHIT!
        result = subprocess.run(['powershell', '-Command', command], check=True, capture_output=True, text=True, shell=False, encoding='utf-8')
        if result.returncode != 0:
            print("RESULT RECIEVED: \n" + str(result))
            print("Command!s failed. Pausing execution...")
            input("Press Enter to continue...")  # This will pause execution until Enter is pressed
            sys.exit(1)  # Exit the script if needed
    except subprocess.CalledProcessError as e:
        print("Command failed with return code", e.returncode)
        print("Output:", e.output)
        print("Error:", e.stderr)


def save_as_srt(entries, output_file='output/bubbles/usernames.srt'):
    with open(output_file, 'w', encoding='utf-8') as f:
        for index, (start, end, user) in enumerate(entries, 1):
            start_srt = format_srt_time(start)
            end_srt = format_srt_time(end)
            f.write(f"{index}\n{start_srt} --> {end_srt}\n{user}\n\n")

def format_srt_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    # SRT format requires milliseconds, so we multiply the fractional part by 1000
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{milliseconds:03}"


from mutagen.mp3 import MP3
from moviepy.editor import VideoFileClip


def get_media_duration(file_path):
    """Returns the duration of an MP3 or MP4 file in seconds."""
    if file_path.lower().endswith('.mp3'):
        media = MP3(file_path)
        duration = media.info.length
    elif file_path.lower().endswith('.mp4'):
        with VideoFileClip(file_path) as video:
            duration = video.duration
    else:
        raise ValueError("Unsupported file format")

    return duration

import platform
def detect_os():
    """
    Detect the operating system of the current device.
    
    Returns:
        str: 'macOS' if the device is running macOS, 'Windows' if the device is running Windows, or 'Other' for other operating systems.
    """
    system = platform.system()
    if system == 'Darwin':
        return 'macOS'
    elif system == 'Windows':
        return 'Windows'
    else:
        return 'Other'


from moviepy.audio.AudioClip import AudioArrayClip
import numpy as np
def make_silent_audio(duration, sample_rate=44100):
    # Create a silent audio segment of the specified duration
    silent_segment = np.zeros((int(duration * sample_rate), 2))  # 2 channels for stereo
    silent_audio = AudioArrayClip(silent_segment, fps=sample_rate)
    return silent_audio

def clean(text):
    text = text.replace("*", "")
    text = text.replace("/", " or ")
    text = text.replace("…", "...")
    text = text.replace("’", "'")
    text = text.replace(" i ", " I ")    
    text = text.replace("i'", "I'")
    return text

import re

def contains_link(text):
    # Regular expression pattern to find URLs
    pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+|\b\w+\.(com|org|net|edu|gov|mil|co\.uk|info|io|biz)\b'
    # Search for the pattern in the text
    match = re.search(pattern, text)
    # Return True if a match is found, False otherwise
    return match is not None


import random
import json

# def generate_title():
#     words = ['CRAZY', 'UNBELIEVABLE', 'SHOCKING', 'HILARIOUS', 'EPIC', 'SAD', 'AMAZING', 'WOW', 'WHAT?!', 'HOW?!', 'NO WAY!', 'INSANE', 'MIND-BLOWING']
#     emojis = ['💀', '🤣', '😱', '👍', '😂', '😭', '🔥', '💯', '🌟', '👀', '🙌', '💥', '😜', '🎉', '🤔', '🧐', '🤯', '😕', '🙄', '🤓']

#     # Randomly pick 1 or 2 words and 1 to 3 emojis
#     chosen_words = ' '.join(random.sample(words, k=1))+"!"
#     # chosen_emojis = ''.join(random.sample(emojis, k=random.randint(1, 3)))

#     return f"{chosen_words}" # {chosen_emojis}"



def generate_title():
    # Path to the JSON file that stores the counts
    file_path = 'title_counts.json'
    
    # Try to load existing counts from the file, or initialize an empty dictionary if the file doesn't exist
    try:
        with open(file_path, 'r') as file:
            title_counts = json.load(file)
    except FileNotFoundError:
        title_counts = {}

    # Compact and catchy titles
    titles = [
        "Reddit’s Weirdest Questions",
        "3AM Reddit Secrets",
        "Reddit Riddles Solved",
        "Unseen Reddit Dramas",
        "Top Reddit Meltdowns",
        "Chilling Reddit Threads",
        "Reddit Nightmares Unveiled",
        "Reddit’s Epic Fails",
        "Weird Reddit Wonders",
        "Creepy Reddit Stories"
    ]

    # Select a random title
    title = random.choice(titles)

    # Update the count for the selected title
    if title in title_counts:
        title_counts[title] += 1
    else:
        title_counts[title] = 1

    # Append the part number if it has been chosen more than once
    full_title = title + (f" (Part {title_counts[title]})" if title_counts[title] > 1 else "")

    # Save the updated counts back to the JSON file
    with open(file_path, 'w') as file:
        json.dump(title_counts, file, indent=4)

    return full_title


import datetime
import pytz

def next_optimal_post_time_final():
    # Define the time slots for posting
    optimal_times_weekday = [(10, 12), (14, 18), (20, 23)]
    optimal_times_weekend = [(11, 13), (16, 19)]

    # Get the current time in EST
    est = pytz.timezone('America/New_York')
    current_time = datetime.datetime.now(est)

    # Determine the day of the week
    weekday = current_time.weekday()

    # Choose the optimal times based on the current day
    if 0 <= weekday <= 4:  # Weekdays
        optimal_times = optimal_times_weekday
    else:  # Weekends
        optimal_times = optimal_times_weekend

    # Find the next optimal time
    for start, end in optimal_times:
        start_time = current_time.replace(hour=start, minute=0, second=0, microsecond=0)
        if current_time < start_time:
            # If current time is before the start of a slot, return the start of this slot
            next_optimal_time = start_time
            break
    else:
        # If current time is past all slots for the day, calculate the next day's first optimal slot
        next_day = current_time + timedelta(days=1+get_scheduled_video_offset()) #1+ latest upload
        next_day_weekday = next_day.weekday()

        if 0 <= next_day_weekday <= 4:  # Weekdays
            next_day_start = optimal_times_weekday[0][0]
        else:  # Weekend
            next_day_start = optimal_times_weekend[0][0]

        next_optimal_time = next_day.replace(hour=next_day_start, minute=0, second=0, microsecond=0)

    # Convert the next optimal time to UTC
    next_optimal_time_utc = next_optimal_time.astimezone(pytz.utc)

    # Format the datetime to ISO 8601 with fractional seconds and 'Z' designator
    next_optimal_time_iso8601 = next_optimal_time_utc.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

    return next_optimal_time_iso8601

def get_unprocessed_times():
    # Define specific times for tomorrow
    times = [datetime.time(hour=8, minute=30),  # 6:45 AM
             datetime.time(hour=13, minute=30),  # 3 PM
             datetime.time(hour=20, minute=0)]  # 9 PM
    return times

def times_for_tomorrow_pacific():
    # Get the current time in Pacific Time
    pacific = pytz.timezone('America/Los_Angeles')
    current_time = datetime.datetime.now(pacific)

    # Calculate tomorrow's date
    tomorrow = current_time + timedelta(days=1+get_scheduled_video_offset()) # <- THIS SHOULD BE ONE NORMALLY!
    
    # Define specific times for tomorrow
    times = get_unprocessed_times()

    # Create datetime objects for each specific time
    datetime_list = [datetime.datetime.combine(tomorrow, time) for time in times]

    # Convert times to UTC for consistency in output, similar to the example function
    datetime_list_utc = [dt.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z' for dt in datetime_list]

    return datetime_list_utc

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import os
# from datetime import datetime

import httplib2
import os
import random
import sys
import time

from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
from apiclient.discovery import build
from apiclient.errors import HttpError
from datetime import timedelta


def get_scheduled_video_offset():
    # Set up the YouTube API client
    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    CLIENT_SECRETS_FILE = "auths/client_secrets.json"


    MISSING_CLIENT_SECRETS_MESSAGE = """
    WARNING: Please configure OAuth 2.0

    To make this sample run you will need to populate the client_secrets.json file
    found at:

    %s

    with information from the API Console
    https://console.cloud.google.com/

    For more information about the client_secrets.json file format, please visit:
    https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
    """ % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                    CLIENT_SECRETS_FILE))


    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
                                   scope=scopes,
                                   message=MISSING_CLIENT_SECRETS_MESSAGE)

    
    # print("%s-oauth2.json" % sys.argv[0])
    storage = Storage("auths/oauth2.json")
    # storage = Storage("%s-oauth2.json" % sys.argv[0])

    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage)
        input("NEW CREDS LOADED - RESTART PROGRAM!")

    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                 http=credentials.authorize(httplib2.Http()))


    # Fetch videos uploaded by the authenticated user
    search_response = youtube.search().list(
        part="id,snippet",
        forMine=True,
        type="video",
        maxResults=50  # Fetch up to 50 videos to ensure we find scheduled ones
    ).execute()

    # Get video IDs
    video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]

    if not video_ids:
        print("No videos found.")
        return

    # Fetch details for the videos
    videos_response = youtube.videos().list(
        part="snippet,status",
        id=",".join(video_ids)
    ).execute()

    # Iterate through the videos and find the scheduled one
    for video in videos_response.get("items", []):
        if video["status"]["privacyStatus"] == "private" and "publishAt" in video["status"]:
            scheduled_upload_date_str = video["status"]["publishAt"]
            scheduled_upload_date = datetime.datetime.strptime(scheduled_upload_date_str, "%Y-%m-%dT%H:%M:%SZ")

            today = datetime.datetime.utcnow()

            # Set time to midnight
            scheduled_upload_date -= timedelta(hours=7)
            today -= timedelta(hours=7)
            # scheduled_upload_date = scheduled_upload_date.replace(hour=0, minute=0, second=0, microsecond=0)
            today = today.replace(hour=20, minute=0, second=0, microsecond=0)


            offset_days = ((scheduled_upload_date - today).days)

            print(f"The offset between today and the video's scheduled upload date is {offset_days} day(s).")
            return offset_days

    print("No scheduled videos found.")
    return 0

# import cv2
# def save_first_frame_as_png(video_path="output/video_subbed.mp4", output_path="output/thumbnail.png"):
#     # Check if the input video file exists
#     if not os.path.exists(video_path):
#         raise FileNotFoundError(f"The video file '{video_path}' does not exist.")
    
#     # Open the video file using OpenCV
#     video_capture = cv2.VideoCapture(video_path)
    
#     # Read the first frame
#     success, frame = video_capture.read()
    
#     # Check if the frame was successfully read
#     if not success:
#         raise RuntimeError(f"Failed to read the first frame from '{video_path}'.")
    
#     # Save the frame as a PNG image
#     cv2.imwrite(output_path, frame)
    
#     # Release the video capture object
#     video_capture.release()

#     print(f"The first frame of '{video_path}' has been saved as '{output_path}'.")


from better_profanity import profanity
def has_profanity(text):
    return profanity.contains_profanity(text)

def censor(text):
    return profanity.censor(text)

import json
def retain_latest_entries(file_path, num_entries=100):
    try:
        # Load the JSON data from the file
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Ensure that data is a dictionary
        if isinstance(data, dict):
            # Sort the dictionary keys based on the insertion order (Python 3.7+ guarantees dict order)
            keys = list(data.keys())
            keys_to_keep = keys[-num_entries:]

            # Create a new dictionary with only the latest `num_entries`
            new_data = {key: data[key] for key in keys_to_keep}

            # Save the updated data back to the JSON file
            with open(file_path, 'w') as file:
                json.dump(new_data, file, indent=4)

            print(f"Successfully retained the latest {num_entries} entries.")
            return True
        else:
            print("The JSON structure is not a dictionary. Please check the file.")
            return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False



if __name__ == '__main__':
    # get_scheduled_video_offset()
    # # Extract the hour from the third time (7 PM)
    # test = get_unprocessed_times()
    # hour_19 = test[2].hour


    # print(hour_19)  # Output: 19

    # save_first_frame_as_png()
    pass


