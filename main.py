import praw
import json
import requests
from bs4 import BeautifulSoup
import os
from sys import argv


# Initialize Reddit instance
reddit = praw.Reddit(
    user_agent="MyRedditBot/1.0",  # Customize this string to uniquely identify your application
    client_id="xk85F2QCXCOManzrgXdZHQ",
    client_secret="6oZFMC-Ai67eAXs75RUJm50Q5ObzcQ",
    username="lilbillyjoieik",
    password="CS172Project"
)
#TOTAL SUBREDDITS SET FOR SAMPLE AND SUBMISSION PURPOSES
def get_subreddit_names(limit=1000, total_subreddits=5000): #CHANGE THESE VALUES TO CRAWL REDDIT TO DESIRED SIZE TYPICALL LIMIT IS 1000 and TOTAL SUBREDDITS = 5000 for 500 MB of raw data
#def get_subreddit_names(limit=1000, total_subreddits=5000):
    subreddit_names = []
    num_collected = 0
    cnt = 0; 
    while num_collected < total_subreddits:
        batch_size = min(limit, total_subreddits - num_collected)
        for subreddit in reddit.subreddits.popular(limit=batch_size):
            cnt += 1
            print(f"Grabbing subreddit {cnt}")
            subreddit_names.append(subreddit.display_name)
            num_collected += 1
            if num_collected >= total_subreddits:
                break
    return subreddit_names

def write_subreddits_to_file(subreddits, filename):
    with open(filename, 'w') as file:
        for subreddit in subreddits:
            file.write(subreddit + '\n')

# Example usage
# subreddit_names = get_subreddit_names(total_subreddits=10) 
subreddit_names = get_subreddit_names(total_subreddits=5000)
write_subreddits_to_file(subreddit_names, 'subreddit_names.txt')
