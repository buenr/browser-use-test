## Finviz Headline Scraper (`fetch_headlines.py`)

This script fetches financial news headlines from Finviz.

**Features:**

*   Retrieves news from two Finviz pages:
    *   Market News: `https://finviz.com/news.ashx`
    *   Stocks News: `https://finviz.com/news.ashx?v=3`
*   Combines headlines from both sources.
*   De-duplicates the combined list to ensure unique headlines, preserving the order of first appearance.
*   Includes pseudocode demonstrating how the collected headlines could be:
    *   Formatted into a prompt.
    *   Sent to a generative AI model like Google Gemini for summarization (requires user's own API key and setup).
*   Prints the unique headlines to the console.

**Setup and Usage:**

1.  **Install Dependencies:**
    Open your terminal and run:
    ```bash
    pip install -r requirements.txt
    ```
    This will install `requests`, `beautifulsoup4`, and `google-generativeai` (the last one is for the conceptual Gemini integration).

2.  **Run the Script:**
    ```bash
    python fetch_headlines.py
    ```
    The script will output the fetched headlines and the Gemini summarization pseudocode.

**Note on Gemini Integration:**
The script includes a section with *pseudocode* for sending headlines to the Google Gemini API. To make this functional, you would need to:
*   Have the `google-generativeai` library installed (as per `requirements.txt`).
*   Obtain a Google API key with access to the Gemini API.
*   Uncomment the relevant sections in the `summarize_headlines_with_gemini_pseudocode` function within `fetch_headlines.py` and insert your API key.
