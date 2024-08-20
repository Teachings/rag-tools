import os
import traceback
from typing import List, Dict
from termcolor import colored
from langchain.schema import Document
from llmsherpa.readers import LayoutPDFReader
from dotenv import load_dotenv
import requests
import chromadb
from chromadb.config import Settings

# Load environment variables from .env file if it exists
load_dotenv()

# Initialize Chroma client
chroma_client = chromadb.HttpClient(
    host="localhost",
    port=8085,
    settings=Settings()
)

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
        print(colored(f"Generated embedding for text: {text[:200]}... | Embedding Length: {len(embedding)}", "cyan"))
        return embedding
    except Exception as e:
        print(colored(f"Error generating embedding: {str(e)}", "red"))
        traceback.print_exc()
        return []

def retrieve_similar_documents(query: str, top_percent: float = 60) -> List[Dict[str, str]]:
    """Retrieve similar documents from the existing ChromaDB based on the query."""
    print(colored(f"\n\nStarting retrieval of similar documents from Chroma DB\n\n", "green"))

    collection_name = "test_documents_collection"

    try:
        # Get the existing Chroma collection
        collection = chroma_client.get_collection(name=collection_name)

        # Generate embedding for the query
        query_embedding = generate_embedding(query)
        
        # Perform the similarity search
        results = collection.query(query_embeddings=[query_embedding], n_results=10)

        # Map results into the passage structure
        passages = []
        idx = 0
        for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
            idx = idx + 1
            passage = {
                "id": idx,
                "text": doc,
                "meta": meta,
                "score": dist
            }
            passages.append(passage)
            print(colored(f"Retrieved document {idx}: {passage['text']} | Score: {passage['score']}", "cyan"))
        
        # Sort results by score in descending order
        sorted_results = sorted(passages, key=lambda x: x['score'], reverse=True)

        # Calculate the number of results to return based on the top_percent parameter
        num_results = max(1, int(len(sorted_results) * (top_percent / 100)))
        print(colored(f"Number of results calculated by top_percent: {num_results} out of {len(sorted_results)} total results", "green"))

        final_results = sorted_results[:num_results]

        print(colored(f"\n\nReturned top {top_percent}% of results ({len(final_results)} documents)\n\n", "green"))

        return final_results

    except Exception as e:
        print(colored(f"Error in retrieving similar documents from Chroma DB: {str(e)}", "red"))
        traceback.print_exc()
        return [{"text": "Error in retrieving documents", "meta": {"source": "unknown"}, "score": 0.0}]

if __name__ == "__main__":
    query = "impex script for oauth"

    # Retrieve similar documents without re-indexing
    results = retrieve_similar_documents(query)
    
    print(f"\n\nFinal Results: {results}")
