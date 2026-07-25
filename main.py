import os
import time
from dotenv import load_dotenv

load_dotenv(override=True)
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1" 

from storage.parquet_manager import ParquetManager
from scraper.review_scraper import ReviewScraper
from analyzer.sentiment import SentimentAnalyzer
from responder.ai_responder import AIResponder
from notifications.email_alerter import EmailAlerter

def process_reviews():
    print("🚀 Starting the Social Review Guardian Pipeline...")
    
    # Initialize all modules
    pm = ParquetManager()
    scraper = ReviewScraper()
    analyzer = SentimentAnalyzer()
    responder = AIResponder()
    alerter = EmailAlerter()
    
    print("🔍 Fetching new reviews using Selenium...")
    new_reviews = scraper.get_new_reviews()
    
    if not new_reviews:
        print("✅ No new reviews found.")
        return

    processed_list = []
    
    for review in new_reviews:
        print(f"\n📝 Processing review ID: {review['id']}")
        
        # 1. Analyze Sentiment
        try:
            analysis = analyzer.analyze_review(review['text'])
            review['sentiment'] = analysis.get('sentiment', 'NEUTRAL')
            review['score'] = analysis.get('score', 0.0)
            review['escalated'] = analysis.get('escalated', False)
        except Exception as e:
            print(f"--> [ERROR] Sentiment analysis failed: {e}")
            continue
        
        # 2. Generate AI Response
        if review['sentiment'] in ["NEGATIVE", "POSITIVE"]:
            print(f"🤖 Drafting AI response for {review['sentiment']} review...")
            reply = responder.generate_reply(review['text'], review['sentiment'], review.get('author', ''))
            review['response'] = reply
        else:
            review['response'] = ""
        # 3. Save as PENDING (Dashboard will handle emails)
        review['status'] = "PENDING"
        if review['escalated']:
            print("🚨 Review escalated! Marking as PENDING for human review on Dashboard.")
        
        print(f"✅ Result: {review['sentiment']} | Score: {review['score']} | Escalated: {review['escalated']}")
        processed_list.append(review)
        
        # Add a delay between each review so we don't spam the API and get blocked
        print("⏳ Waiting 3 seconds before processing the next review...")
        time.sleep(3)
        
    # 4. Save everything to Parquet in one batch
    if processed_list:
        pm.append_batch(processed_list)
        print(f"\n💾 Pipeline execution complete! {len(processed_list)} records saved to data/reviews.parquet")

if __name__ == "__main__":
    process_reviews()