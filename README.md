# Financial News Headline Scraper and JSON Converter

This project fetches financial news headlines from Yahoo Finance's RSS feed, then uses Google Gemini to process this data and output it in a structured JSON format.

## Features

- Fetches news from Yahoo Finance top stories RSS feed.
- Processes the news data (titles, links, publication dates, summaries) using Google Gemini.
- Outputs a JSON array where each object represents a news item with the following keys:
    - `headline`: The news article's title.
    - `source_url`: The direct link to the article.
    - `publication_date`: The date the article was published.
    - `brief_summary`: A concise summary of the article (can be from the RSS feed or refined by Gemini).

## Prerequisites

- Python 3.7+
- Pip (Python package installer)

## Setup

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Set up a Python virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your Google Gemini API Key:**
    This script requires a Google Gemini API key. You need to:
    - Obtain an API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
    - Set it as an environment variable named `GOOGLE_API_KEY`.
      - On Linux/macOS:
        ```bash
        export GOOGLE_API_KEY="YOUR_API_KEY_HERE"
        ```
      - On Windows (Command Prompt):
        ```bash
        set GOOGLE_API_KEY="YOUR_API_KEY_HERE"
        ```
      - Or on Windows (PowerShell):
        ```bash
        $env:GOOGLE_API_KEY="YOUR_API_KEY_HERE"
        ```
    Replace `"YOUR_API_KEY_HERE"` with your actual key. You might want to add this to your shell's profile file (e.g., `.bashrc`, `.zshrc`) for persistence.

## Running the Script

Once the setup is complete, you can run the script:

```bash
python scraper.py
```

The script will print the JSON output to the console. If the `GOOGLE_API_KEY` is not set, it will print an error message within the JSON output for the Gemini processing part.

Example output snippet:
```json
[
  {
    "headline": "Example News Headline Title",
    "source_url": "https://finance.yahoo.com/news/example-article-12345.html",
    "publication_date": "Mon, 01 Jul 2024 10:00:00 GMT",
    "brief_summary": "This is a brief summary of the news article, potentially refined by Gemini."
  },
  // ... more news items
]
```

## How it Works

1.  The script fetches the latest financial news from the Yahoo Finance RSS feed (`https://finance.yahoo.com/rss/topstories`) using the `requests` and `feedparser` libraries.
2.  The collected news items (title, link, summary, published date) are then passed to the Google Gemini API (`gemini-pro` model).
3.  A prompt instructs Gemini to structure this information into a JSON array, with each news item having a "headline", "source_url", "publication_date", and "brief_summary".
4.  The script then prints this final JSON to the standard output.

```
