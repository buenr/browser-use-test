import asyncio
import os
from datetime import datetime, timedelta
from typing import List

from browser_use import Agent, BrowserSession, Controller, ActionResult
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel, Field

# --- 1. Load Environment Variables ---
load_dotenv()

# Retrieve Azure-specific environment variables
azure_openai_api_key = os.getenv('AZURE_OPENAI_KEY')
azure_openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')

if not azure_openai_api_key or not azure_openai_endpoint:
	raise ValueError('AZURE_OPENAI_KEY or AZURE_OPENAI_ENDPOINT is not set')


# --- 2. Pydantic Models for Structured Output ---
# This defines the data structure the agent must return.

class Product(BaseModel):
    """Represents a single product on the leaderboard."""
    name: str = Field(description="The name of the product.")
    description: str = Field(description="A short description of the product.")
    upvotes: int = Field(description="The number of upvotes (likes) the product has received, as highlighted in the screenshot.")

class DailyLeaderboard(BaseModel):
    """Represents the leaderboard for a single day."""
    date: str = Field(description="The date of the leaderboard in YYYY-MM-DD format.")
    products: List[Product] = Field(description="A list of the top products for that day.")

class FinalReport(BaseModel):
    """The final compiled report containing data for all requested days."""
    leaderboards: List[DailyLeaderboard] = Field(description="A list of leaderboards, one for each day.")


# --- 3. Custom Controller and Action Functions ---
# We extend the agent's capabilities with a custom tool for scraping.

# The controller will enforce the FinalReport as the required output format
controller = Controller(output_model=FinalReport)

@controller.action(
    "Extracts product information from the current Product Hunt leaderboard page.",
    param_model=None  # This action takes no parameters from the LLM
)
async def extract_leaderboard_data(page) -> ActionResult:
    """
    Scans the current page for product listings and extracts their name,
    description, and upvote count.
    """
    print("🤖 Executing custom action: extract_leaderboard_data...")
    try:
        # Wait for the main content to be visible to ensure the page is loaded
        await page.wait_for_selector('div[data-test^="post-item-"]', timeout=15000)
        product_elements = await page.query_selector_all('div[data-test^="post-item-"]')
        
        extracted_products = []
        
        # Limit to the top 5 for a quicker demonstration
        for item in product_elements[:5]:
            name_element = await item.query_selector('h3')
            description_element = await item.query_selector('div > div > div:nth-child(2)')
            upvote_element = await item.query_selector('div[class*="styles_voteButtonContainer"] button > div > div')

            name = await name_element.inner_text() if name_element else "N/A"
            description = await description_element.inner_text() if description_element else "N/A"
            upvotes_text = "0"
            if upvote_element:
                upvotes_text = await upvote_element.inner_text()

            try:
                upvotes = int(upvotes_text.strip())
            except (ValueError, AttributeError):
                upvotes = 0

            extracted_products.append(
                Product(name=name, description=description, upvotes=upvotes)
            )

        if not extracted_products:
            return ActionResult(extracted_content="No products found on the page.", include_in_memory=True)
        
        current_date_str = page.url.split("/daily/")[1].replace('/', '-')
        
        daily_data = DailyLeaderboard(date=current_date_str, products=extracted_products)

        print(f"✅ Successfully extracted {len(extracted_products)} products for {current_date_str}.")
        
        # Return the structured data as a JSON string for the LLM to process
        return ActionResult(extracted_content=daily_data.model_dump_json(indent=2), include_in_memory=True)
    except Exception as e:
        print(f"❌ Error in extract_leaderboard_data: {e}")
        return ActionResult(extracted_content=f"An error occurred: {str(e)}", is_error=True)


# --- 4. Main Agent Execution Logic ---

async def main():
    """Sets up and runs the advanced browser-use agent."""
    print("🚀 Starting the Product Hunt Leaderboard Scraper Agent...")

    # --- Date and URL Generation ---
    # The prompt uses a future date (2025). To get real data, we'll use a recent date.
    # Let's pretend "today" is a day in the recent past with valid data.
    today = datetime.now() - timedelta(days=5) # Use a recent date
    date_urls = [
    f"https://www.producthunt.com/leaderboard/daily/{dt.year}/{dt.month}/{dt.day}"
    for dt in [(today - timedelta(days=i)) for i in range(10)]
    ]

    print("\n📋 URLs to be scraped:")
    for url in date_urls:
        print(url)

    # --- Agent Configuration ---
    llm = AzureChatOpenAI(
	model='gpt-4.1',
	api_key=azure_openai_api_key,
	azure_endpoint=azure_openai_endpoint,  # Corrected to use azure_endpoint instead of openai_api_base
	api_version='2025-01-01-preview',  # Explicitly set the API version here
    )
    
    browser_session = BrowserSession(
        headless=True,
        viewport={'width': 1280, 'height': 1024},
    )

    message_context = "You are an expert web scraping agent. Your mission is to gather data from Product Hunt's daily leaderboards."
    extend_system_message = (
        "CRITICAL RULE: You must visit each URL provided, use the `extract_leaderboard_data` tool, and remember the result. "
        "After processing ALL URLs, consolidate the daily leaderboards into the final `FinalReport` JSON format "
        "and call the `finish` action with this complete data structure. Do not finish until all 10 days are processed."
    )
    task = (
        f"Compile a report of the top 5 products from Product Hunt's daily leaderboard for the last 10 days. "
        f"Here are the exact URLs you must visit in order:\n"
        f"{chr(10).join(date_urls)}\n\n"
        "Follow these steps:\n"
        "1. Open the first URL.\n"
        "2. Use the `extract_leaderboard_data` tool.\n"
        "3. Remember the result and move to the next URL.\n"
        "4. Repeat until all URLs are done.\n"
        "5. Once all 10 days are extracted, format the complete data into the `FinalReport` structure and call the `finish` action."
    )
    initial_actions = [{'open_tab': {'url': date_urls[0]}}]

    # --- Instantiate and Run the Agent ---
    agent = Agent(
        task=task,
        llm=llm,
        controller=controller,
        browser_session=browser_session,
        message_context=message_context,
        extend_system_message=extend_system_message,
        initial_actions=initial_actions,
    )

    print("\n🤖 Agent is configured. Starting run...")
    history = await agent.run(
        max_steps=50)
    
    print("\n🏁 Agent run finished.")

    # --- Process and Display Results ---
    final_result_json = history.final_result()
    if final_result_json:
        print("\n\n--- 📊 FINAL REPORT ---")
        try:
            final_report = FinalReport.model_validate_json(final_result_json)
            print(final_report.model_dump_json(indent=2))
            
            report_path = "product_hunt_leaderboard_report.json"
            with open(report_path, "w") as f:
                f.write(final_report.model_dump_json(indent=2))
            print(f"\n✅ Report saved to {report_path}")
        except Exception as e:
            print("\n❌ Failed to parse the final result. See raw output below:")
            print(final_result_json)
            print(f"Validation Error: {e}")
    else:
        print("\n⚠️ Agent did not produce a final result.")
        if errors := history.errors():
            print("\n--- Agent Errors ---")
            for error in errors: print(error)
        else:
            print("No errors were explicitly logged, but the task was not completed.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 User interrupted the process.")
