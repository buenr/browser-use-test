## Product Hunt Daily Leaderboard Scraper (`ProductHunt.py`)

This script helps you discover the latest trending products from Product Hunt, a popular website where new tech products are launched and discussed.

**What it does:**

*   **Visits Product Hunt:** The script automatically goes to the "daily leaderboard" pages on ProductHunt.com for the last 10 days.
*   **Finds Top Products:** For each day, it looks for the top 5 products listed.
*   **Gathers Information:** For each of these top products, it collects:
    *   The product's name.
    *   A short description of what the product does.
    *   The number of "upvotes" (likes) it has received.
*   **Saves the Data:** All this information (name, description, upvotes for the top 5 products from each of the 10 days) is saved into a file called `product_hunt_leaderboard_report.json`. This file is structured in a way that's easy for other programs to read, but you can also open it with a text editor to see the results.

**Why is this useful?**

*   **Stay Updated:** Quickly see what new products are getting attention in the tech world.
*   **Market Research:** Get a sense of current trends and what kinds of products people are excited about.
*   **Discover New Tools:** You might find new apps or services that could be useful to you.

**How to use it (Simplified):**

1.  **Setup (for developers):** If you're a developer, you'll need to make sure Python and some helper tools (listed in `requirements.txt`) are installed. You'll also need to provide API keys for Azure OpenAI in a special configuration file (`.env`) for the script's more advanced features to work (though the basic scraping might work without it, the script is designed to use AI).
2.  **Running the script (for developers):**
    ```bash
    python ProductHunt.py
    ```
3.  **Viewing the results:** After the script finishes, you'll find a file named `product_hunt_leaderboard_report.json` in the same directory. This file contains all the data it collected.

**Technical Notes (for those interested):**

*   The script uses tools to browse the web automatically (like a robot).
*   It's designed to structure the collected data neatly using a library called `pydantic`.
*   It uses `langchain_openai` which suggests it's built to potentially interact with advanced AI models from Azure OpenAI to process or understand the data it gathers, though the primary function described here is scraping.

---
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
