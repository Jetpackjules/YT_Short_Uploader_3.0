import praw
import os
import tts

# Set up PRAW with your Reddit API credentials
reddit = praw.Reddit(
    client_id='iwdABdbDIKeTvNEee5ojlw',
    client_secret='Bv_QRYI2doViQWKastzTlbz2elZZdw',
    user_agent="idk"
)

def scrape_and_convert_to_audio():
    # Access the r/AskReddit subreddit and get the top posts of the day
    subreddit = reddit.subreddit('AskReddit')
    top_posts = subreddit.top('day', limit=1)  # Adjust 'limit' for the number of posts

    for index, post in enumerate(top_posts, start=1):
        # Prepare the text for TTS: Post title followed by top comments
        text_for_tts = f"Question {index}: {post.title} "
        top_comments = list(post.comments)[:6]  # Get the top 2 comments
        for idx, comment in enumerate(top_comments, start=1):
            text_for_tts += f" Answer {idx}: {comment.body} "

        # Convert the text to speech
        output = tts.speak(f'post_{index}', text_for_tts)
        print(f'Generated audio file at: {output}')

if __name__ == "__main__":
    scrape_and_convert_to_audio()
