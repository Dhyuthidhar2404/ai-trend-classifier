import requests
import json
import praw
import tweepy
import os
import time
import streamlit as st
from dotenv import load_dotenv
from langdetect import detect

# Function to check if the text is in English
def is_english(text):
    try:
        return detect(text) == "en"
    except:
        return False

# Load environment variables
load_dotenv()

# Load API keys
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

# Hugging Face API for text classification
def classify_text(text):
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    
    data = {"inputs": text, "parameters": {"candidate_labels": ["AI-related", "Not AI-related"]}}
    response = requests.post(API_URL, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()["labels"][0]
    return "Unknown"

# Set up Reddit API
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

# Fetch trending Reddit posts
def fetch_reddit_posts():
    posts = []
    try:
        subreddit = reddit.subreddit("MachineLearning")
        for post in subreddit.hot(limit=5):
            classification = classify_text(post.title)
            posts.append({"title": post.title, "classification": classification})
        return posts
    except Exception as e:
        st.error(f"⚠️ Error fetching Reddit posts: {e}")
        return []

# Fetch trending AI tweets
def fetch_twitter_tweets():
    tweets = []
    try:
        client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
        query = "AI OR artificial intelligence -is:retweet lang:en"
        response = client.search_recent_tweets(query=query, max_results=10, tweet_fields=["text"])
        
        if response.data:
            for tweet in response.data:
                if is_english(tweet.text):
                    classification = classify_text(tweet.text)
                    tweets.append({"tweet": tweet.text, "classification": classification})
                time.sleep(1)  # Small delay to avoid hitting rate limits
        return tweets
    except tweepy.TooManyRequests:
        st.warning("⚠️ Twitter rate limit hit! Retrying after 15 minutes...")
        time.sleep(900)  # Wait 15 minutes before retrying
        return fetch_twitter_tweets()
    except Exception as e:
        st.error(f"⚠️ Error fetching tweets: {e}")
        return []

# Streamlit UI
def main():
    st.title("AI Trend Classifier 🧠🚀")
    st.write("Fetch and classify trending AI-related posts from Reddit & Twitter!")
    
    if st.button("Fetch and Classify Reddit & Twitter Trends"):
        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.text("Fetching Reddit posts...")
        reddit_posts = fetch_reddit_posts()
        progress_bar.progress(50)

        status_text.text("Fetching Twitter tweets...")
        twitter_posts = fetch_twitter_tweets()
        progress_bar.progress(100)

        progress_bar.empty()
        status_text.text("✅ Data fetched successfully!")
        
        # Display Reddit results
        st.subheader("Trending Reddit Posts (Machine Learning Subreddit)")
        if reddit_posts:
            for post in reddit_posts:
                st.write(f"**{post['title']}** → {post['classification']}")
        else:
            st.write("No Reddit posts found.")
        
        # Display Twitter results
        st.subheader("Trending AI Tweets")
        if twitter_posts:
            for tweet in twitter_posts:
                st.write(f"**{tweet['tweet']}** → {tweet['classification']}")
        else:
            st.write("No Twitter posts found.")

if __name__ == "__main__":
    main()
