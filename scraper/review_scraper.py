# scraper/review_scraper.py
import uuid
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


class ReviewScraper:
    def __init__(self, target_url="https://www.trustpilot.com/review/myiq.com", max_reviews=12):
        self.target_url = target_url
        self.max_reviews = max_reviews
        self.options = Options()
        
        # --- BROWSER CONFIGURATION ---
        # self.options.add_argument("--headless")  # Uncomment for server/background mode
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--window-size=1920,1080")
        self.options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        # Disable images to speed up loading
        prefs = {"profile.managed_default_content_settings.images": 2}
        self.options.add_experimental_option("prefs", prefs)

    def _scroll_to_bottom(self, driver):
        """Scroll to the bottom of the page to trigger lazy loading."""
        last_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        return new_height > last_height

    def _extract_card_v1(self, element):
        """Extract using 'data-service-review-card-paper' attribute (common Trustpilot pattern)."""
        try:
            # Wait for the review text to be present within this card
            text_el = element.find_element(
                By.XPATH,
                ".//*[@data-service-review-text-typography='true']"
            )
            text = text_el.text.strip()
            if not text:
                return None

            author = ""
            try:
                author_el = element.find_element(
                    By.XPATH,
                    ".//*[@data-consumer-name-typography='true']"
                )
                author = author_el.text.strip()
            except NoSuchElementException:
                # Try fallback: look for name in heading or link elements
                try:
                    author_el = element.find_element(
                        By.XPATH,
                        ".//*[self::h2 or self::h3 or self::a][@class and contains(@class, 'consumer')]"
                    )
                    author = author_el.text.strip()
                except NoSuchElementException:
                    author = "Anonymous"

            return {
                "id": f"rev_{str(uuid.uuid4())[:8]}",
                "platform": "Trustpilot",
                "author": author,
                "text": text,
                "timestamp": datetime.now(),
                "url": self.target_url,
                "sentiment": "PENDING",
                "score": 0.0,
                "response": "",
                "escalated": False,
            }
        except NoSuchElementException:
            return None

    def _extract_card_v2(self, element):
        """Extract using 'data-service-review-card-v2' testid attribute."""
        try:
            text_el = element.find_element(
                By.XPATH,
                ".//*[@data-service-review-text-typography='true']"
            )
            text = text_el.text.strip()
            if not text:
                return None

            author = ""
            try:
                author_el = element.find_element(
                    By.XPATH,
                    ".//*[@data-consumer-name-typography='true']"
                )
                author = author_el.text.strip()
            except NoSuchElementException:
                author = "Anonymous"

            return {
                "id": f"rev_{str(uuid.uuid4())[:8]}",
                "platform": "Trustpilot",
                "author": author,
                "text": text,
                "timestamp": datetime.now(),
                "url": self.target_url,
                "sentiment": "PENDING",
                "score": 0.0,
                "response": "",
                "escalated": False,
            }
        except NoSuchElementException:
            return None

    def _extract_card_v3(self, element):
        """
        Fallback: use broad structural selectors.
        Looks for paragraphs with review-like content within the card.
        """
        try:
            # Find any paragraph element with substantial text
            paragraphs = element.find_elements(By.XPATH, ".//p")
            for p in paragraphs:
                txt = p.text.strip()
                if len(txt) > 10:  # Must have meaningful content
                    author = "Anonymous"
                    try:
                        # Try to find a name in headings or links
                        name_el = element.find_element(
                            By.XPATH,
                            ".//*[self::h2 or self::h3 or self::a or self::span][string-length(text()) > 0]"
                        )
                        name_text = name_el.text.strip()
                        if name_text and len(name_text) < 100 and name_text != txt:
                            author = name_text
                    except NoSuchElementException:
                        pass

                    return {
                        "id": f"rev_{str(uuid.uuid4())[:8]}",
                        "platform": "Trustpilot",
                        "author": author,
                        "text": txt,
                        "timestamp": datetime.now(),
                        "url": self.target_url,
                        "sentiment": "PENDING",
                        "score": 0.0,
                        "response": "",
                        "escalated": False,
                    }
        except NoSuchElementException:
            pass
        return None

    def _try_extract(self, element):
        """Try extraction strategies in order, return first match."""
        for extractor in [self._extract_card_v1, self._extract_card_v2, self._extract_card_v3]:
            result = extractor(element)
            if result is not None:
                return result
        return None

    def get_new_reviews(self):
        """
        Main method to scrape reviews using Selenium.
        Uses multiple XPath strategies to handle Trustpilot DOM changes.
        """
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self.options
        )
        reviews_data = []
        seen_texts = set()  # Deduplication

        try:
            print(f"--> Navigating to {self.target_url}...")
            driver.get(self.target_url)

            # Wait for the page to load - look for any known review card indicator
            wait = WebDriverWait(driver, 15)

            # Strategy 1: Wait for data-service-review-card-paper
            try:
                wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//*[@data-service-review-card-paper]")
                    )
                )
                card_xpath = "//*[@data-service-review-card-paper]"
                print("--> Using selector: data-service-review-card-paper")
            except TimeoutException:
                # Strategy 2: Fallback to data-testid
                try:
                    wait.until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//*[@data-testid='service-review-card-v2']")
                        )
                    )
                    card_xpath = "//*[@data-testid='service-review-card-v2']"
                    print("--> Using selector: data-testid='service-review-card-v2'")
                except TimeoutException:
                    # Strategy 3: Try class-based selectors
                    try:
                        wait.until(
                            EC.presence_of_element_located(
                                (By.XPATH, "//div[contains(@class, 'reviewCard')]")
                            )
                        )
                        card_xpath = "//div[contains(@class, 'reviewCard')]"
                        print("--> Using selector: class~reviewCard")
                    except TimeoutException:
                        print("--> [ERROR] No review cards found on the page.")
                        return reviews_data

            # Scroll to load lazy reviews
            print("--> Scrolling to load all reviews...")
            for scroll_attempt in range(5):
                if not self._scroll_to_bottom(driver):
                    break
                print(f"    Scrolled {scroll_attempt + 1}/5")

            # Find all review card elements
            review_elements = driver.find_elements(By.XPATH, card_xpath)
            print(f"--> Found {len(review_elements)} review elements")

            for idx, element in enumerate(review_elements):
                # Stop if we've collected enough reviews
                if len(reviews_data) >= self.max_reviews:
                    print(f"--> Reached limit of {self.max_reviews} reviews. Stopping extraction.")
                    break

                # Visual feedback: highlight the card
                try:
                    driver.execute_script(
                        "arguments[0].style.border = '2px solid red';",
                        element
                    )
                    driver.execute_script(
                        "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                        element
                    )
                except Exception:
                    pass  # Non-critical

                time.sleep(0.3)

                review = self._try_extract(element)
                if review is None:
                    print(f"    [SKIP] Element {idx + 1}: Could not extract review data")
                    continue

                # Deduplicate by text content
                text_key = review["text"][:80]
                if text_key in seen_texts:
                    print(f"    [SKIP] Element {idx + 1}: Duplicate review")
                    continue
                seen_texts.add(text_key)

                print(f"    [{len(reviews_data) + 1}/{self.max_reviews}] Author: {review['author'][:30]:<30} | Text: {review['text'][:50]}...")
                reviews_data.append(review)

        except Exception as e:
            print(f"--> [ERROR] Selenium scraping failed: {e}")

        finally:
            time.sleep(2)
            print(f"--> Closing Browser... ({len(reviews_data)} reviews collected)")
            driver.quit()

        return reviews_data


if __name__ == "__main__":
    # Test block - scrape only 5 for quick testing
    scraper = ReviewScraper(max_reviews=5)
    reviews = scraper.get_new_reviews()
    print(f"\nTotal reviews collected: {len(reviews)}")
    for r in reviews:
        print(f"Found Review: {r['author']} -> {r['text'][:60]}...")
