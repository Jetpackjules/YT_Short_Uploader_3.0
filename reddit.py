import praw
import os
# import tts

# Set up PRAW with your Reddit API credentials
reddit = praw.Reddit(
    client_id='iwdABdbDIKeTvNEee5ojlw',
    client_secret='Bv_QRYI2doViQWKastzTlbz2elZZdw',
    user_agent="idk"
)

def scrape_questions_and_answers():
    # Access the r/AskReddit subreddit and get the top posts of the day
    subreddit = reddit.subreddit('AskReddit')
    top_posts = subreddit.top('day', limit=1)  # Adjust 'limit' for the number of posts

    qa_list = []  # This will store our questions and answers

    for post in top_posts:
        # Add the post title (the question) as the first item in the list
        qa_list.append(post.title)
        
        # Fetch the top comments (the answers)
        top_comments = list(post.comments)[:6]  # Adjust for the number of comments you want
        for idx, comment in enumerate(top_comments, start=1):
            # Append each comment to the list
            qa_list.append(comment.body)

    return qa_list


def scrape_questions_and_answers():
    # Access the r/AskReddit subreddit and get the top posts of the day
    subreddit = reddit.subreddit('AskReddit')
    top_posts = subreddit.top('month', limit=1)  # Adjust 'limit' for the number of posts

    qa_dict = {}  # This will store our questions and answers along with usernames

    for post in top_posts:
        # Create a unique identifier for the post
        post_id = post.id
        # Add the post title (the question) and the poster's username as the first item in the dict
        qa_dict[post_id] = {'post': post.title, 'user': "u/"+str(post.author.name), 'comments': []}
        
        # Fetch the top comments (the answers)
        top_comments = list(post.comments)[:15]  # Adjust for the number of comments you want
        for comment in top_comments:
            if comment.body != "[deleted]":
                # Append each comment with the commenter's username to the list under the post's entry
                qa_dict[post_id]['comments'].append({'text': comment.body, 'user': ("u/"+str(comment.author))})

    return qa_dict

