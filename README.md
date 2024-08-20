# PDF Embedding and Retrieval with ChromaDB

This repository contains a Python script that processes PDF documents, chunks their content, generates embeddings using a text embedding model, and stores these embeddings in ChromaDB. The script also allows for querying the stored embeddings to retrieve and rank relevant document chunks based on a user's query.

## Features

- **PDF Text Extraction**: Extracts text from PDF files using the `PyPDF2` library.
- **Intelligent Chunking**: Splits the extracted text into manageable chunks using `RecursiveCharacterTextSplitter`.
- **Embedding Generation**: Generates embeddings for each text chunk using a model from the Ollama server.
- **Document Indexing**: Indexes the generated embeddings in ChromaDB, a scalable vector search engine.
- **Query and Retrieval**: Performs similarity search on the indexed embeddings and retrieves relevant document chunks based on a query.

## Setup

### Prerequisites

- Conda (Anaconda or Miniconda)
- A running instance of ChromaDB
- Ollama server for embedding generation

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/Teachings/rag-tools.git
    cd rag-tools
    ```

2. Create and activate the Conda environment:
    ```bash
    conda create --name rag-tools python=3.8
    conda activate rag-tools
    ```

3. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the root directory to configure the following environment variables:
    ```bash
    OLLAMA_API_URL=http://localhost:11424  # URL of your Ollama server
    CHROMA_HOST=localhost                 # Host for ChromaDB
    CHROMA_PORT=8085                      # Port for ChromaDB
    ```

### Setting Up Chroma DB with Docker

#### **Step 1: Pull Chroma DB Docker Image**

   ```bash
   docker pull mukultripathi/chroma-db:latest
   ```

#### **Step 2: Create a Docker Volume for Persistent Storage**

To persist data across container restarts, create a Docker volume:
```bash
docker volume create chroma-db-data
```

#### **Step 3: Run Chroma DB Container**

Run the container with your custom image, ensuring persistent storage and automatic restarts:
```bash
docker run -d \
  --name chroma-db-instance \
  --network ollama-network \
  -p 8085:8000 \
  --restart always \
  -v chroma-db-data:/chroma/data \
  mukultripathi/chroma-db:latest
```

**Explanation**:
- `--name chroma-db-instance`: Assigns a name to the container for easy reference.
- `--network ollama-network`: Connects to the specified Docker network.
- `-p 8085:8000`: Maps port 8085 on the host machine to port 8000 inside the container, making the Chroma DB accessible via port 8085.
- `--restart always`: Ensures the container automatically restarts if it crashes or the Docker service restarts.
- `-v chroma-db-data:/chroma/data`: Mounts the Docker volume `chroma-db-data` to the `/chroma/data` directory inside the container, ensuring persistent storage of the Chroma DB data.

#### **Step 4: Verify the Container**

Ensure the container is running correctly:
```bash
docker ps
docker inspect chroma-db-instance
```

These commands will show the running container's status and details, including the mounted volume.

### Directory Structure

- **`docs/`**: This folder is where you should place your PDF files. The script will reference files from this directory when processing documents.

    ```
    ├── docs/
    │   ├── sample-document.pdf
    ```

### Usage

1. Place your PDF files in the `docs/` directory in the root of this repository.

2. Update the `file_path` in the script to reference the PDF file in the `docs/` directory. For example:
    ```python
    file_path = "./docs/sample-document.pdf"
    ```

3. Run the script:
    ```bash
    python script_name.py
    ```

4. The script will:
    - Extract text from the specified PDF.
    - Split the text into chunks.
    - Generate embeddings for each chunk.
    - Index the embeddings in ChromaDB.
    - Allow you to query the indexed data and retrieve relevant document chunks.

### Example

The following is a brief example of how to use the script:

```python
file_path = "./docs/sample-document.pdf"
collection_name = "sample_collection"
query = "What are the key events discussed in the document?"

# Step 1: Chunk the document and generate embeddings
documents = intelligent_chunking(file_path)

# Step 2: Index the documents in the collection
index_documents(documents, collection_name, delete=False)

# Step 3: Retrieve and rank the documents based on the query
results = retrieve_text(query, collection_name)
```

### Contribution

Feel free to open issues or submit pull requests if you find any bugs or have suggestions for new features.

### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
