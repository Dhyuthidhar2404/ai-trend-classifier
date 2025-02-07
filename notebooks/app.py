import requests
import json
import praw
import tweepy
import time
import streamlit as st
from langdetect import detect

# Access secrets using st.secrets (This is the KEY change)
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

# Fetch trending Reddit posts with links
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

# Fetch trending AI tweets with links
def fetch_twitter_tweets():
    tweets = []
    try:
        client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
        query = "AI OR artificial intelligence -is:retweet lang:en"
        response = client.search_recent_tweets(query=query, max_results=10, tweet_fields=["text", "id"])
        
        if response.data:
            for tweet in response.data:
                if is_english(tweet.text):
                    classification = classify_text(tweet.text)
                    tweet_link = f"https://twitter.com/i/web/status/{tweet.id}"
                    tweets.append({"tweet": tweet.text, "classification": classification, "link": tweet_link})
                time.sleep(1)  # Small delay to avoid hitting rate limits
        return tweets
    except tweepy.TooManyRequests:
        return handle_rate_limit()
    except Exception as e:
        st.error(f"⚠️ Error fetching tweets: {e}")
        return []

# Handle Twitter API Rate Limits
def handle_rate_limit():
    st.warning("⚠️ Twitter rate limit hit! Retrying after 15 minutes...")

    countdown_placeholder = st.empty()
    progress_bar = st.progress(0)

    for remaining in range(900, 0, -1):
        minutes, seconds = divmod(remaining, 60)
        countdown_placeholder.markdown(f"⏳ **Retrying in {minutes} min {seconds} sec...**")
        progress_bar.progress((900 - remaining) / 900)  # Update progress bar
        time.sleep(1)

    countdown_placeholder.empty()
    progress_bar.empty()

    return fetch_twitter_tweets()  # Retry after countdown

# Streamlit UI with Auto-Refresh
def main():
    st.title("AI Trend Classifier 🧠🚀")
    st.write("Fetch and classify trending AI-related posts from Reddit & Twitter!")

    # Toggle for Auto-Refresh
    auto_refresh = st.checkbox("🔄 Auto-refresh every 5 minutes")

    def fetch_and_display():
        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.text("Fetching Reddit posts... 📡")
        reddit_posts = fetch_reddit_posts()
        progress_bar.progress(50)

        status_text.text("Fetching Twitter tweets... 🐦")
        twitter_posts = fetch_twitter_tweets()
        progress_bar.progress(100)

        progress_bar.empty()
        status_text.text("✅ Data fetched successfully!")

        # ✅ **Fix: Remove Twitter Rate Limit Warning if Data is Fetched**
        if twitter_posts:
            st.success("🐦 Twitter data fetched successfully!")

        # Display Reddit results with links
        st.subheader("🔥 Trending Reddit Posts (Machine Learning Subreddit)")
        if reddit_posts:
            for post in reddit_posts:
                with st.expander(f"📌 {post['classification']} Post"):
                    st.write(post["title"])
                    st.markdown(f"[🔗 View Post]({post['link']})", unsafe_allow_html=True)
        else:
            st.write("🚫 No Reddit posts found.")

        # Display Twitter results with links
        st.subheader("🐦 Trending AI Tweets")
        if twitter_posts:
            for tweet in twitter_posts:
                with st.expander(f"📢 {tweet['classification']} Tweet"):
                    st.write(tweet["tweet"])
                    st.markdown(f"[🔗 View Tweet]({tweet['link']})", unsafe_allow_html=True)
        else:
            st.warning("🚫 No Twitter posts found.")

    if st.button("Fetch and Classify Reddit & Twitter Trends"):
        fetch_and_display()

    # Auto-refresh logic
    if auto_refresh:
        while True:
            fetch_and_display()
            time.sleep(300)  # Refresh every 5 minutes

if __name__ == "__main__":
    main()
