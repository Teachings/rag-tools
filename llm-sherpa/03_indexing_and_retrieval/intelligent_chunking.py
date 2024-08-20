import os
import uuid
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

def intelligent_chunking(file_path: str) -> List[Document]:
    """Processes content from a file, chunks it, and generates embeddings."""
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
                print(colored(f"Chunk {i+1}: {chunk.to_context_text()[:200]}...", "cyan"))
                # Generate embedding
                generate_embedding(chunk.to_context_text())
            
            print(colored(f"Created corpus with {len(documents)} documents", "green"))
        
        if not content:
            print(colored(f"No content to append to corpus", "red"))
        
        return documents
    
    except Exception as e:        
        print(colored(f"Error processing file {file_path}: {str(e)}", "red"))
        traceback.print_exc()
        return [Document(page_content=f"Error processing file: {file_path}", metadata={"source": file_path})]

def index_and_rank(corpus: List[Document], query: str, top_percent: float = 60) -> List[Dict[str, str]]:
    print(colored(f"\n\nStarting indexing and ranking with Chroma DB for {len(corpus)} documents\n\n", "green"))

    collection_name = "test_documents_collection"

    try:
        # Initialize Chroma collection
        existing_collections = chroma_client.list_collections()
        if collection_name in [col.name for col in existing_collections]:
            print(f"Collection '{collection_name}' already exists. Deleting the existing collection.")
            chroma_client.delete_collection(name=collection_name)
        print("Creating new Chroma collection")
        collection = chroma_client.get_or_create_collection(name=collection_name)

        # Embed and store each document (chunk) using the generate_embedding function
        for i, doc in enumerate(corpus):
            try:
                embedding = generate_embedding(doc.page_content)
                collection.add(
                    ids=[f"chunk_{i}"],  # Unique ID for each chunk
                    embeddings=[embedding],
                    metadatas=[doc.metadata],
                    documents=[doc.page_content],
                )
                print(colored(f"Indexed document {i+1}/{len(corpus)}", "green"))
            except Exception as e:
                print(colored(f"Error embedding and storing document {i+1}: {str(e)}", "red"))
                traceback.print_exc()

        print(colored(f"Total documents indexed in Chroma DB: {len(corpus)}", "green"))

        # Perform the similarity search using the same embedding function
        query_embedding = generate_embedding(query)
        results = collection.query(query_embeddings=[query_embedding], n_results=40)

        # Extract individual chunks and their metadata and distances
        passages = []
        for idx, (doc, metadata, distance) in enumerate(zip(results["documents"], results["metadatas"], results["distances"])):
            try:
                passage = {
                    "id": idx + 1,
                    "text": doc if isinstance(doc, str) else doc[0],  # Ensure doc is treated as string
                    "meta": metadata[0] if isinstance(metadata, list) else metadata,  # Handle metadata as single item
                    "score": distance if isinstance(distance, float) else distance[0],  # Handle score as single float
                }
                passages.append(passage)
                print(colored(f"Retrieved document {idx+1}: {passage['text'][:200]}... | Score: {passage['score']}", "cyan"))
            except Exception as e:
                print(colored(f"Error processing search result: {str(e)}", "red"))
                traceback.print_exc()

        # Sort results by score in descending order
        sorted_results = sorted(passages, key=lambda x: x['score'], reverse=True)

        # Calculate the number of results to return based on the top_percent parameter
        num_results = max(2, int(len(sorted_results) * (top_percent / 100)))
        final_results = sorted_results[:num_results]

        print(colored(f"\n\nReturned top {top_percent}% of results ({len(final_results)} documents)\n\n", "green"))

        return final_results

    except Exception as e:
        print(colored(f"Error in indexing and ranking with Chroma DB: {str(e)}", "red"))
        traceback.print_exc()
        return [{"text": "Error in indexing and ranking", "meta": {"source": "unknown"}, "score": 0.0}]

if __name__ == "__main__":
    file_path = "test_document.txt"
    query = "test document"
    
    # Chunk the document and generate embeddings
    corpus = intelligent_chunking(file_path)
    
    # Index and rank the documents
    results = index_and_rank(corpus, query)
    
    print(f"\n\nFinal Results: {results}")
