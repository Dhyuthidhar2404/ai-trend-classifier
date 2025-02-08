# 🧠 AI Trend Classifier
Classifies trending AI-related posts from Reddit & Twitter using NLP models.
🔗 Live Website: [AI Trend Classifier](https://ai-classifier-sss.streamlit.app/)

📌 Features
✅ Fetches trending posts from Reddit & Twitter
✅ Uses Hugging Face NLP Model to classify posts as AI-related or Not AI-related
✅ Rate-limit handling for Twitter API
✅ Streamlit UI for easy interaction

🛠️ Setup Instructions
🔹 1. Clone the Repository

git clone https://github.com/Dhyuthidhar2404/ai-trend-classifier.git
cd ai-trend-classifier
🔹 2. Create & Activate Virtual Environment

python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
🔹 3. Install Dependencies

pip install -r requirements.txt

🔹 4. Configure Secrets for API Access
Create a .streamlit/secrets.toml file for Streamlit deployment:

toml

HUGGINGFACE_API_KEY = "your_huggingface_api_key"
TWITTER_BEARER_TOKEN = "your_twitter_api_key"
REDDIT_CLIENT_ID = "your_reddit_client_id"
REDDIT_CLIENT_SECRET = "your_reddit_client_secret"
REDDIT_USER_AGENT = "your_reddit_user_agent"
Note: For GitHub, do NOT commit secrets! Use GitHub Actions secrets instead.

🚀 Running the App Locally

streamlit run app.py
🔗 Deployment on Streamlit Cloud
1️⃣ Push the code to GitHub
2️⃣ Go to Streamlit Cloud and deploy
3️⃣ Add API keys in Secrets under Settings > Secrets
4️⃣ Visit AI Trend Classifier 🎉

📜 License
This project is licensed under the MIT License.
