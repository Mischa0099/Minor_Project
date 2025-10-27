# ------------------------------------------------------------
# Sentiment Analysis for Healthcare Chatbot
# Model: cardiffnlp/twitter-roberta-base-sentiment-latest
# Author: Mahak Lodha
# ------------------------------------------------------------

import warnings
warnings.filterwarnings("ignore")

from transformers import pipeline
import torch
import logging

# Suppress model logs
logging.getLogger("transformers").setLevel(logging.ERROR)

# Load model once (for speed)
print("Loading Sentiment Model... Please wait.\n")
model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
device = 0 if torch.cuda.is_available() else -1  # GPU if available
sentiment_pipeline = pipeline("sentiment-analysis", model=model_name, device=device)
print("✅ Model loaded successfully!\n")

def analyze_sentiment(text):
    """
    Analyzes the sentiment of the input text and prints clean output.
    """
    result = sentiment_pipeline(text)[0]
    label = result['label'].capitalize()
    score = round(result['score'] * 100, 2)
    print(f"🧠 Input Text: {text}")
    print(f"💬 Sentiment: {label} ({score}% confidence)")

# ------------------------------------------------------------
# Interactive Loop
# ------------------------------------------------------------
if __name__ == "__main__":
    print("=== Sentiment Analysis using Twitter RoBERTa Model ===")
    print("Type 'exit' to stop.\n")

    while True:
        user_input = input("Enter text: ")
        if user_input.lower() == 'exit':
            print("👋 Exiting sentiment analysis. Have a great day!")
            break
        analyze_sentiment(user_input)
