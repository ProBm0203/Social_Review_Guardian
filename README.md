# 🛡️ Social Review Guardian

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-API-orange.svg)](https://openrouter.ai/)
[![Hugging Face](https://img.shields.io/badge/🤗-Transformers-FFD21E.svg)](https://huggingface.co/)

An **enterprise-grade, end-to-end pipeline** for automatically monitoring, analyzing, responding to, and managing online business reviews. The system scrapes reviews from platforms like **Trustpilot**, performs **local AI sentiment analysis** using Hugging Face Transformers, drafts **intelligent responses** via the OpenRouter API, stores everything in efficient **Parquet format**, and provides a **C-Level Executive Dashboard** built with Streamlit and Plotly for strategic reputation management.

---

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Running the Full Pipeline](#1-running-the-full-pipeline)
  - [Launching the Executive Dashboard](#2-launching-the-executive-dashboard)
  - [Running Tests](#3-running-tests)
- [Module Deep Dive](#module-deep-dive)
  - [1. Scraper (`scraper/`)](#1-scraper-scraperreview_scraperpy)
  - [2. Analyzer (`analyzer/`)](#2-analyzer-analyzersentimentpy)
  - [3. Responder (`responder/`)](#3-responder-responderai_responderpy)
  - [4. Storage (`storage/`)](#4-storage-storageparquet_managerpy)
  - [5. Notifications (`notifications/`)](#5-notifications-notificationsemail_alerterpy)
  - [6. Dashboard (`dashboard/`)](#6-dashboard-dashboardapppy)
  - [7. Pipeline Orchestrator (`main.py`)](#7-pipeline-orchestrator-mainpy)
- [Dashboard Tabs Explained](#dashboard-tabs-explained)
- [Jargon Buster / Glossary](#jargon-buster--glossary)
- [Environment Variables Reference](#environment-variables-reference)
- [Contributing](#contributing)
- [License](#license)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SOCIAL REVIEW GUARDIAN                          │
│                                                                         │
│   ┌──────────┐    ┌───────────┐    ┌──────────┐    ┌───────────────┐   │
│   │ Scraper  │───▶│  Sentiment│───▶│   AI     │───▶│   Parquet     │   │
│   │(Selenium)│    │  Analyzer │    │Responder │    │   Storage     │   │
│   │          │    │ (Hugging  │    │(OpenRouter│    │   (Polars)    │   │
│   │Trustpilot│    │   Face)   │    │   API)   │    │               │   │
│   └──────────┘    └───────────┘    └──────────┘    └───────┬───────┘   │
│                                                            │           │
│                      ┌────────────────────────────────────┘           │
│                      ▼                                                  │
│   ┌───────────────────────────────────────────────┐                    │
│   │           Streamlit Executive Dashboard        │                    │
│   │  ┌──────────┐ ┌──────────┐ ┌──────────────┐  │                    │
│   │  │ Alert    │ │Reputation│ │  Business    │  │                    │
│   │  │ Center   │ │ Trends   │ │  Impact      │  │                    │
│   │  └──────────┘ └──────────┘ └──────────────┘  │                    │
│   │              ┌──────────────┐                 │                    │
│   │              │ Operations   │                 │                    │
│   │              └──────────────┘                 │                    │
│   └───────────────────────────────────────────────┘                    │
│                            │                                            │
│                            ▼                                            │
│   ┌───────────────────────────────────────────────┐                    │
│   │         Email Notification (Gmail SMTP)        │                    │
│   │   Sends escalation alerts & response emails    │                    │
│   └───────────────────────────────────────────────┘                    │
└─────────────────────────────────────────────────────────────────────────┘
```

**Data Flow:**
1. **Scraper** extracts new reviews from Trustpilot using Selenium WebDriver
2. **Sentiment Analyzer** classifies each review (POSITIVE/NEGATIVE) using a local Hugging Face model
3. **AI Responder** drafts professional customer service replies via OpenRouter API
4. **Escalation Engine** flags highly negative reviews (score > 0.8) for immediate human attention
5. **Parquet Manager** persists all data locally in columnar Apache Parquet format
6. **Executive Dashboard** provides real-time visualization, alert management, and business analytics
7. **Email Alerter** sends escalation notifications and dispatches final responses to customers

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Automated Scraping** | Selenium-based web scraper targeting Trustpilot reviews with smart element detection |
| **Local Sentiment Analysis** | Runs entirely offline using Hugging Face's `distilbert-base-uncased-finetuned-sst-2-english` — no API costs |
| **AI Response Generation** | Generates context-aware professional replies via OpenRouter API (free tier available) |
| **Smart Escalation** | Automatically flags reviews with NEGATIVE sentiment and confidence score > 0.8 |
| **Parquet Storage** | Columnar storage format using Polars — highly efficient for large datasets |
| **Executive Dashboard** | Full-featured Streamlit dashboard with 4 analytical tabs |
| **Reputation Scoring** | Composite 0-100 score factoring sentiment, response rate, and escalation metrics |
| **Business Impact Analysis** | Revenue-at-risk and customer retention impact modeling |
| **Real-time Alert Center** | Human-in-the-loop review management with AI response editing and email dispatch |
| **Email Notifications** | Gmail SMTP integration for escalation alerts and customer response delivery |
| **Exponential Backoff Retry** | Resilient API calls with automatic retry and rate-limit handling |
| **Corruption-Resistant Storage** | Automatic detection and recovery from corrupted Parquet files |

---

## 📂 Project Structure

```
Social_Review_Guardian/
├── main.py                          # Pipeline orchestrator - entry point
├── requirements.txt                 # Python dependencies
├── test_all.py                      # Unit tests
├── debug_creds.py                   # Credential debug utility
├── .gitignore                       # Git ignore rules
├── .env                             # Environment variables (NOT committed)
├── README.md                        # This file
│
├── scraper/
│   ├── __init__.py
│   └── review_scraper.py           # Selenium Trustpilot scraper
│
├── analyzer/
│   ├── __init__.py
│   └── sentiment.py                # Hugging Face sentiment analysis
│
├── responder/
│   ├── __init__.py
│   └── ai_responder.py             # OpenRouter AI response generator
│
├── storage/
│   ├── __init__.py
│   └── parquet_manager.py          # Polars Parquet CRUD operations
│
├── notifications/
│   ├── __init__.py
│   └── email_alerter.py            # Gmail SMTP email sender
│
├── dashboard/
│   └── app.py                      # Streamlit executive dashboard
│
└── data/
    └── reviews.parquet             # Persistent review storage (gitignored)
```

---

## 🛠️ Technology Stack

| Technology | Purpose | Version |
|------------|---------|---------|
| **Python** | Core programming language | 3.9+ |
| **Selenium** | Web scraping and browser automation | 4.x |
| **webdriver-manager** | Automatic ChromeDriver management | 3.x+ |
| **Hugging Face Transformers** | Local NLP sentiment analysis | 4.x+ |
| **PyTorch** | Deep learning backend for Transformers | 2.x+ |
| **OpenRouter API** | AI text generation (LLM-as-a-service) | v1 |
| **OpenAI Python SDK** | Client for OpenRouter API | 1.x+ |
| **Polars** | High-performance DataFrame library & Parquet I/O | 0.20+ |
| **PyArrow** | Apache Arrow backend for Parquet | 14.x+ |
| **Streamlit** | Interactive web dashboard framework | 1.28+ |
| **Plotly** | Interactive data visualizations | 5.x+ |
| **python-dotenv** | Environment variable management | 1.x+ |
| **BeautifulSoup4** | HTML parsing (scraper utility) | 4.x+ |

---

## 📦 Prerequisites

- **Python 3.9 or higher** installed on your system
- **Google Chrome** browser installed (for Selenium WebDriver)
- **A Gmail account** with an [App Password](https://support.google.com/accounts/answer/185833) configured (for email features)
- **An OpenRouter account** with an API key (free tier available at [openrouter.ai/keys](https://openrouter.ai/keys))
- **pip** (Python package manager)

---

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/ProBm0203/Social_Review_Guardian.git
cd Social_Review_Guardian
```

### 2. Create a Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `selenium` & `beautifulsoup4` — Web scraping
- `transformers` & `torch` — Hugging Face sentiment analysis
- `polars` & `pyarrow` — Parquet data storage
- `streamlit` & `plotly` — Dashboard and visualizations
- `python-dotenv` — Environment variable loading

> **Note:** The first time you run the analyzer, Hugging Face will download the `distilbert-base-uncased-finetuned-sst-2-english` model (~250MB). This is a one-time download.

---

## ⚙️ Configuration

### 1. Create a `.env` File

Create a `.env` file in the project root directory:

```bash
# .env - Social Review Guardian Configuration
# Copy this template and fill in your credentials

# ── OpenRouter AI Configuration ──
# Get your API key from: https://openrouter.ai/keys
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-api-key-here

# ── Gmail SMTP Configuration ──
# Your Gmail address (the sender)
GMAIL_USER=your-email@gmail.com
# Gmail App Password (NOT your regular password)
# Generate one at: https://myaccount.google.com/apppasswords
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx

# ── Support Contact Info (used in AI responses) ──
SUPPORT_EMAIL=support@yourcompany.com
SUPPORT_PHONE=1-800-123-4567
```

### 2. Setting Up Gmail App Password

Google requires an **App Password** instead of your regular password for SMTP access:

1. Go to your [Google Account](https://myaccount.google.com/)
2. Navigate to **Security** → **2-Step Verification** (must be enabled)
3. Scroll to **App passwords** (or search for it)
4. Select **Mail** as the app and **Windows Computer** as the device
5. Click **Generate** — you'll receive a 16-character password
6. Copy this password into your `.env` as `GMAIL_APP_PASSWORD` (spaces optional)

---

## 🚀 Usage

### 1. Running the Full Pipeline

The pipeline orchestrator (`main.py`) executes all stages sequentially:

```bash
python main.py
```

**What happens step-by-step:**

```
🚀 Starting the Social Review Guardian Pipeline...
🔍 Fetching new reviews using Selenium...
    → Navigates to Trustpilot (configurable URL)
    → Identifies review cards via XPath
    → Extracts author name, review text, and metadata
    → Highlights each element with a red border during scraping (visual feedback)

📝 Processing review ID: rev_abc12345
    → Runs Hugging Face sentiment classifier on the review text
    → Returns: label (POSITIVE/NEGATIVE) and confidence score

🤖 Drafting AI response for NEGATIVE review...
    → Sends the review to OpenRouter API (Llama/Step 3.5 Flash model)
    → Generates a concise 1-2 sentence professional reply
    → Includes support contact info and customer name
    → Implements exponential backoff (3 retries) for rate limits

✅ Result: NEGATIVE | Score: 0.9876 | Escalated: True
    → Highly negative reviews (score > 0.8) are flagged as 'escalated'
    → Escalated reviews are marked as 'PENDING' for dashboard review

💾 Pipeline execution complete! 5 records saved to data/reviews.parquet
```

**Status Workflow:**
- **PENDING** — Initial state after scraping; awaiting dashboard review
- **APPROVED** — Human reviewed and approved the AI response
- **RESOLVED** — Final response dispatched to the customer

### 2. Launching the Executive Dashboard


```bash
streamlit run dashboard/app.py
```

Access the dashboard at **http://localhost:8501** in your browser.

**What you'll see:**
- **Executive Header** with system status and alert bar
- **5 Key Metrics** — Reputation Score, Revenue at Risk, Retention Impact, Total Reviews, Escalations
- **4 Tabs:** Alert Center, Reputation Trends, Business Impact, Operations
- **Real-time data** loaded from `data/reviews.parquet`
- **Alert cards** with inline AI response editing and email dispatch

### 3. Running Tests

```bash
python test_all.py
```

Tests cover three areas:
- **`test_analyzer`** — Verifies sentiment classification (e.g., "fantastic" → POSITIVE)
- **`test_responder`** — Confirms AI response generation works (or falls back gracefully)
- **`test_parquet_manager`** — Tests CRUD operations: insert, read, update review status

### 4. Debugging Credentials

If you encounter email authentication issues:

```bash
python debug_creds.py
```

This utility prints your loaded Gmail credentials, their length, and indicates if spaces are present in the password.

---

## 🔍 Module Deep Dive

### 1. Scraper (`scraper/review_scraper.py`)

**Class:** `ReviewScraper`

A Selenium-based web scraper targeting Trustpilot review pages. It uses explicit XPath selectors to identify review cards, scrolls to each element for visual feedback, and extracts structured data.

**Key Methods:**

| Method | Description |
|--------|-------------|
| `get_new_reviews()` | Main scraping entry point. Returns a list of review dicts with fields: `id`, `platform`, `author`, `text`, `timestamp`, `url`, `sentiment`, `score`, `response`, `escalated` |

**Configuration:**
- Default URL: `https://www.trustpilot.com/review/myiq.com?date=last30days&stars=1&stars=4`
- Customizable via the `target_url` constructor parameter
- Headless mode is commented out — uncomment for server/background execution

**Review Schema (raw):**
```python
{
    "id": "rev_a1b2c3d4",           # UUID-based unique identifier
    "platform": "Truspilot",         # Source platform name
    "author": "John Doe",            # Customer display name
    "text": "Great product!",        # Full review text
    "timestamp": datetime(2026, 6, 21),  # Scraped timestamp
    "url": "https://...",            # Source URL
    "sentiment": "PENDING",          # Pre-analysis placeholder
    "score": 0.0,                    # Pre-analysis placeholder
    "response": "",                  # AI response (generated later)
    "escalated": False               # Escalation flag (set by analyzer)
}
```

### 2. Analyzer (`analyzer/sentiment.py`)

**Class:** `SentimentAnalyzer`

Uses Hugging Face's `pipeline("sentiment-analysis")` with the **distilbert-base-uncased-finetuned-sst-2-english** model — a distilled BERT model fine-tuned on the Stanford Sentiment Treebank (SST-2). This model is **fast, accurate, and runs 100% locally** with no API costs.

**Key Methods:**

| Method | Description |
|--------|-------------|
| `analyze_review(text: str) -> dict` | Returns `{sentiment, score, escalated}` |

**Return Schema:**
```python
{
    "sentiment": "POSITIVE",  # or "NEGATIVE" or "NEUTRAL" (if empty text) or "ERROR"
    "score": 0.9876,          # Confidence score (0.0 to 1.0)
    "escalated": True         # True if NEGATIVE AND score > 0.8
}
```

**Escalation Logic:**
- If `sentiment == "NEGATIVE"` **and** `score > 0.8` → `escalated = True`
- This flags reviews for immediate human attention on the dashboard

### 3. Responder (`responder/ai_responder.py`)

**Class:** `AIResponder`

Generates professional customer service responses using the **OpenRouter API** — a unified API gateway to multiple LLMs. Uses the OpenAI Python SDK pointed at OpenRouter's base URL.

**Default Model:** `stepfun/step-3.5-flash:free` (free tier — no cost)

**Key Methods:**

| Method | Description |
|--------|-------------|
| `generate_reply(review_text, sentiment, customer_name) -> str` | Returns a 1-2 sentence AI-generated response |

**Response Behavior:**

| Sentiment | With API Key | Without API Key |
|-----------|--------------|-----------------|
| **POSITIVE** | AI-generates a thank-you message | Static: "Thank you for the wonderful feedback!" |
| **NEGATIVE** | AI-generates an apology + resolution offer | Static: "We sincerely apologize..." |
| **NEUTRAL** | Returns empty string (no response needed) | Empty string |

**Retry Logic (Exponential Backoff):**
- Maximum 3 retry attempts
- Initial delay: 2 seconds
- Backoff multiplier: 2x per attempt (2s → 4s → 8s)
- Rate limit (429) detection and graceful handling
- If all retries fail, falls back to static responses

**Response Formatting:**
- For NEGATIVE: Includes support contact email and phone number
- For all: Addresses the customer by name if available
- Strictly limited to 1-2 sentences (via prompt engineering)

### 4. Storage (`storage/parquet_manager.py`)

**Class:** `ParquetManager`

Manages persistent storage using **Apache Parquet** files via the **Polars** DataFrame library. Parquet is a columnar storage format that offers excellent compression, fast read/write speeds, and schema enforcement.

**Key Methods:**

| Method | Description |
|--------|-------------|
| `get_reviews_table() -> pl.DataFrame` | Loads existing reviews or returns empty schema. Handles corrupted files gracefully by starting fresh. |
| `append_batch(reviews_list: list)` | Appends multiple reviews at once using diagonal concatenation (handles schema mismatches) |
| `append_review(review_data: dict)` | Wrapper for single review insertion |
| `update_review_status(review_id, new_status, edited_response)` | Finds a review by ID, updates its status and optionally its response text |

**Parquet Schema:**
```python
{
    "id": pl.Utf8,         # String - unique review identifier
    "platform": pl.Utf8,   # String - source platform name
    "author": pl.Utf8,     # String - customer name
    "text": pl.Utf8,       # String - full review text
    "timestamp": pl.Datetime,  # Datetime - when scraped
    "url": pl.Utf8,        # String - source URL
    "sentiment": pl.Utf8,  # String - POSITIVE/NEGATIVE/NEUTRAL/ERROR
    "score": pl.Float64,   # Float - confidence score
    "response": pl.Utf8,   # String - AI or human response
    "escalated": pl.Boolean,   # Bool - escalation flag
    "status": pl.Utf8      # String - PENDING/APPROVED/RESOLVED
}
```

**Corruption Handling:**
- Checks file size before reading (avoids 0-byte file crashes)
- Catches any read exceptions and starts with a fresh empty schema
- Useful for development environments where files may get truncated

### 5. Notifications (`notifications/email_alerter.py`)

**Class:** `EmailAlerter`

Handles email communication via **Gmail SMTP** using SSL on port 465.

**Key Methods:**

| Method | Description |
|--------|-------------|
| `send_escalation_alert(review_data, recipient_email)` | Sends an urgent alert about an escalated negative review to the management team |
| `send_response_email(recipient_email, author_name, response_text)` | Dispatches the final AI/human response directly to the customer |

**Email Templates:**
- **Escalation Alert:** Subject includes 🚨 URGENT prefix, contains review ID, author, score, full text, AI response, and review URL
- **Customer Response:** Polite, professional subject line ("Response to Your Recent Review"), body contains the AI-generated or human-edited response text

**Error Handling:**
- Checks for missing credentials and provides clear error messages
- Detects SMTP error code 535 (authentication failure) and provides troubleshooting hints
- Uses context manager (`with` statement) for secure SSL connection management

### 6. Dashboard (`dashboard/app.py`)

**Type:** Streamlit web application

The executive dashboard is a full-featured, real-time business intelligence interface. See the [Dashboard Tabs Explained](#dashboard-tabs-explained) section below for detailed breakdown of each tab.

**Key Metrics Calculated:**

| Metric | Formula | Range |
|--------|---------|-------|
| **Reputation Score** | `weighted_sentiment * 0.5 + response_rate * 0.3 + escalation_factor * 0.2` | 0–100 |
| **Revenue at Risk** | `min(negative_ratio * 50, 50)` | 0–50% |
| **Retention Impact** | `min(negative_ratio * 30, 30)` | 0–30% |
| **Response Rate** | `responded_reviews / total_reviews * 100` | 0–100% |
| **Brand Equity Index** | `reputation_score * 0.8 + response_rate * 0.2` | 0–100 |
| **Data Freshness** | `max(0, 100 - hours_since_last_update * 2)` | 0–100% |

### 7. Pipeline Orchestrator (`main.py`)

The central pipeline controller. Executes all stages in sequence with status logging.

**Flow:**
1. Loads environment variables via `python-dotenv`
2. Disables Hugging Face symlink warning
3. Initializes all module instances
4. Fetches new reviews via Selenium scraper
5. For each review:
   - Analyzes sentiment using Hugging Face pipeline
   - Generates AI response for POSITIVE/NEGATIVE reviews
   - Sets status to `PENDING`
   - Appends to processing list
   - Waits 3 seconds between reviews (rate limiting)
6. Saves all processed reviews to Parquet in a single batch

---

## 📊 Dashboard Tabs Explained

### 🚨 Alert Center

The operational command center for review management.

- **Active Alerts:** Shows all reviews that are `PENDING` or `ESCALATED` but not yet `RESOLVED` or `APPROVED`
- **Alert Cards:** Horizontal layout with:
  - **Left Panel:** Author name, timestamp, sentiment badge (color-coded), full review text, escalation/pending status
  - **Right Panel:** Editable AI response text area, customer email input field, "Dispatch Final Response" button
- **Dispatch Workflow:**
  1. Review the AI-suggested response
  2. Edit if needed
  3. Enter the customer's email address
  4. Click dispatch — system sends the email and updates status to `RESOLVED`
- **Empty State:** Shows "Corporate Reputation Secured" message when all reviews are handled
- **Raw Data Table:** Full scrollable data table at the bottom for data export/analysis

### 📈 Reputation Trends

Strategic analytics for reputation monitoring over time.

- **Quadrant Chart (4 subplots):**
  - Daily Sentiment Trend (line chart — average sentiment over time)
  - Review Volume (bar chart — daily review count)
  - Escalation Trends (bar chart — daily escalations)
  - Sentiment Distribution (donut pie chart — POSITIVE/NEUTRAL/NEGATIVE split)
- **Sentiment Breakdown:** Interactive pie chart with color coding
- **Sentiment Quality Score:** Percentage of positive reviews displayed as a KPI card
- **Time Series Analysis:** Groups data by date for trend visualization (requires timestamp data)

### 💼 Business Impact

Executive-level business metrics and ROI analysis.

- **Revenue Protection:** Composite score showing how much revenue is protected from negative reviews
- **Customer Loyalty Impact:** Retention score based on sentiment and response metrics
- **Brand Equity Index:** Weighted formula combining reputation and response rate
- **Response Effectiveness:**
  - Response Rate vs Target (65% benchmark)
  - Average Score Improvement (comparing responded vs unresponded reviews)
  - Escalation Reduction (percentage reduction through timely responses)
- **Key Discussion Themes:** Simple NLP keyword extraction across categories: Service, Quality, Price, Speed, Friendliness

### ⚙️ Operations

Operational efficiency and system health monitoring.

- **Team Performance:**
  - Average Response Time (simulated: 2.4h)
  - Issue Resolution Rate (simulated: 87.5%)
  - AI Automation Rate (simulated: 65%)
  - Cost per Review Managed (simulated: $2.50)
- **Workflow Efficiency:** Funnel chart showing the review processing pipeline stages
- **System Health:**
  - Data Freshness (real-time: calculated from latest timestamp)
  - System Uptime (simulated: 99.8%)
  - API Success Rate (simulated: 98.2%)

---

## 📖 Jargon Buster / Glossary

| Term | Definition |
|------|------------|
| **Apache Parquet** | A columnar storage file format that provides efficient data compression and encoding. Used here for storing review data locally. |
| **Bidirectional Encoder Representations from Transformers (BERT)** | A transformer-based machine learning model for NLP tasks. The `distilbert-base-uncased-finetuned-sst-2-english` is a distilled (smaller, faster) version fine-tuned for sentiment analysis. |
| **C-Level** | Executive-level leadership positions (CEO, CTO, CMO, etc.) — the target audience for the dashboard. |
| **CLI (Command-Line Interface)** | A text-based interface for running commands in a terminal/shell. |
| **Composite Score** | A metric derived from multiple weighted sub-metrics, producing a single number (e.g., Reputation Score 0–100). |
| **CRUD (Create, Read, Update, Delete)** | The four basic operations of persistent storage. Implemented via `ParquetManager`. |
| **DAG (Directed Acyclic Graph)** | In this context, refers to the internal memory/task tracking system used by Vritanta for AI state management. |
| **Diagonal Concatenation** | A Polars operation that concatenates DataFrames with potentially different schemas, filling missing columns with null. |
| **DistilBERT** | A distilled version of BERT that is 40% smaller, 60% faster, while retaining 97% of BERT's language understanding. |
| **Environment Variables** | Key-value pairs stored outside the code (in `.env`) for configuration like API keys and credentials. |
| **Escalation** | The process of flagging highly negative reviews (score > 0.8) for immediate human intervention. |
| **Exponential Backoff** | A retry strategy where wait times increase exponentially (2s, 4s, 8s) between failed attempts to avoid overwhelming an API. |
| **Gmail App Password** | A 16-character password generated by Google specifically for application access (not your regular Gmail password). |
| **Headless Mode** | Running a browser without a visible GUI — useful for servers and automated scraping. |
| **Hugging Face Transformers** | An open-source library providing thousands of pre-trained NLP models via a unified API (`pipeline()`). |
| **Human-in-the-Loop** | A workflow design where automated decisions can be reviewed and overridden by humans (the Alert Center workflow). |
| **KPI (Key Performance Indicator)** | A measurable value that demonstrates how effectively a company is achieving key business objectives. |
| **LLM (Large Language Model)** | A neural network model trained on vast text data to generate human-like text (e.g., GPT-4, Llama 3, Step 3.5). |
| **NLP (Natural Language Processing)** | A branch of AI focused on enabling computers to understand, interpret, and generate human language. |
| **OpenRouter** | An API gateway that provides unified access to multiple LLMs (Llama, GPT, Claude, etc.) through a single SDK. |
| **Orchestrator** | A centralized controller that coordinates multiple services/modules in a defined sequence (here, `main.py`). |
| **Pandas vs Polars** | Both are DataFrame libraries. Polars is a modern, Rust-based alternative that is significantly faster, memory-efficient, and supports lazy evaluation. |
| **Pipeline** | A sequence of data processing stages where the output of one stage feeds into the next. |
| **Plotly** | A graphing library that creates interactive, web-based visualizations (charts, graphs, dashboards). |
| **Rate Limiting** | API restrictions that limit the number of requests within a time window. Triggered when exceeded (HTTP 429). |
| **Sentiment Analysis** | The use of NLP to determine the emotional tone of text — classifying it as positive, negative, or neutral. |
| **Selenium** | A browser automation tool used here to programmatically navigate Trustpilot and extract review data. |
| **SMTP (Simple Mail Transfer Protocol)** | The standard protocol for sending emails. Used via Gmail's SMTP server (`smtp.gmail.com:465`). |
| **SST-2 (Stanford Sentiment Treebank v2)** | A dataset of movie reviews labeled for binary sentiment classification. The DistilBERT model used here was fine-tuned on SST-2. |
| **Streamlit** | A Python framework that turns data scripts into interactive web apps with minimal code. |
| **Symlink Warning** | A Hugging Face warning about symbolic link support on Windows. Disabled via `HF_HUB_DISABLE_SYMLINKS_WARNING=1`. |
| **Transformers** | The deep learning architecture that powers modern NLP models, based on self-attention mechanisms. |
| **Trustpilot** | An online review platform where consumers can review businesses. This is the default scraping target. |
| **UUID (Universally Unique Identifier)** | A 128-bit label used for unique identification. The scraper uses the first 8 hex characters of a UUID as review IDs. |
| **XPath** | A query language for selecting nodes from XML/HTML documents. Used by Selenium to find review elements. |

---

## 🌐 Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENROUTER_API_KEY` | ✅ Yes | — | API key from [openrouter.ai/keys](https://openrouter.ai/keys) |
| `GMAIL_USER` | ✅ Yes* | — | Your full Gmail address (e.g., `you@gmail.com`) |
| `GMAIL_APP_PASSWORD` | ✅ Yes* | — | 16-character Gmail App Password |
| `SUPPORT_EMAIL` | ❌ No | `support@example.com` | Displayed in AI-generated responses for negative reviews |
| `SUPPORT_PHONE` | ❌ No | `1-800-123-4567` | Displayed in AI-generated responses for negative reviews |

*\* Required for email features. The pipeline and dashboard will work without Gmail credentials, but email dispatch will fail.*

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository on GitHub
2. **Create a feature branch:** `git checkout -b feature/amazing-feature`
3. **Commit your changes:** `git commit -m 'Add amazing feature'`
4. **Push to the branch:** `git push origin feature/amazing-feature`
5. **Open a Pull Request** on the [GitHub repository](https://github.com/ProBm0203/Social_Review_Guardian)

**Development Guidelines:**
- Write unit tests for new features (see `test_all.py` for patterns)
- Follow PEP 8 style guidelines
- Use meaningful variable/function names
- Add docstrings to all public methods
- Update this README if you change functionality

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Made with ❤️ for businesses who take their online reputation seriously<br>
  <a href="https://github.com/ProBm0203/Social_Review_Guardian">GitHub Repository</a> •
  <a href="https://github.com/ProBm0203/Social_Review_Guardian/issues">Report a Bug</a> •
  <a href="https://github.com/ProBm0203/Social_Review_Guardian">Request a Feature</a>
</p>