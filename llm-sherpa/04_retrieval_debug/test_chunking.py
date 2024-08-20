import os
from typing import List
from termcolor import colored
from llmsherpa.readers import LayoutPDFReader
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

def print_chunks(chunks: List[str]):
    """Prints out each chunk's size and content."""
    for i, chunk in enumerate(chunks):
        num_chars = len(chunk)
        num_words = len(chunk.split())
        print(colored(f"Chunk {i+1}: {chunk}", "cyan"))
        print(colored(f"Characters: {num_chars} | Words: {num_words}\n", "yellow"))

def chunk_document(file_path: str):
    """Processes content from a file and chunks it."""
    try:
        print(colored(f"\n\nProcessing content from file: {file_path}\n\n", "green"))
        llmsherpa_api_url = os.environ.get('LLM_SHERPA_SERVER')

        if not llmsherpa_api_url:
            raise ValueError("LLM_SHERPA_SERVER environment variable is not set")

        print(colored("Starting LayoutPDFReader...\n\n", "yellow"))
        reader = LayoutPDFReader(llmsherpa_api_url)
        content = reader.read_pdf(file_path)
        print(colored("Finished LayoutPDFReader...\n\n", "yellow"))

        if content:
            chunks = [chunk.to_context_text() for chunk in content.chunks()]
            print_chunks(chunks)
        else:
            print(colored("No content found.", "red"))
    
    except Exception as e:
        print(colored(f"Error processing file {file_path}: {str(e)}", "red"))

if __name__ == "__main__":
    # Sample file path
    file_path = "../docs/world-war-2.pdf"

    chunk_document(file_path)
