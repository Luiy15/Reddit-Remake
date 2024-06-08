import praw
import json
import requests
from bs4 import BeautifulSoup
import os
import time

import lucene
from org.apache.lucene.store import SimpleFSDirectory, NIOFSDirectory
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, IndexOptions, DirectoryReader
from org.apache.lucene.search import IndexSearcher
import json

reddit = praw.Reddit(
    user_agent="MyRedditBot/1.0",  # Customize this string to uniquely identify your application
    client_id="xk85F2QCXCOManzrgXdZHQ",
    client_secret="6oZFMC-Ai67eAXs75RUJm50Q5ObzcQ",
    username="lilbillyjoieik",
    password="CS172Project"
)

def get_html_title(url):
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'  # Set encoding to utf-8
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup.title.string.strip() if soup.title else 'No title found'
    except requests.RequestException as e:
        return f'Failed to retrieve title: {str(e)}'
    except Exception as e:
        return f'Error during HTML parsing: {str(e)}'

def collect_all_posts(subreddit_name):
    subreddit = reddit.subreddit(subreddit_name)
    collected_posts = []
    seen_posts = set()
    cnt = 0
    last_post = None

    while len(collected_posts) < 50: # COMMENT THIS LINE OUT IF WANTING TO COLLECT MORE DATA
        try:
            if last_post:
                posts = subreddit.new(limit=10, params={'after': last_post}) # TYPICAL LIMIT 10
            else:
                posts = subreddit.new(limit=10) # TYPICAL LIMIT 10 

            new_posts = list(posts)
            if not new_posts:
                break

            for post in new_posts:
                cnt += 1
                print(f"Grabbing post {cnt}")
                if post.id in seen_posts:
                    continue  # Skip duplicate posts
                seen_posts.add(post.id)

                post_data = {
                    'title': post.title,
                    'author': post.author.name if post.author else 'Anonymous',
                    'content': post.selftext,
                    'score': post.score,
                    'url': post.url,
                    'num_comments': post.num_comments,
                    'upvote_ratio': post.upvote_ratio,
                    'is_nsfw': post.over_18,
                    'created_utc': post.created_utc
                }
                # Add HTML title if the post includes a URL
                if post.url:
                    post_data['linked_page_title'] = get_html_title(post.url)
                    
                collected_posts.append(post_data)

            last_post = new_posts[-1].fullname
            time.sleep(1)  # Avoid hitting rate limits

        except KeyboardInterrupt:
            print("Program interrupted. Saving data...")
            return collected_posts
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            time.sleep(5)  # Wait before retrying

    return collected_posts

def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)


if __name__ == "__main__":
    # Ensure the Posts directory exists
    output_directory = "Posts"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Read subreddit names from file
    subreddit_names_file = "subreddit_names.txt"
    with open(subreddit_names_file, 'r') as file:
        subreddit_names = [line.strip() for line in file.readlines()]

    for subreddit_name in subreddit_names:
        posts = collect_all_posts(subreddit_name)  # Collect all posts from the subreddit

        # Save posts to JSON file within the "Posts" directory
        json_filename = os.path.join(output_directory, f"{subreddit_name}_reddit_posts.json")
        save_to_json(posts, json_filename)  # Save posts to JSON file
        
        # Check file size
        file_size = os.path.getsize(json_filename) / (1024 * 1024)  # Convert bytes to MB
        if file_size != -1:
            print(f"The size of {json_filename} is {file_size:.2f} MB.")
        else:
            print(f"The file {json_filename} does not exist.")