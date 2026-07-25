import sys
import os
import unittest
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

class TestSocialReviewGuardian(unittest.TestCase):
    def test_analyzer(self):
        from analyzer.sentiment import SentimentAnalyzer
        analyzer = SentimentAnalyzer()
        res = analyzer.analyze_review("This is a fantastic product!")
        self.assertEqual(res['sentiment'], 'POSITIVE')
        
    def test_responder(self):
        from responder.ai_responder import AIResponder
        responder = AIResponder()
        # Mock API Key to quickly test fallback if no proper key
        # or test the API directly
        reply = responder.generate_reply("This is a fantastic product!", "POSITIVE", "John")
        self.assertTrue(isinstance(reply, str))
        self.assertTrue(len(reply) > 5)
        
    def test_parquet_manager(self):
        from storage.parquet_manager import ParquetManager
        import uuid
        pm = ParquetManager(data_dir=Path("data"))
        df = pm.get_reviews_table()
        self.assertTrue(df is not None)
        
        # Test inserting and updating
        test_id = f"test_{uuid.uuid4()}"
        dummy_review = {
            "id": test_id,
            "platform": "Test",
            "author": "Tester",
            "text": "This is a test review.",
            "timestamp": __import__("datetime").datetime.now(),
            "url": "http://test.com",
            "sentiment": "NEUTRAL",
            "score": 0.5,
            "response": "",
            "escalated": False,
            "status": "PENDING"
        }
        pm.append_review(dummy_review)
        df2 = pm.get_reviews_table()
        self.assertTrue(test_id in df2['id'].to_list())
        
        # Test update
        pm.update_review_status(test_id, "RESOLVED", "New Response")
        df3 = pm.get_reviews_table()
        updated_row = df3.filter(__import__('polars').col("id") == test_id)
        self.assertEqual(updated_row["status"][0], "RESOLVED")
        self.assertEqual(updated_row["response"][0], "New Response")

if __name__ == '__main__':
    unittest.main()
