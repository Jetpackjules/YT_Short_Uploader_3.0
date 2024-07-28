import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import os
from datetime import datetime

def get_scheduled_video_info():
    # Set up the YouTube API client
    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "auths/client_secrets.json"  # Update this path

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_local_server(port=8080)
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

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
            scheduled_upload_date = datetime.strptime(scheduled_upload_date_str, "%Y-%m-%dT%H:%M:%SZ")

            # Calculate the offset in days between the scheduled upload date and today's date
            today = datetime.utcnow()
            offset_days = (scheduled_upload_date - today).days

            # Print the video's scheduled upload date and offset
            print(f"Video's scheduled upload date: {scheduled_upload_date_str}")
            print(f"The offset between today and the video's scheduled upload date is {offset_days} days.")
            return

    print("No scheduled videos found.")

if __name__ == "__main__":
    get_scheduled_video_info()
