import requests
from bs4 import BeautifulSoup
from typing import List, Tuple

def fetch_finviz_headlines(urls: List[str]) -> List[Tuple[str, str]]:
    all_headlines: List[Tuple[str, str]] = []

    for url in urls:
        print(f"Fetching headlines from: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            print(f"Successfully fetched page content from {url}.")

            soup = BeautifulSoup(response.text, 'html.parser')

            target_table = None
            # The news table is usually within a <td class="contentpaneopen"> which itself is in a table.
            # Then, inside contentpaneopen, there are more tables. The news one is 'styled-table-new'
            # and contains rows with 'news_table-row'.

            # Find all tables with class 'styled-table-new' as candidates
            candidate_tables = soup.find_all('table', class_='styled-table-new')

            for table_candidate in candidate_tables:
                # Check if this table is directly involved with news rows and has a 'nn-tab-link'
                # This helps differentiate from other 'styled-table-new' tables (like for blogs, if on same page)
                # A more direct check: the news table seems to be the one whose direct parent TR has no class or specific ID,
                # and is a child of a TD that's part of the main page layout.
                # The simplest robust check is if it contains 'news_table-row' and 'nn-tab-link'
                if table_candidate.find('tr', class_='news_table-row') and table_candidate.find('a', class_='nn-tab-link'):
                    # Check if this table is for general news (usually on the left) vs blogs (usually on the right)
                    # The main news table is typically the first one that fits this criteria under the main content area.
                    # A common structure is <div id="news"> -> <table class="news_time-table"> -> multiple TDs -> styled-table-new
                    # We are interested in the 'News' section not 'Blogs' if they are side by side.
                    # The 'News' section table is usually the first one.
                    # Let's assume the first one found that contains actual news rows is the one.
                    target_table = table_candidate
                    break

            if not target_table:
                # Fallback if the above doesn't isolate it, try finding within 'news_time-table' as per previous success
                main_container_table = soup.find('table', class_='news_time-table')
                if main_container_table:
                    target_table = main_container_table.find('table', class_='styled-table-new')

            if not target_table:
                print(f"Could not find the specific news articles table in {url}.")
                continue

            news_rows = target_table.find_all('tr', class_='news_table-row')

            if not news_rows:
                print(f"No news headlines found (news_table-row) in {url}.")
                continue

            processed_for_url = 0
            for row in news_rows:
                time_cell = row.find('td', class_=lambda c: c and 'news_date-cell' in c.split())
                headline_anchor = row.find('a', class_='nn-tab-link')

                if time_cell and headline_anchor:
                    time_text = time_cell.text.strip()
                    headline_text = headline_anchor.text.strip()
                    if time_text and headline_text:
                        all_headlines.append((time_text, headline_text))
                        processed_for_url += 1
            print(f"Processed {processed_for_url} headlines from {url}.")

        except requests.exceptions.HTTPError as http_err:
            status_code_val = http_err.response.status_code if http_err.response is not None else 'N/A'
            print(f"HTTP error occurred for {url}: {http_err} - Status code: {status_code_val}")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred during the request for {url}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during parsing of {url}: {e}")

    return all_headlines

def summarize_headlines_with_gemini_pseudocode(headlines: List[Tuple[str, str]]):
    print("\n--- Google Gemini Summarization (Pseudocode) ---")
    if not headlines:
        print("No headlines available to summarize.")
        return

    print(f"Imagine these {len(headlines)} headlines are now being sent to a generative AI model like Google Gemini:")

    # 1. Format headlines into a prompt
    prompt_headlines = "\n".join([f"{time} {text}" for time, text in headlines])
    full_prompt = (
        "Please summarize the following financial news headlines, "
        "highlighting key market trends or significant events:\n\n"
        f"{prompt_headlines}\n\nSummary:"
    )

    print("\nFormatted Prompt (first 500 chars):")
    print(full_prompt[:500] + "..." if len(full_prompt) > 500 else full_prompt)

    print("\n# --- PSEUDOCODE FOR GEMINI API CALL ---")
    print("# import google.generativeai as genai")
    print("# ")
    print("# # IMPORTANT: Replace with your actual API key")
    print("# genai.configure(api_key='YOUR_GOOGLE_API_KEY')")
    print("# ")
    print("# # Initialize the model (e.g., gemini-pro)")
    print("# model = genai.GenerativeModel('gemini-pro')")
    print("# ")
    print("# try:")
    print("#     print('\n# Attempting to generate content (this is still pseudocode)...')")
    print("#     # response = model.generate_content(full_prompt)")
    print("#     # print('\n# --- AI Summary (Pseudocode) ---')")
    print("#     # print(response.text)")
    print("# except Exception as e:")
    print("#     print(f'# An error occurred during hypothetical Gemini API call: {e}')")
    print("# finally:")
    print("#     print('# --- End of AI Summary (Pseudocode) ---')")
    print("# ")
    print("# NOTE: To run this, you would need to:")
    print("# 1. Install the library: pip install google-generativeai")
    print("# 2. Obtain an API key from Google AI Studio or Google Cloud.")
    print("# 3. Uncomment the code above and replace 'YOUR_GOOGLE_API_KEY'.")
    print("# --- END OF PSEUDOCODE ---")

if __name__ == "__main__":
    finviz_urls = ["https://finviz.com/news.ashx", "https://finviz.com/news.ashx?v=3"]
    print(f"Starting to fetch headlines from: {', '.join(finviz_urls)}")

    all_raw_headlines = fetch_finviz_headlines(finviz_urls) # This returns List[Tuple[str, str]]

    print(f"\n--- Processing Headlines ---")
    print(f"Total raw headlines fetched (including duplicates): {len(all_raw_headlines)}")

    # De-duplicate using dict.fromkeys to preserve order and remove duplicates
    unique_headlines_ordered = list(dict.fromkeys(all_raw_headlines))

    print(f"Total unique headlines: {len(unique_headlines_ordered)}")

    print(f"\n--- Unique Headlines ({len(unique_headlines_ordered)}) ---")
    if unique_headlines_ordered:
        for time, text in unique_headlines_ordered:
            print(f"{time} {text}")
    else:
        print("No unique headlines to display.")
    print("--- End of Unique Headlines ---")

    # Store for Gemini (next step)
    final_headlines_for_summary = unique_headlines_ordered

    # Placeholder for Gemini summarization (next step)
    # summary = summarize_headlines_with_gemini(final_headlines_for_summary)

    summarize_headlines_with_gemini_pseudocode(final_headlines_for_summary)
