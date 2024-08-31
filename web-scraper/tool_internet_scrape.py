import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlparse

@dataclass
class ScrapedData:
    website_name: str
    scraped_at: datetime
    paragraphs: list[str]
    total_words: int

def extract_content(url: str) -> ScrapedData:
    try:
        # Fetch the content of the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes

        # Parse the content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the website name from the URL
        # website_name = urlparse(url).netloc

        # Get the current date and time
        scraped_at = datetime.now()

        # Extract all text from paragraphs and calculate total words
        paragraphs = [para.get_text() for para in soup.find_all('p')]
        total_words = sum(len(para.split()) for para in paragraphs)

        # Create an instance of ScrapedData
        scraped_data = ScrapedData(
            website_name=url,
            scraped_at=scraped_at,
            paragraphs=paragraphs,
            total_words=total_words
        )

        return scraped_data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None

# Example usage
url = "https://ollama.com/blog/openai-compatibility"
data = extract_content(url)
print(data)
