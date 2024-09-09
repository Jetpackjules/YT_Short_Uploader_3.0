import praw
import os
import json
from helper import retain_latest_entries, has_profanity

# Set up PRAW with your Reddit API credentials
reddit = praw.Reddit(
    client_id='iwdABdbDIKeTvNEee5ojlw',
    client_secret='Bv_QRYI2doViQWKastzTlbz2elZZdw',
    user_agent="idk"
)

def save_posts_to_file(posts, filename):
    existing_posts = {}
    
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            try:
                existing_posts = json.load(file)
            except json.JSONDecodeError:
                print(f"Warning: {filename} is empty or contains invalid JSON. It will be overwritten.")

    for post_id, post_data in posts.items():
        if post_id in existing_posts:
            existing_posts[post_id].update(post_data)
            existing_posts[post_id]['processed'] = existing_posts[post_id].get('processed', False)
        else:
            existing_posts[post_id] = post_data

    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(existing_posts, file, indent=4)

def scrape_questions_and_answers(subreddit_name='AskReddit'):
    subreddit = reddit.subreddit(subreddit_name)
    filename=f'Reddit_Posts/{subreddit_name}_saved_posts.json'
    retain_latest_entries(filename, 100)
    

    existing_post_ids = set()
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            try:
                posts = json.load(file)
                existing_post_ids = set(posts.keys())
            except json.JSONDecodeError:
                posts = {}


    # Initialize the dictionary to hold questions and answers
    qa_dict = {}
    total_valid_posts = 0

    def calculate_tts_time(char_count, word_count):
        return (0.04 * char_count + 0.05 * word_count)

    # Continue fetching until we have 31 non-NSFW posts
    post_limit = 0
    while total_valid_posts < 12:
        post_limit += 75
        top_posts = subreddit.top(limit=post_limit, time_filter="week")  # Fetch more posts in each iteration to ensure we reach the required number

        for post in top_posts:
            # print(post.title)
            if post.id in existing_post_ids:
                print("Skipping existing post...")
                continue  # Skip posts that are already processed
                

            if (not post.over_18) and (not has_profanity(post.title)) and (not has_profanity(post.selftext)):  # Check if the post is NSFW and skip if it is
                desc_char_count = len(post.selftext)
                desc_word_count = len(post.selftext.split())
                post_char_count = len(post.title)
                post_word_count = len(post.title.split())
                print("Desc time: ", calculate_tts_time(desc_char_count, desc_word_count))
                if (calculate_tts_time(desc_char_count, desc_word_count) > 57-calculate_tts_time(post_char_count, post_word_count)): #Check if post and desc fits under a min
                    print("Post desc too long for 1 min video! - Skipping...")
                    continue

                print("New posts found: ", str(total_valid_posts))
                post_id = post.id
                total_valid_posts += 1
                author_name = "u/[deleted]" if post.author is None else "u/" + str(post.author.name)

                qa_dict[post_id] = {
                    'post': post.title,
                    'body': post.selftext,
                    'user': author_name,
                    'comments': []
                }


            
                top_comments = list(post.comments)[:11]
                for comment in top_comments:
                    if ((comment.body != "[deleted]") and (not has_profanity(comment.body))):
                        qa_dict[post_id]['comments'].append({
                            'text': comment.body,
                            'user': "u/" + str(comment.author)
                        })
            else:
                print("NSFW - Skipping...")
            if total_valid_posts >= 12:
                break  # Exit the loop once we have enough posts

    save_posts_to_file(qa_dict, filename)
    return qa_dict

def get_unprocessed_post(subreddit='AskReddit', process=True):
    filename=f'Reddit_Posts/{subreddit}_saved_posts.json'
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            try:
                posts = json.load(file)
                existing_post_ids = set(posts.keys())
            except json.JSONDecodeError:
                posts = {}
                
        unprocessed_found = False
        for post_id, post_info in posts.items():
            if ('processed' not in post_info) or (not post_info['processed']):
                unprocessed_found = True
                if process:
                    post_info['processed'] = True
                save_posts_to_file(posts, filename)
                return post_info

        if not unprocessed_found:
            print("RAN OUT OF POSTS, GETTING NEW ONES...")
            previous_post_count = len(posts)
            new_posts = scrape_questions_and_answers(subreddit)
            
            with open(filename, 'r', encoding='utf-8') as file:
                posts = json.load(file)
            
            if len(posts) == previous_post_count:
                print(f"Found {len(posts)} posts")
                print("ALL FETCHED POSTS ARE THE SAME, STOPPING EXECUTION.")
                return None
            else:
                return get_unprocessed_post(subreddit, process)
    else:
        print("NO POSTS FILE FOUND, GETTING POSTS...")
        scrape_questions_and_answers(subreddit)
        return get_unprocessed_post(subreddit, process)
        
# RUNS WHEN NOT AN IMPORT:
if __name__ == "__main__":
    subreddit = "AskReddit"
    subreddit = "offmychest"
    scrape_questions_and_answers(subreddit)


    # post = get_unprocessed_post(subreddit, process=False)
    # if post is not None:
    #     print(post['post'])
    # else:
    #     print("No unprocessed posts available.")
