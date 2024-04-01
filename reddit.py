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
    top_posts = subreddit.top('year', limit=1)  # Adjust 'limit' for the number of posts

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
    top_posts = subreddit.top('month', limit=5)  # Adjust 'limit' for the number of posts

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


#  ---------------------------------------------------------------------------------
import praw
import os
import json

# Set up PRAW with your Reddit API credentials
reddit = praw.Reddit(
    client_id='iwdABdbDIKeTvNEee5ojlw',
    client_secret='Bv_QRYI2doViQWKastzTlbz2elZZdw',
    user_agent="idk"
)

def save_posts_to_file(posts, filename='saved_posts.json'):
    # Initialize existing_posts as an empty dictionary
    existing_posts = {}
    
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                existing_posts = json.load(file)
        except json.JSONDecodeError:
            # If JSON is empty or invalid, keep existing_posts as an empty dictionary
            print(f"Warning: {filename} is empty or contains invalid JSON. It will be overwritten.")

    # Update existing posts with new ones, avoiding duplicates
    existing_posts.update(posts)

    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(existing_posts, file, indent=4)

def scrape_questions_and_answers():
    subreddit = reddit.subreddit('AskReddit')
    top_posts = subreddit.top(limit=30, time_filter="month")

    qa_dict = {}

    for post in top_posts:
        post_id = post.id
        if post_id not in qa_dict:  # Check if the post is already processed
            qa_dict[post_id] = {'post': post.title, 'user': "u/" + str(post.author.name), 'comments': []}
            top_comments = list(post.comments)[:15]
            for comment in top_comments:
                if comment.body != "[deleted]":
                    qa_dict[post_id]['comments'].append({'text': comment.body, 'user': "u/" + str(comment.author)})

    save_posts_to_file(qa_dict)

def get_unprocessed_post(filename='saved_posts.json'):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            posts = json.load(file)

        for post_id, post_info in posts.items():
            if 'processed' not in post_info or not post_info['processed']:
                # Mark as processed (to avoid re-fetching in the future)
                posts[post_id]['processed'] = True
                save_posts_to_file(posts, filename)
                return post_info

        # If all posts are processed, fetch new ones
        print("RAN OUT OF POSTS, GETTING NEW ONES...")
        scrape_questions_and_answers()
        return get_unprocessed_post(filename)
    else:
        # No file found, fetch new posts
        print("NO POSTS FILE FOUND, GETTING POSTS...")
        scrape_questions_and_answers()
        return get_unprocessed_post(filename)


        
# RUNS WHEN NOT AN IMPORT:
if __name__ == "__main__":
    post = get_unprocessed_post()
    print(post['post'])
