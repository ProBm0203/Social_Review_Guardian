# test_email.py
from notifications.email_alerter import EmailAlerter
import os
from dotenv import load_dotenv

load_dotenv(override=True)

def test_gmail():
    alerter = EmailAlerter()
    
    # Mock review data
    test_review = {
        "id": "TEST_001",
        "author": "Test User",
        "platform": "Google",
        "score": "0.1 (Negative)",
        "text": "The service was terrible and I am very unhappy.",
        "response": "We are very sorry for your experience. Please contact us at support@example.com",
        "url": "https://example.com/reviews/1"
    }
    
    recipient = os.getenv("RECIPIENT_EMAIL")
    if not recipient:
        print("RECIPIENT_EMAIL not found in .env. Using fallback.")
        recipient = "bhaskarmishra12675@outlook.com" # From the .env I saw earlier
    
    print(f"Attempting to send test email to {recipient}...")
    alerter.send_escalation_alert(test_review, recipient)

if __name__ == "__main__":
    test_gmail()
