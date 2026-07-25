# storage/parquet_manager.py
import polars as pl
from pathlib import Path
import os

class ParquetManager:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.file_path = self.data_dir / "reviews.parquet"

    def get_reviews_table(self):
        """Load existing reviews or create empty. Handles corrupted files."""
        if self.file_path.exists():
            try:
                # Check if file has size (handles 0-byte files)
                if os.path.getsize(self.file_path) > 0:
                    return pl.read_parquet(self.file_path)
            except Exception as e:
                print(f"--> [WARNING] Parquet file appears corrupted, starting fresh. {e}")
                # Optional: back up or delete corrupted file
        
        return pl.DataFrame(schema={
            "id": pl.Utf8, 
            "platform": pl.Utf8, 
            "author": pl.Utf8,
            "text": pl.Utf8, 
            "timestamp": pl.Datetime, 
            "url": pl.Utf8,
            "sentiment": pl.Utf8, 
            "score": pl.Float64, 
            "response": pl.Utf8,
            "escalated": pl.Boolean,
            "status": pl.Utf8
        })

    def append_batch(self, reviews_list: list):
        """Append a list of reviews at once to reviews.parquet"""
        if not reviews_list:
            return
            
        new_df = pl.DataFrame(reviews_list)
        
        # Re-use get_reviews_table to handle corruption logic
        existing = self.get_reviews_table()
        
        if not existing.is_empty():
            # Use 'diagonal' to handle potential schema mismatches gracefully
            updated = pl.concat([existing, new_df], how="diagonal")
        else:
            updated = new_df
            
        updated.write_parquet(self.file_path)
        print(f"--> Saved {len(reviews_list)} reviews to {self.file_path}")

    def append_review(self, review_data: dict):
        """Atomic append to reviews.parquet"""
        self.append_batch([review_data])

    def update_review_status(self, review_id: str, new_status: str, edited_response: str = None):
        """Finds a review by ID, updates its status and optionally its response, and rewrites the file"""
        if not self.file_path.exists():
            print(f"--> [ERROR] Cannot update review {review_id}. Parquet file does not exist.")
            return False

        df = self.get_reviews_table()
        
        # Check if ID exists
        if review_id not in df['id'].to_list():
            print(f"--> [ERROR] Review {review_id} not found in Parquet.")
            return False

        # Apply updates using Polars expressions
        if edited_response is not None:
            updated_df = df.with_columns(
                pl.when(pl.col("id") == review_id)
                .then(pl.lit(new_status))
                .otherwise(pl.col("status"))
                .alias("status"),
                pl.when(pl.col("id") == review_id)
                .then(pl.lit(edited_response))
                .otherwise(pl.col("response"))
                .alias("response")
            )
        else:
            updated_df = df.with_columns(
                pl.when(pl.col("id") == review_id)
                .then(pl.lit(new_status))
                .otherwise(pl.col("status"))
                .alias("status")
            )

        updated_df.write_parquet(self.file_path)
        print(f"--> Successfully updated review {review_id} to status '{new_status}'.")
        return True