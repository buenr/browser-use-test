import requests
from bs4 import BeautifulSoup

def fetch_finviz_headlines():
    url = "https://finviz.com/news.ashx"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Raises an HTTPError for bad responses (4XX or 5XX)
        print("Successfully fetched page content from Finviz news.")

        soup = BeautifulSoup(response.text, 'html.parser')
        # print(soup.prettify()) # Keep this commented unless debugging is needed again

        # Find the main container table for news and blogs
        main_container_table = soup.find('table', class_='news_time-table')

        if not main_container_table:
            print("Could not find the main news container table (selector: 'table.news_time-table'). Page structure might have changed.")
            return

        # The actual news articles are in tables nested within the main_container_table.
        # We'll target the first such nested table, which usually contains the primary news feed.
        # These inner tables have class 'styled-table-new'.
        news_article_table = main_container_table.find('table', class_='styled-table-new')

        if not news_article_table:
            print("Could not find the specific news articles table (selector: 'table.styled-table-new' within 'table.news_time-table').")
            return

        # News rows have the class 'news_table-row'
        news_rows = news_article_table.find_all('tr', class_='news_table-row')

        if not news_rows:
            print("No news headlines found within the news articles table (selector: 'tr.news_table-row'). Check selectors or page content.")
            return

        print("\n--- Finviz News Headlines ---")
        parsed_count = 0
        processed_rows = 0
        for row in news_rows:
            processed_rows += 1
            # Using a lambda for more robust class matching for the time cell
            time_cell = row.find('td', class_=lambda c: c and 'news_date-cell' in c.split())
            # The headline is inside an 'a' tag with class 'nn-tab-link'
            headline_anchor = row.find('a', class_='nn-tab-link')

            if time_cell and headline_anchor:
                time_text = time_cell.text.strip()
                headline_text = headline_anchor.text.strip()
                if time_text and headline_text: # Ensure text is not empty
                    print(f"{time_text} {headline_text}")
                    parsed_count += 1
            # No specific 'else' needed here anymore if not debugging individual row failures
            # The final 'if parsed_count == 0' handles the case where nothing was extracted.

        if parsed_count == 0 and processed_rows > 0: # Check if rows were processed but none yielded results
             print(f"Processed {processed_rows} news rows, but could not extract time/headline pairs from any. Final check of selectors (td.news_date-cell, a.nn-tab-link) might be needed if page structure changed.")
        elif processed_rows == 0 and not news_rows : # This case is already handled by "No news headlines found..."
            pass # Already covered by earlier checks for news_rows

        print(f"--- End of Headlines (found {parsed_count}) ---")

    except requests.exceptions.HTTPError as http_err:
        status_code_val = http_err.response.status_code if http_err.response is not None else 'N/A'
        print(f"HTTP error occurred: {http_err} - Status code: {status_code_val}")
        if hasattr(http_err.response, 'status_code'): # Ensure response object exists and has status_code
            if http_err.response.status_code == 403:
                print("Access Forbidden (403). The site may be blocking requests due to the User-Agent or IP.")
            elif http_err.response.status_code == 503:
                print("Service Unavailable (503). The site may be down or overloaded.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during parsing: {e}")


if __name__ == "__main__":
    fetch_finviz_headlines()
