import asyncio
import multiprocessing
from crawlee.playwright_crawler import PlaywrightCrawler, PlaywrightCrawlingContext
from markdownify import markdownify as md
from dataclasses import dataclass
from datetime import datetime
from bs4 import BeautifulSoup
from termcolor import colored

@dataclass
class ScrapedData:
    """A data class to store scraped information."""
    website_name: str
    scraped_at: datetime
    paragraphs: list[str]
    total_words: int
    markdown: str  # New attribute for markdown content

async def scrape_to_scrapeddata(url) -> ScrapedData:
    """Function to scrape a webpage and return the data as a ScrapedData object."""
    crawler = PlaywrightCrawler(max_requests_per_crawl=5, headless=True)
    paragraphs = []
    markdown_content = ""

    @crawler.router.default_handler
    async def request_handler(context: PlaywrightCrawlingContext) -> None:
        nonlocal markdown_content  # Access the markdown_content variable from the outer scope
        await context.page.wait_for_load_state('networkidle')
        content = await context.page.content()
        soup = BeautifulSoup(content, 'html.parser')

        # Extract paragraphs from the HTML content
        for para in soup.find_all('p'):
            paragraphs.append(para.get_text())

        # Convert the entire content to markdown format
        markdown_content = md(content)

    # Run the crawler for the given URL
    await crawler.run([url])
    await crawler._browser_pool._close_inactive_browsers()  # Ensure all browsers are closed
    
    # Calculate the total number of words in the extracted paragraphs
    total_words = sum(len(para.split()) for para in paragraphs)
    
    # Return the scraped data in a ScrapedData object
    return ScrapedData(
        website_name=url,
        scraped_at=datetime.now(),
        paragraphs=paragraphs,
        total_words=total_words,
        markdown=markdown_content
    )

def print_scraped_data(data: ScrapedData):
    """Function to print the scraped data with colored output."""
    print(colored(f"Website: {data.website_name}", 'blue'))
    print(colored(f"Scraped at: {data.scraped_at}", 'cyan'))
    print(colored(f"Total Words: {data.total_words}", 'green'))
    print(colored("Paragraphs:", 'yellow'))
    
    # Print each paragraph in yellow
    for paragraph in data.paragraphs:
        print(colored(paragraph, 'yellow'))
    
    print(colored("\nMarkdown Content:\n", 'magenta'))
    print(colored(data.markdown, 'magenta'))

def run_scrape(url):
    """Run the scraping process for a single URL and print the results."""
    scraped_data = asyncio.run(scrape_to_scrapeddata(url))
    print_scraped_data(scraped_data)

async def run_scraping_sequentially(urls):
    """Run the scraping process sequentially for a list of URLs and collect the results."""
    results = []
    for url in urls:
        # Scrape each URL and append the result to the results list
        scraped_data = await scrape_to_scrapeddata(url)
        results.append(scraped_data)
    return results

if __name__ == '__main__':
    
    # Example usage sequential processing:
    urls_to_scrape = [
        'http://www.example.com',
        'https://ollama.com/blog/openai-compatibility'
    ]
    
    # Run the scraping sequentially for the list of URLs and collect the results
    scraped_data_list = asyncio.run(run_scraping_sequentially(urls_to_scrape))
    
    # Print all collected scraped data
    for scraped_data in scraped_data_list:
        print_scraped_data(scraped_data)
