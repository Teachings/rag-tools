import os
import traceback
from typing import List, Dict, Optional
from termcolor import colored
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import requests
import chromadb
from chromadb.config import Settings

# Load environment variables from the .env file
load_dotenv()

# Configuration Section
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
EMBEDDING_MODEL = "mxbai-embed-large"
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8085))
CHROMA_SETTINGS = Settings()

# Initialize the Chroma client to connect to the Chroma DB server
chroma_client = chromadb.HttpClient(
    host=CHROMA_HOST,
    port=CHROMA_PORT,
    settings=CHROMA_SETTINGS
)

def extract_text_from_pdf(file_path: str) -> str: 
    """Extract all text from a PDF file using PyPDF2."""
    try:
        reader = PdfReader(file_path)
        text = "".join([page.extract_text() for page in reader.pages])
        print(colored(f"Extracted text from {len(reader.pages)} pages in {file_path}", "green"))
        return text
    except Exception as e:
        print(colored(f"Error extracting text from PDF {file_path}: {str(e)}", "red"))
        traceback.print_exc()
        return ""

def intelligent_chunking(file_path: str) -> List[Document]:
    """Extract, split, and convert PDF text into chunks with embeddings."""
    try:
        print(colored(f"\nProcessing content from file: {file_path}\n", "green"))
        
        # Step 2
        input(colored("Step 2: \n We are about to extract all the text from the PDF file using PyPDF2. \n This will allow us to process the content for further analysis. \n Press Enter to continue...", "yellow"))

        # Extract text from the PDF
        content = extract_text_from_pdf(file_path)

        # Step 3
        input(colored("Step 3: \n The text has been extracted. \n Now, we will split this text into smaller, manageable chunks. \n This is essential because it allows us to process the document in segments, \n making it easier to handle large texts and more effective for embedding generation. \n Press Enter to continue...", "yellow"))

        # Split the text into manageable chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1024,
            chunk_overlap=50,
            separators=["\n\n", "\n", " ", ". ", ""]
        )
        chunks = splitter.split_text(content)

        print(colored("Text has been split into chunks.", "green"))


        # Step 4
        input(colored("Step 4: \n We will now create Document objects from these chunks, \n which will include metadata about the source file. \n This step prepares the chunks for embedding generation and indexing. \n Press Enter to continue...", "yellow"))

        # Create documents from the chunks
        documents = [Document(page_content=chunk, metadata={"source": file_path}) for chunk in chunks]

        # Log the created chunks
        for i, doc in enumerate(documents):
            print(colored(f"Chunk {i+1}: {doc.page_content[:200]}...", "cyan"))

        print(colored(f"Created {len(documents)} documents", "green"))
        return documents
    
    except Exception as e:        
        print(colored(f"Error processing file {file_path}: {str(e)}", "red"))
        traceback.print_exc()
        return [Document(page_content=f"Error processing file: {file_path}", metadata={"source": file_path})]

def generate_embedding(text: str) -> List[float]:
    """Generate an embedding for the given text using the Ollama server."""
    try:
        response = requests.post(
            f"{OLLAMA_API_URL}/api/embeddings",
            json={"model": EMBEDDING_MODEL, "prompt": text}
        )
        response.raise_for_status()
        embedding = response.json().get("embedding")
        print(colored(f"Generated embedding for text: {text[:200]}... | Embedding Length: {len(embedding)}", "cyan"))
        return embedding
    except Exception as e:
        print(colored(f"Error generating embedding: {str(e)}", "red"))
        traceback.print_exc()
        return []

