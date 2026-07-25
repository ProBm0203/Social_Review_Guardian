# analyzer/sentiment.py
from transformers import pipeline

class SentimentAnalyzer:
    def __init__(self):
        print("Loading local AI sentiment model (this takes a moment)...")
        # Explicitly declare the model to remove the warning
        self.analyzer = pipeline(
            "sentiment-analysis", 
            model="distilbert/distilbert-base-uncased-finetuned-sst-2-english"
        )

    def analyze_review(self, text: str) -> dict:
        """
        Analyzes the text and returns a dictionary with the sentiment metrics.
        """
        # If the review is empty, return a default state
        if not text or not text.strip():
            return {"sentiment": "NEUTRAL", "score": 0.0, "escalated": False}

        try:
            # The pipeline returns a list containing a dictionary, e.g.:
            # [{'label': 'POSITIVE', 'score': 0.9998}]
            result = self.analyzer(text)[0]
            
            sentiment_label = result['label'].upper()
            score = round(result['score'], 4)
            
            # Business Logic: Escalate if it is highly negative 
            escalated = True if sentiment_label == 'NEGATIVE' and score > 0.8 else False
            
            return {
                "sentiment": sentiment_label,
                "score": score,
                "escalated": escalated
            }
            
        except Exception as e:
            print(f"Error analyzing text: {e}")
            return {"sentiment": "ERROR", "score": 0.0, "escalated": False}