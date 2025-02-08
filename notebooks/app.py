import requests
import json
import praw
import tweepy
import time
import streamlit as st
from langdetect import detect
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

def get_next_reset_date():
    """Returns the next Twitter API reset date dynamically (5th of next month at 00:00 UTC)."""
    now = datetime.now(timezone.utc)
    
    if now.day >= 5:
        next_reset = now + relativedelta(months=1)
    else:
        next_reset = now

    next_reset = next_reset.replace(day=5, hour=0, minute=0, second=0)
    return next_reset.strftime("%Y-%m-%d %H:%M:%S UTC")

# Access secrets using st.secrets
HUGGINGFACE_API_KEY = st.secrets["HUGGINGFACE_API_KEY"]
TWITTER_BEARER_TOKEN = st.secrets["TWITTER_BEARER_TOKEN"]
REDDIT_CLIENT_ID = st.secrets["REDDIT_CLIENT_ID"]
REDDIT_CLIENT_SECRET = st.secrets["REDDIT_CLIENT_SECRET"]
REDDIT_USER_AGENT = st.secrets["REDDIT_USER_AGENT"]

# Function to check if text is in English
def is_english(text):
    try:
        return detect(text) == "en"
    except:
        return False

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
            post_link = f"https://www.reddit.com{post.permalink}"
            posts.append({"title": post.title, "classification": classification, "link": post_link})
        return posts
    except Exception as e:
        st.error(f"⚠️ Error fetching Reddit posts: {e}")
        return []

# Fetch AI-related tweets
def fetch_twitter_tweets():
    tweets = []
    reset_date = get_next_reset_date()

    try:
        client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
        query = "AI OR artificial intelligence -is:retweet lang:en"

        # Convert reset_date string to datetime
        reset_datetime = datetime.strptime(reset_date, "%Y-%m-%d %H:%M:%S UTC").replace(tzinfo=timezone.utc)

        if datetime.now(timezone.utc) < reset_datetime:
            st.warning(f"🚫 Twitter API limit reached! Try again after **{reset_date}**.")
            return []

        response = client.search_recent_tweets(query=query, max_results=10, tweet_fields=["text", "id"])

        if response.data:
            for tweet in response.data:
                if is_english(tweet.text):
                    classification = classify_text(tweet.text)
                    tweet_link = f"https://twitter.com/i/web/status/{tweet.id}"
                    tweets.append({"tweet": tweet.text, "classification": classification, "link": tweet_link})

        return tweets

    except tweepy.TooManyRequests:
        st.warning(f"🚫 Twitter API limit reached! Try again later.")
        return []
    except Exception as e:
        st.error(f"⚠️ Error fetching tweets: {e}")
        return []

# Function to display posts in Streamlit
def display_posts(posts, platform):
    if not posts:
        st.warning(f"⚠️ No {platform} posts found.")
        return

    st.subheader(f"📌 {platform} Trends")

    for post in posts:
        with st.expander(f"📢 {post['classification']} {platform} Post"):
            st.write(f"**{post['title'] if 'title' in post else post['tweet']}**")
            st.markdown(f"[🔗 View Post]({post['link']})", unsafe_allow_html=True)

# Streamlit UI
def main():
    st.title("AI Trend Classifier 🧠🚀")
    st.write("Fetch and classify trending AI-related posts from Reddit & Twitter!")

    reset_date = get_next_reset_date()

    # Fetch Reddit
    if st.button("Fetch Reddit Trends 🔥"):
        reddit_posts = fetch_reddit_posts()
        display_posts(reddit_posts, "Reddit")

    # Fetch Twitter (Check API limit before allowing request)
    reset_datetime = datetime.strptime(reset_date, "%Y-%m-%d %H:%M:%S UTC").replace(tzinfo=timezone.utc)

    if datetime.now(timezone.utc) < reset_datetime:
        st.warning(f"🚫 Twitter API limit reached! Try again after **{reset_date}**.")
    else:
        if st.button("Fetch Twitter Trends 🐦"):
            twitter_posts = fetch_twitter_tweets()
            display_posts(twitter_posts, "Twitter")

if __name__ == "__main__":
    main()
