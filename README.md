# This is the github repo for testing browser-use. This application will use Playwright to grab data from a website, pass the scraped data to Google Gemini 2.0 Pro to parse using structured outputs.

Gemini Structured Outputs example:
%pip install google-genai pydantic
import os
from google import genai
from pydantic import BaseModel

# create client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY","xxx"))


# Define Pydantic schemas 
class Ingredient(BaseModel):
  name: str
  quantity: str
  unit: str

class Recipe(BaseModel):
  recipe_name: str
  ingredients: list[Ingredient]


# Generate a list of cookie recipes
response = client.models.generate_content(
    model='gemini-2.0-flash-lite',
    contents='List a few popular cookie recipes.',
    config={
        'response_mime_type': 'application/json',
        'response_schema': list[Recipe],
    },
)
# Use the parsed response
recipes: list[Recipe] = response.parsed
recipes
