#!/usr/bin/python

import httplib2
import os
import random
import sys
import time

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
import helper

# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google API Console at
# https://console.cloud.google.com/.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "auths\\client_secrets.json"

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube"# REMOVED A "".upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
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

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


def get_authenticated_service(args):
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
                                   scope=YOUTUBE_UPLOAD_SCOPE,
                                   message=MISSING_CLIENT_SECRETS_MESSAGE)

    
    # print("%s-oauth2.json" % sys.argv[0])
    storage = Storage("auths\\oauth2.json")
    # storage = Storage("%s-oauth2.json" % sys.argv[0])

    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage, args)
        input("NEW CREDS LOADED - RESTART PROGRAM!")

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                 http=credentials.authorize(httplib2.Http()))

def add_video_to_playlist(youtube, video_id, playlist_id):
    add_to_playlist_request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
    )
    add_to_playlist_request.execute()
    print(f"Video id '{video_id}' was added to playlist id '{playlist_id}'.")

def set_thumbnail(youtube, video_id, thumbnail_path):
    if not os.path.exists(thumbnail_path):
        print(f"Thumbnail file {thumbnail_path} not found.")
        return

    try:
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_path)
        ).execute()
        print(f"Thumbnail for video id '{video_id}' successfully uploaded.")
    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")



def initialize_upload(youtube, options):
    tags = None
    if options.keywords:
        tags = options.keywords.split(", ")
        print("PROCESSED TAGS: ", tags)

    body = dict(
        snippet=dict(
            title=options.title,
            description=options.description,
            tags=tags,
            categoryId=options.category
        ),
        status=dict(
            privacyStatus=options.privacyStatus,
            publishAt=options.publishTime,
            selfDeclaredMadeForKids=False
        )
    )

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        # The chunksize parameter specifies the size of each chunk of data, in
        # bytes, that will be uploaded at a time. Set a higher value for
        # reliable connections as fewer chunks lead to faster uploads. Set a lower
        # value for better recovery on less reliable connections.
        #
        # Setting "chunksize" equal to -1 in the code below means that the entire
        # file will be uploaded in a single HTTP request. (If the upload fails,
        # it will still be retried where it left off.) This is usually a best
        # practice, but if you're using Python older than 2.6 or if you're
        # running on App Engine, you should set the chunksize to something like
        # 1024 * 1024 (1 megabyte).
        media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
    )

    response = resumable_upload(insert_request)

    # Add video to playlist if upload was successful
    if response and 'id' in response:
        video_id = response['id']
        playlist_id = options.playlistId
        thumbnail_path = "output\\thumbnail.png"

        #Doesnt really work :( TBD
        # if playlist_id:
        #     add_video_to_playlist(youtube, video_id, playlist_id)
        # if thumbnail_path:
        #     set_thumbnail(youtube, video_id, thumbnail_path)


# This method implements an exponential backoff strategy to resume a
# failed upload.


def resumable_upload(insert_request):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print("Uploading file...")
            status, response = insert_request.next_chunk()
            if response is not None:
                if 'id' in response:
                    print("Video id '%s' was successfully uploaded." %
                          response['id'])
                else:
                    exit("The upload failed with an unexpected response: %s" % response)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                                     e.content)
            else:
                raise
            
        except RETRIABLE_EXCEPTIONS as e:
            error = "A retriable error occurred: %s" % e

        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit("No longer attempting to retry.")

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print("Sleeping %f seconds and then retrying..." % sleep_seconds)
            time.sleep(sleep_seconds)


VALID_PRIVACY_STATUSES = ['private', 'public', 'unlisted']  # Example privacy statuses
import argparse


# Category 24 is entertainment, what everyone else uses
def upload_video(file, title="Test Title", description="Test Description", category="24", keywords="", privacyStatus="private", publishTime="default", playlistId="PLw8KwGTnJQ8QJbiuyzmm7eTpqbIbsLPTf"):
    if not os.path.exists(file):
        exit("Please specify a valid file using the --file= parameter.")

    args = argparser.parse_args()
    # Update args with function parameters if not set via command line
    args.file = file
    args.title = title
    args.description = description
    args.category = category
    args.keywords = keywords
    args.privacyStatus = privacyStatus
    args.playlistId = playlistId

    if publishTime == "default":
        publishTime = helper.next_optimal_post_time_final()

    args.publishTime = publishTime



    # args = argparse.Namespace(file=file, title=title, description=description, category=category, keywords=keywords, privacyStatus=privacyStatus, publishTime=publishTime)
    
    youtube = get_authenticated_service(args)
    try:
        initialize_upload(youtube, args)
    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")


if __name__ == '__main__':
    from ai import gen_description, gen_tags
    transcript = "What celebrity has abused plastic surgery to the point they don't look like their former selves?\n\nSimon Cowell. I feel like Simon Cowell from 20 years ago would ridicule and lambast current Simon worse than any crazy X Factor or American Idol contestant\n\nDonatella Versace which is heartbreaking because she didn't need any of the surgery\n\nMadonna.\n\nMickey Rourke looks like he was made by a cobbler. - Henchman 21\n\nSmokey Robinson. If the surgeons pull his face any tighter it'll tear with a snap. He used to be gorgeous.\n\nFamke Janssen was a shock to me\n\nJessica Simpson doesn't look like herself anymore\n\nCarrot Top\n\n*Sharon and Kelly Osborne"
    upload_video("output\\video_subbed.mp4", description=gen_description(transcript) + "\n\n Vol: " + str(round(13, 2)), keywords=gen_tags(transcript), title="Test Upload")