import sys
import os
import uuid
import requests
import traceback
import concurrent.futures
import functools
from typing import Dict, List
from termcolor import colored
from langchain.schema import Document
from fake_useragent import UserAgent
import chromadb
from chromadb.config import Settings
from llmsherpa.readers import LayoutPDFReader
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

ua = UserAgent()
os.environ["USER_AGENT"] = ua.random

# Initialize Chroma client with HttpClient
chroma_client = chromadb.HttpClient(
    host="localhost",
    port=8085,
    settings=Settings()
)

def timeout(max_timeout):
    """Timeout decorator, parameter in seconds."""
    def timeout_decorator(item):
        """Wrap the original function."""
        @functools.wraps(item)
        def func_wrapper(*args, **kwargs):
            """Closure for function."""
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(item, *args, **kwargs)
                try:
                    return future.result(max_timeout)
                except concurrent.futures.TimeoutError:
                    return [Document(page_content=f"Timeout occurred while processing URL: {args[0]}", metadata={"source": args[0]})]
        return func_wrapper
    return timeout_decorator

def generate_embedding(text: str) -> List[float]:
    """Generate an embedding for the given text using the Ollama server."""
    try:
        ollama_api_url = os.getenv("OLLAMA_API_URL")
        response = requests.post(
            f"{ollama_api_url}/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": text}
        )
        response.raise_for_status()
        embedding = response.json().get("embedding")
        return embedding
    except Exception as e:
        print(colored(f"Error generating embedding: {str(e)}", "red"))
        traceback.print_exc()
        return []

@timeout(20)  # 20 second timeout
def intelligent_chunking(url: str) -> List[Document]:
    try:
        print(colored(f"\n\nStarting Intelligent Chunking with LLM Sherpa for URL: {url}\n\n", "green"))
        llmsherpa_api_url = os.environ.get('LLM_SHERPA_SERVER')

        if not llmsherpa_api_url:
            raise ValueError("LLM_SHERPA_SERVER environment variable is not set")
        
        corpus = []

        try: 
            print(colored("Starting LLM Sherpa LayoutPDFReader...\n\n", "yellow"))
            reader = LayoutPDFReader(llmsherpa_api_url)
            doc = reader.read_pdf(url)
            print(colored("Finished LLM Sherpa LayoutPDFReader...\n\n", "yellow"))
        except Exception as e:
            print(colored(f"Error in LLM Sherpa LayoutPDFReader: {str(e)}", "red"))
            traceback.print_exc()
            doc = None
        
        if doc:
            for chunk in doc.chunks():
                document = Document(
                    page_content=chunk.to_context_text(),
                    metadata={"source": url}
                )
                corpus.append(document)
            
            print(colored(f"Created corpus with {len(corpus)} documents", "green"))
        
        if not doc:
            print(colored(f"No document to append to corpus", "red"))
        
        return corpus
    
    except concurrent.futures.TimeoutError:
        print(colored(f"Timeout occurred while processing URL: {url}", "red"))
        return [Document(page_content=f"Timeout occurred while processing URL: {url}", metadata={"source": url})]
    except Exception as e:        
        print(colored(f"Error in Intelligent Chunking for URL {url}: {str(e)}", "red"))
        traceback.print_exc()
        return [Document(page_content=f"Error in Intelligent Chunking for URL: {url}", metadata={"source": url})]

def index_and_rank(corpus: List[Document], query: str, top_percent: float = 60) -> List[Dict[str, str]]:
    print(colored(f"\n\nStarting indexing and ranking with Chroma DB for {len(corpus)} documents\n\n", "green"))

    collection_name = "documents_collection"

    try:
        print("Initialize Chroma collection (will create if it doesn't exist)")
        existing_collections = chroma_client.list_collections()
        collection_exists = False
        for existing_collection in existing_collections:
            if existing_collection.name == collection_name:
                print(f"Collection '{collection_name}' already exists. Deleting the existing collection.")
                chroma_client.delete_collection(name=collection_name)
                collection_exists = True
                break
        if not collection_exists:
            print("Creating new Chroma collection")
        collection = chroma_client.get_or_create_collection(name=collection_name)


        # Embed and store each document using the Ollama server
        for doc in corpus:
            try:
                embedding = generate_embedding(doc.page_content)
                collection.add(
                    ids= str(uuid.uuid4()),
                    embeddings=[embedding],
                    metadatas=[doc.metadata],
                    documents=[doc.page_content],
                )
            except Exception as e:
                print(colored(f"Error embedding and storing document: {str(e)}", "red"))
                traceback.print_exc()

        print(colored(f"Total documents indexed in Chroma DB: {len(corpus)}", "green"))

        # Perform the similarity search using the Ollama server for embedding the query
        query_embedding = generate_embedding(query)
        results = collection.query(query_embeddings=[query_embedding], n_results=40)

        passages = []
        for idx, result in enumerate(results["documents"]):
            try:
                passage = {
                    "id": idx + 1,
                    "text": result,
                    "meta": results["metadatas"][idx],
                    "score": results["distances"][idx]
                }
                passages.append(passage)
            except Exception as e:
                print(colored(f"Error processing search result: {str(e)}", "red"))
                traceback.print_exc()

        # Sort results by score in descending order
        sorted_results = sorted(passages, key=lambda x: x['score'], reverse=True)

        # Calculate the number of results to return based on the percentage
        num_results = max(1, int(len(sorted_results) * (top_percent / 100)))
        final_results = sorted_results[:num_results]

        print(colored(f"\n\nReturned top {top_percent}% of results ({len(final_results)} documents)\n\n", "green"))

        return final_results

    except Exception as e:
        print(colored(f"Error in indexing and ranking with Chroma DB: {str(e)}", "red"))
        traceback.print_exc()
        return [{"text": "Error in indexing and ranking", "meta": {"source": "unknown"}, "score": 0.0}]

def run_rag(urls: List[str], query: str) -> List[Dict[str, str]]:
    # Use ThreadPoolExecutor instead of multiprocessing
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(urls), 3)) as executor:
        futures = [executor.submit(intelligent_chunking, url) for url in urls]
        chunks_list = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    # Flatten the list of lists into a single corpus
    corpus = [chunk for chunks in chunks_list for chunk in chunks]
    print(colored(f"\n\nTotal documents in corpus after chunking: {len(corpus)}\n\n", "green"))
    
    ranked_docs = index_and_rank(corpus, query)
    return ranked_docs

if __name__ == "__main__":
    # For testing purposes.
    url1 = "https://learning.sap.com/learning-journeys/explore-the-technical-essentials-of-sap-commerce-cloud/impex-overview_aaae24a6-83e4-4ec5-8ff8-9149e361f9a5"
    url2 = "https://help.sap.com/docs/SAP_COMMERCE/d0224eca81e249cb821f2cdf45a82ace/8bee5297866910149854898187b16c96.html"
    url3 = "https://microlearning.opensap.com/media/An+Overview+of+ImpEx+-+SAP+Commerce-Cloud/1_frfj8asm"
    url_pdf = "../docs/world-war-2.pdf"


    query = "OMS Integration with SAP Commerce"

    urls = [url1, url2, url3]
    # urls = [url_pdf]

    results = run_rag(urls, query)


    print(f"\n\n RESULTS: {results}")
