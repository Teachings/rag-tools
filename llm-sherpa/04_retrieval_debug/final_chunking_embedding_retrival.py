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
            # chroma_client.delete_collection(name=collection_name)
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
                print(colored("Error embedding and storing document {i+1}: {str(e)}", "red"))
                traceback.print_exc()

        print(colored(f"Total documents indexed in Chroma DB: {len(corpus)}", "green"))

        # Perform the similarity search using the same embedding function
        query_embedding = generate_embedding(query)
 
        results = collection.query(query_embeddings=[query_embedding], n_results=10)

        # Map results into the passage structure
        passages = []
        idx = 0
        for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
            idx = idx +1
            passage = {
                "id": idx,
                "text": doc,
                "meta": meta,
                "score": dist
            }
            passages.append(passage)
            print(colored(f"Retrieved document {idx}: {passage['text'][:200]}... | Score: {passage['score']}", "cyan"))
        
        # Sort results by score in descending order
        sorted_results = sorted(passages, key=lambda x: x['score'], reverse=True)

        # Calculate the number of results to return based on the top_percent parameter
        num_results = max(1, int(len(sorted_results) * (top_percent / 100)))
        print(colored(f"Number of results calculated by top_percent: {num_results} out of {len(sorted_results)} total results" , "green"))

        # Debug: Print out the sorted results with their scores before filtering
        # for i, result in enumerate(sorted_results):
        #     print(colored(f"Rank {i+1}: Text = {result['text'][:200]}... | Score = {result['score']}", "light_blue"))

        final_results = sorted_results[:num_results]

        print(colored(f"\n\nReturned top {top_percent}% of results ({len(final_results)} documents)\n\n", "green"))

        return final_results

    except Exception as e:
        print(colored(f"Error in indexing and ranking with Chroma DB: {str(e)}", "red"))
        traceback.print_exc()
        return [{"text": "Error in indexing and ranking", "meta": {"source": "unknown"}, "score": 0.0}]

if __name__ == "__main__":
    # file_path = "test_document.txt"
    file_path = "../docs/world-war-2.pdf"

    query = "Dispute"
    
    # Chunk the document and generate embeddings
    corpus = intelligent_chunking(file_path)
    
    # Index and rank the documents
    results = index_and_rank(corpus, query)
    
    print(f"\n\nFinal Results: {results}")
