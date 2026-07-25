# notifications/email_alerter.py
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from dotenv import load_dotenv

# Use absolute path to root .env
root_path = Path(__file__).resolve().parent.parent
load_dotenv(root_path / ".env", override=True)

class EmailAlerter:
    def __init__(self):
        """
        Initializes the Gmail SMTP client using credentials from .env.
        """
        self.gmail_user = os.getenv("GMAIL_USER") or ""
        self.gmail_password = os.getenv("GMAIL_APP_PASSWORD") or ""
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 465  # SSL

    def send_escalation_alert(self, review_data: dict, recipient_email: str):
        """
        Sends an active email alert using Gmail SMTP.
        """
        if not self.gmail_user or not self.gmail_password:
            print("--> Gmail credentials not found in .env. Please configure GMAIL_USER and GMAIL_APP_PASSWORD.")
            return

        if not recipient_email:
            print("--> Recipient email not provided.")
            return

        print(f"--> Sending Gmail alert to {recipient_email}...")
        
        # Build the email content
        subject = f"🚨 URGENT: Escalated Negative Review Detected ({review_data.get('platform', 'Unknown')})"
        body = (
            f"A highly negative review requires immediate attention.\n\n"
            f"Review ID: {review_data.get('id')}\n"
            f"Author: {review_data.get('author')}\n"
            f"Sentiment Score: {review_data.get('score')}\n\n"
            f"Review Text:\n'{review_data.get('text')}'\n\n"
            f"AI Drafted Response:\n'{review_data.get('response')}'\n\n"
            f"Link: {review_data.get('url')}"
        )

        msg = MIMEMultipart()
        msg['From'] = self.gmail_user
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            # Connect to Gmail SMTP server using SSL
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.gmail_user, self.gmail_password)
                server.send_message(msg)
            
            print("--> Gmail alert sent successfully!")
            
        except Exception as e:
            print(f"--> Failed to send via Gmail: {e}")
            if "535" in str(e):
                print(f"--> [DEBUG] Attempted login with user: '{self.gmail_user}'")
                print(f"--> [DEBUG] Password length: {len(self.gmail_password)}")
            print("--> TROUBLESHOOTING: Ensure you are using a Gmail App Password, not your account password.")

    def send_response_email(self, recipient_email: str, author_name: str, response_text: str):
        """
        Sends the final AI or human-modified response to the customer via email.
        """
        if not self.gmail_user or not self.gmail_password:
            error_msg = "Gmail credentials (GMAIL_USER / GMAIL_APP_PASSWORD) are missing in .env"
            print(f"--> [ERROR] {error_msg}")
            raise ValueError(error_msg)

        if not recipient_email:
            print("--> Recipient email not provided.")
            return False
            
        print(f"--> Sending response email to {recipient_email}...")
        
        subject = "Response to Your Recent Review"
        body = response_text
        
        msg = MIMEMultipart()
        msg['From'] = self.gmail_user
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.gmail_user, self.gmail_password)
                server.send_message(msg)
            print("--> Response email sent successfully!")
            return True
        except Exception as e:
            print(f"--> Failed to send via Gmail: {e}")
            raise e