def index_documents(documents: List[Document], collection_name: str, delete: Optional[bool] = False):
    """Index document chunks in Chroma DB."""
    try:
        print(colored(f"\nStarting indexing with Chroma DB for {len(documents)} documents\n", "green"))

        # Step 5 is skipped in this version
        input(colored("Step 5: \n We access the ChromaDB collection where we want to store the embeddings. \n Press Enter to continue...", "yellow"))


        # Access or create the collection
        print(colored(f"Accessing Chroma Collection '{collection_name}'", "green"))
        collection = chroma_client.get_or_create_collection(name=collection_name)

        # Step 6
        input(colored("Step 6: \n We will now generate embeddings for each chunk of text and index them in the Chroma DB collection. \n These embeddings represent the text in a vector format,  \n which is essential for similarity search and retrieval later. \n Press Enter to continue...", "yellow"))

        # Embed and store each document (chunk) in the collection
        for i, doc in enumerate(documents):
            try:
                embedding = generate_embedding(doc.page_content)
                collection.add(
                    ids=[f"chunk_{i}"],  # Unique ID for each chunk
                    embeddings=[embedding],
                    metadatas=[doc.metadata],
                    documents=[doc.page_content],
                )
                print(colored(f"Indexed document {i+1}/{len(documents)}", "green"))
            except Exception as e:
                print(colored(f"Error embedding and storing document {i+1}: {str(e)}", "red"))
                traceback.print_exc()

        print(colored(f"Total documents indexed in Chroma DB: {len(documents)}", "green"))

    except Exception as e:
        print(colored(f"Error in indexing with Chroma DB: {str(e)}", "red"))
        traceback.print_exc()

def retrieve_text(query: str, collection_name: str, top_percent: float = 60) -> List[Dict[str, str]]:
    """Retrieve and rank documents from Chroma DB based on the query."""
    try:
        print(colored(f"\nStarting retrieval with Chroma DB for query: '{query}'\n", "green"))

        # Step 7
        input(colored("Step 7: \n We will now access the collection in Chroma DB and generate an embedding for the query text. \n This embedding will be compared against the embeddings of the stored documents to find the most similar ones. \n Press Enter to continue...", "yellow"))

        # Access the collection
        collection = chroma_client.get_collection(name=collection_name)

        # Generate the query embedding and perform similarity search
        query_embedding = generate_embedding(query)
        results = collection.query(query_embeddings=[query_embedding], n_results=10)

        # Step 8
        input(colored("Step 8: \n The similarity search is complete. \n Now, we will retrieve the top-ranked documents based on how closely they match the query embedding. \n These documents will be ranked by relevance, allowing us to see the most pertinent results. \n Press Enter to continue...", "yellow"))

        # Map results to a readable format
        passages = []
        for idx, (doc, meta, dist) in enumerate(zip(results["documents"][0], results["metadatas"][0], results["distances"][0]), start=1):
            passage = {
                "id": idx,
                "text": doc,
                "meta": meta,
                "score": dist
            }
            passages.append(passage)
            print(colored(f"Retrieved document {idx}: {passage['text'][:200]}... | Score: {passage['score']}", "cyan"))

        # Sort and return the top results based on the top_percent
        sorted_results = sorted(passages, key=lambda x: x['score'], reverse=True)
        num_results = max(1, int(len(sorted_results) * (top_percent / 100)))
        final_results = sorted_results[:num_results]

        return final_results

    except Exception as e:
        print(colored(f"Error in retrieval with Chroma DB: {str(e)}", "red"))
        traceback.print_exc()
        return [{"text": "Error in retrieval", "meta": {"source": "unknown"}, "score": 0.0}]

if __name__ == "__main__":
    # Example PDF file and collection name
    file_path = "../docs/world-war-2.pdf"
    collection_name = "test_documents_collection"

    # Step 1
    query = input(colored("Step 1: \n Please enter the search query you want to use for retrieving information from the documents. \n This query will be used to find the most relevant chunks of text in our indexed collection. \n Enter your query and press Enter to continue: \n ", "yellow"))

    top_percent = 60

    # Step 2: Chunk the document and generate embeddings
    documents = intelligent_chunking(file_path)
    
    # Step 3
    input(colored("Starting Indexing Phase: \n Chunks have been created. \n  Now, we'll index them in the Chroma DB.  \n Press Enter to continue...", "yellow"))

    # Step 4: Index the documents in the collection
    index_documents(documents, collection_name, delete=False)
    
    # Step 6
    input(colored("End Indexing Phase:  \n Indexing is complete.  \n Next, we'll retrieve documents based on the query you entered. \n Press Enter to continue...", "yellow"))

    # Step 7: Retrieve and rank the documents based on the query
    final_results = retrieve_text(query, collection_name, top_percent)

    print(colored(f"Returned top {top_percent}% of results ({len(final_results)} documents)\n", "green"))
