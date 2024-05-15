import praw
import os
import json
import helper

# Set up PRAW with your Reddit API credentials
reddit = praw.Reddit(
    client_id='iwdABdbDIKeTvNEee5ojlw',
    client_secret='Bv_QRYI2doViQWKastzTlbz2elZZdw',
    user_agent="idk"
)

def save_posts_to_file(posts, filename='saved_posts.json'):
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

def scrape_questions_and_answers(existing_post_ids):
    subreddit = reddit.subreddit('AskReddit')
    
    # Initialize the dictionary to hold questions and answers
    qa_dict = {}
    total_non_nsfw_posts = 0

    # Continue fetching until we have 31 non-NSFW posts
    while total_non_nsfw_posts < 31:
        top_posts = subreddit.top(limit=200, time_filter="month")  # Fetch more posts in each iteration to ensure we reach the required number

        for post in top_posts:
            if post.id in existing_post_ids:
                continue  # Skip posts that are already processed

            if (not post.over_18) and (not helper.has_profanity(post.title)):  # Check if the post is NSFW and skip if it is
                post_id = post.id
                total_non_nsfw_posts += 1
                author_name = "u/[deleted]" if post.author is None else "u/" + str(post.author.name)

                qa_dict[post_id] = {
                    'post': post.title,
                    'user': author_name,
                    'comments': []
                }
                top_comments = list(post.comments)[:11]
                for comment in top_comments:
                    if ((comment.body != "[deleted]") and (not helper.has_profanity(comment.body))):
                        qa_dict[post_id]['comments'].append({
                            'text': comment.body,
                            'user': "u/" + str(comment.author)
                        })
            
            if total_non_nsfw_posts >= 31:
                break  # Exit the loop once we have enough posts

    save_posts_to_file(qa_dict)
    return qa_dict

def get_unprocessed_post(filename='saved_posts.json', process=True):
    existing_post_ids = set()
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
            new_posts = scrape_questions_and_answers(existing_post_ids)
            
            with open(filename, 'r', encoding='utf-8') as file:
                posts = json.load(file)
            
            if len(posts) == previous_post_count:
                print(f"Found {len(posts)} posts")
                print("ALL FETCHED POSTS ARE THE SAME, STOPPING EXECUTION.")
                return None
            else:
                return get_unprocessed_post(filename, process)
    else:
        print("NO POSTS FILE FOUND, GETTING POSTS...")
        scrape_questions_and_answers(existing_post_ids)
        return get_unprocessed_post(filename, process)
        
# RUNS WHEN NOT AN IMPORT:
if __name__ == "__main__":
    post = get_unprocessed_post(process=False)
    if post is not None:
        print(post['post'])
    else:
        print("No unprocessed posts available.")
