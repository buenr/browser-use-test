import requests
from bs4 import BeautifulSoup
from typing import List, Tuple
from dotenv import load_dotenv
import os

load_dotenv('.env')

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

def summarize_headlines_with_gemini(headlines: List[Tuple[str, str]]):
    print("\n--- Google Gemini Summarization ---")
    if not headlines:
        print("No headlines available to summarize.")
        return

    print(f"Sending {len(headlines)} headlines to Google Gemini for summarization...")

    # Format headlines into a prompt
    prompt_headlines = "\n".join([f"{time} {text}" for time, text in headlines])
    full_prompt = (
        "Please summarize the following financial news headlines, "
        "highlighting key market trends or significant events. "
        "Focus on identifying any major market-moving news, sector trends, "
        "or economic indicators mentioned across these headlines:\n\n"
        f"{prompt_headlines}\n\n"
        "Provide a concise summary in 3-5 bullet points."
    )

    try:
        import google.generativeai as genai
        from google.generativeai.types.generation_types import StopCandidateException
        from google.api_core.exceptions import InvalidArgument

        # Configure the Gemini API
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

        # Initialize the model
        model = genai.GenerativeModel('gemini-2.0-flash')

        try:
            print("Generating summary...")
            response = model.generate_content(full_prompt)
            print("\n--- AI Summary ---")
            print(response.text)
            print("--- End of AI Summary ---")
            return response.text
            
        except StopCandidateException as e:
            print(f"Content generation was stopped: {e}")
        except InvalidArgument as e:
            print(f"Invalid argument provided to the API: {e}")
        except Exception as e:
            print(f"An error occurred during content generation: {e}")

    except ImportError:
        print("Google Generative AI library not found.")
        print("Please install it using: pip install google-generativeai")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    finviz_urls = ["https://finviz.com/news.ashx", "https://finviz.com/news.ashx?v=3"]
    print(f"Starting to fetch headlines from: {', '.join(finviz_urls)}")

    all_raw_headlines = fetch_finviz_headlines(finviz_urls)  # This returns List[Tuple[str, str]]

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

    # Generate summary using Gemini
    summarize_headlines_with_gemini(unique_headlines_ordered)
