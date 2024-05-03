import praw
import json
import scrapy

reddit = praw.Reddit(user_agent=True, 
                    client_id = "xk85F2QCXCOManzrgXdZHQ", 
                    client_secret = "6oZFMC-Ai67eAXs75RUJm50Q5ObzcQ",
                    username = "lilbillyjoieik",
                    password = "CS172Project"
                    )


def collect_posts(subreddit_name, num_posts):
    subreddit = reddit.subreddit(subreddit_name)        # get the subreddit object
    
    posts = subreddit.new(limit=num_posts)              # collects the number of posts from subreddit
    collected_posts = []                                # array of collected posts
    
                                                        
    for post in posts:                                  # extract relevant information from each post
        post_data = {
            'title': post.title,           
            'author': post.author.name,    
            'score': post.score,           
            'url': post.url,               
            'num_comments': post.num_comments,  
            'upvote_ratio': post.upvote_ratio,  
            'is_nsfw': post.over_18,       
            'created_utc': post.created_utc             # creation time of the post in UTC
        }
        
        collected_posts.append(post_data)               # add post data to the list
    
    return collected_posts

def save_to_json(posts, filename):                      # save collected posts to a json file
    with open(filename, 'w') as file:
        json.dump(posts, file, indent=4)                # write the posts to the file in json format


if __name__ == "__main__":
    subreddit_name = "ucr"  
    num_posts = 10                                      # number of posts to collect
    
    posts = collect_posts(subreddit_name, num_posts)    # collect posts from the subreddit
    save_to_json(posts, "reddit_posts.json")            # save collected posts to a JSON file