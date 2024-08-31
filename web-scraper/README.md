# Crawlee Web Scraper

## Overview
This repository provides a robust web scraping tool built with Crawlee, Playwright, BeautifulSoup, and markdownify. It allows users to scrape web pages, extract content, and convert it to both plain text and markdown formats, making it ideal for various applications, including large language model (LLM) preprocessing.

## Features
- **Extract Paragraphs**: Extracts all text within `<p>` tags and calculates the total word count.
- **Markdown Conversion**: Converts the entire page content into markdown format, making it suitable for LLM ingestion.
- **Multiprocessing Support**: Allows for scraping multiple URLs concurrently.
- **Sequential Processing**: Supports sequential scraping of multiple URLs with asynchronous handling.

## Installation

### 1. Clone the Repository
First, clone the repository to your local machine:
```bash
git clone <this repo>
cd web-scraper
```

### 2. Set Up Conda Environment
Create and activate a new conda environment:
```bash
conda create -n web_scraper python=3.12 pip
conda activate web_scraper
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright Dependencies (Linux Only)
If you are on a Linux system, install the necessary system dependencies:
```bash
playwright install-deps
```

### 5. Install Playwright Browsers
Install the required browsers for Playwright:
```bash
playwright install
```

## Usage

### 1. Single URL Scraping
To scrape a single URL, modify the `url_to_scrape` variable in the script and run it:
```python
url_to_scrape = 'http://www.example.com'
run_scrape(url_to_scrape)
```
This will print both the extracted paragraphs and the markdown version of the content.

### 2. Multiprocessing
For concurrent scraping using multiple processes, you can use the following pattern:
```python
url_to_scrape = 'http://www.example.com'
url_to_scrape2 = 'https://ollama.com/blog/openai-compatibility'
p = multiprocessing.Process(target=run_scrape, args=(url_to_scrape,))
p.start()
p.join()

p2 = multiprocessing.Process(target=run_scrape, args=(url_to_scrape2,))
p2.start()
p2.join()
```

### 3. Sequential Scraping
For sequential processing of multiple URLs:
```python
urls_to_scrape = [
    'http://www.example.com',
    'https://ollama.com/blog/openai-compatibility'
]
scraped_data_list = asyncio.run(run_scraping_sequentially(urls_to_scrape))

for scraped_data in scraped_data_list:
    print_scraped_data(scraped_data)
```

## Contributing
Contributions are welcome! Feel free to fork the repository, create a feature branch, and submit a pull request.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
