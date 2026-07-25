# responder/ai_responder.py
import os
import time
from openai import OpenAI

class AIResponder:
    def __init__(self):
        print("Loading OpenRouter AI Responder...")
        
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            print("--> [WARNING] OPENROUTER_API_KEY not found in .env. Responses will fail or fallback.")
        
        # OpenRouter uses the standard OpenAI SDK, just point it to their base URL
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key or "placeholder", # Prevents SDK crash on init if missing
        )
        
        # OpenRouter free model - widely available and reliable
        self.model = "nvidia/nemotron-3-super-120b-a12b:free"

    def generate_reply(self, review_text: str, sentiment: str, customer_name: str = "") -> str:
        """
        Drafts a professional, concise response for positive and negative reviews using OpenRouter, addressing the customer by name.
        """
        if sentiment not in ["POSITIVE", "NEGATIVE"]:
            return ""
            
        if not self.api_key:
            if sentiment == "NEGATIVE":
                return "We sincerely apologize for your experience. Our support team will look into this immediately."
            else:
                return "Thank you for the wonderful feedback! We highly appreciate your support."

        contact_email = os.getenv("SUPPORT_EMAIL", "support@example.com")
        contact_phone = os.getenv("SUPPORT_PHONE", "1-800-123-4567")
        contact_instruction = f" If resolving the issue, ask them to contact {contact_email} or {contact_phone}."

        name_instruction = f" Address the customer as {customer_name} if possible." if customer_name else ""

        if sentiment == "NEGATIVE":
            prompt = (
                f"Draft a very concise, polite, and professional customer service response apologizing "
                f"and offering to resolve this issue.{contact_instruction}{name_instruction} Keep it strictly to 1 or 2 sentences max: '{review_text}'"
            )
        else:
            prompt = (
                f"Draft a very concise, polite, and professional customer service response thanking "
                f"the customer for their positive feedback.{name_instruction} Keep it strictly to 1 or 2 sentences max: '{review_text}'"
            )
        
        max_retries = 3
        # Exponential backoff parameters
        initial_delay = 2
        
        for attempt in range(max_retries):
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": f"You are a professional customer service representative. Keep replies brief, polite, and helpful.\n\nTask: {prompt}"}
                    ]
                )
                return completion.choices[0].message.content.strip()
                
            except Exception as e:
                print(f"--> [WARNING] OpenRouter API attempt {attempt + 1} failed: {e}")
                
                # Check if it's a rate limit error (429)
                is_rate_limit = "429" in str(e) or "Too Many Requests" in str(e) or "rate limit" in str(e).lower()
                
                if attempt < max_retries - 1:
                    # Exponential backoff
                    delay = initial_delay * (2 ** attempt)
                    if is_rate_limit:
                        print(f"--> [INFO] Rate limit hit. Waiting {delay} seconds before retrying...")
                    else:
                        print(f"--> [INFO] Waiting {delay} seconds before retrying...")
                    time.sleep(delay)
                else:
                    print("--> [ERROR] All OpenRouter API retries failed.")
                    if sentiment=="NEGATIVE":
                        return "We sincerely apologize for your experience. Please contact our support team immediately so we can help."
                    else:
                        return "Thank you for the wonderful feedback! We highly appreciate your support."

        return "We sincerely apologize for your experience. Please contact our support team immediately so we can help."