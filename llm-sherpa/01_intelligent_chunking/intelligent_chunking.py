import os
import traceback
from typing import List
from langchain.schema import Document
from llmsherpa.readers import LayoutPDFReader
from termcolor import colored

def intelligent_chunking(file_path: str) -> List[Document]:
    """Processes content from a file and returns chunks as Documents."""
    try:
        print(colored(f"\n\nProcessing content from file: {file_path}\n\n", "green"))
        llmsherpa_api_url = os.environ.get('LLM_SHERPA_SERVER')

        if not llmsherpa_api_url:
            raise ValueError("LLM_SHERPA_SERVER environment variable is not set")

        documents = []
        try: 
            print(colored("Starting LayoutPDFReader...\n\n", "yellow"))
            reader = LayoutPDFReader(llmsherpa_api_url)
            content = reader.read_pdf(file_path)  # Assuming this method works for both PDFs and text files
            print(colored("Finished LayoutPDFReader...\n\n", "yellow"))
        except Exception as e:
            print(colored(f"Error in LayoutPDFReader: {str(e)}", "red"))
            traceback.print_exc()
            content = None
        
        if content:
            for i, chunk in enumerate(content.chunks()):
                document = Document(
                    page_content=chunk.to_context_text(),
                    metadata={"source": file_path}
                )
                documents.append(document)
                print(colored(f"Chunk {i+1}: {chunk.to_context_text()[:200]}...", "cyan"))  # Show first 200 chars of each chunk
            
            print(colored(f"Created corpus with {len(documents)} documents", "green"))
        
        if not content:
            print(colored(f"No content to append to corpus", "red"))
        
        return documents
    
    except Exception as e:        
        print(colored(f"Error processing file {file_path}: {str(e)}", "red"))
        traceback.print_exc()
        return [Document(page_content=f"Error processing file: {file_path}", metadata={"source": file_path})]

if __name__ == "__main__":
    file_path = "test_document.txt"
    results = intelligent_chunking(file_path)
    print(f"\n\nFinal Results: {results}")
