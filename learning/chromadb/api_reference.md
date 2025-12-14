# ChromaDB & LangChain API Reference

This document contains official API documentation from Context7 for the libraries used in this project.

## Table of Contents

1. [LangChain ChromaDB Integration](#langchain-chromadb-integration)
2. [ChromaDB Python Client](#chromadb-python-client)
3. [LangChain Text Splitters](#langchain-text-splitters)
4. [Ollama Embeddings](#ollama-embeddings)

---

## LangChain ChromaDB Integration

### Import Statement

```python
from langchain_community.vectorstores import Chroma
```

**Note**: The project uses `langchain_community.vectorstores.Chroma` (not `langchain_chroma.Chroma`). This is the correct import for the current implementation.

### Initialize Chroma Vector Store

```python
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

# Create embeddings
embeddings = OllamaEmbeddings(
    base_url="http://localhost:11434",
    model="mxbai-embed-large:latest"
)

# Initialize vector store with persistence
vector_store = Chroma(
    collection_name="order_return_kb",
    embedding_function=embeddings,
    persist_directory="./data/chroma_db",  # Where to save data locally
)
```

### Create Vector Store from Documents

```python
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# Create from documents
vector_store = Chroma.from_documents(
    documents=documents,  # List of Document objects
    embedding=embeddings,
    collection_name="order_return_kb",
    persist_directory="./data/chroma_db",
)
```

### Similarity Search

```python
# Basic similarity search
results = vector_store.similarity_search(
    query="return policy electronics",
    k=3  # Number of results
)

# Results are Document objects with:
# - page_content: The text content
# - metadata: Dictionary with source information
```

---

## ChromaDB Python Client

### Persistent Client

```python
import chromadb

# Create persistent client (saves to disk)
client = chromadb.PersistentClient(path="./chroma_db")

# Get or create collection
collection = client.get_or_create_collection(name="order_return_kb")
```

### HTTP Client (Remote Server)

```python
import chromadb

# Connect to remote ChromaDB server
client = chromadb.HttpClient(
    host="localhost",
    port=8000
)

collection = client.get_or_create_collection(name="order_return_kb")
```

### Async Client (High Performance)

```python
import chromadb
import asyncio

async def main():
    # Create async client
    client = await chromadb.AsyncHttpClient(
        host="localhost",
        port=8000
    )

    # Async operations
    collection = await client.get_or_create_collection(name="async_docs")

    await collection.add(
        documents=["Document 1", "Document 2"],
        ids=["id1", "id2"]
    )

    results = await collection.query(
        query_texts=["search query"],
        n_results=5
    )

    return results

# Run async code
results = asyncio.run(main())
```

### Query Collection

#### Basic Query

```python
# Query with natural language
results = collection.query(
    query_texts=["What is a vector database?"],
    n_results=5,
    include=["documents", "metadatas", "distances"]
)

# Process results
for i, doc in enumerate(results["documents"][0]):
    distance = results["distances"][0][i]
    metadata = results["metadatas"][0][i]
    print(f"Result {i+1} (distance: {distance:.4f}):")
    print(f"  Document: {doc}")
    print(f"  Metadata: {metadata}")
```

#### Query with Metadata Filtering

```python
# Query with WHERE clause for metadata filtering
results = collection.query(
    query_texts=["machine learning concepts"],
    n_results=10,
    where={
        "$and": [
            {"source": {"$eq": "blog"}},
            {"year": {"$gte": 2023}}
        ]
    },
    where_document={"$contains": "neural network"}
)
```

#### Complex Filters

```python
# Complex metadata filtering with nested logical operators
results = collection.query(
    query_texts=["affordable laptops"],
    n_results=20,
    where={
        "$or": [
            {
                "$and": [
                    {"category": "electronics"},
                    {"price": {"$lte": 1000}},
                    {"rating": {"$gte": 4.0}}
                ]
            },
            {"featured": True}
        ]
    },
    include=["documents", "metadatas", "distances"]
)
```

#### Query by Specific IDs

```python
# Constrain search to specific document IDs
results = collection.query(
    query_embeddings=[[11.1, 12.1, 13.1], [1.1, 2.3, 3.2]],
    n_results=5,
    ids=["id1", "id2"]
)
```

### Add Documents

```python
# Add documents with metadata
collection.add(
    documents=["This is document1", "This is document2"],
    metadatas=[
        {"source": "notion"},
        {"source": "google-docs"}
    ],
    ids=["doc1", "doc2"],
    # embeddings are optional - will be generated if not provided
)
```

### Get Collection by ID

```python
# Get collection by ID
col = client.get_collection(id=collection_id)

# Verify properties
assert col.id == collection_id
assert col.name == "order_return_kb"
```

### List Collections

```python
# List all collections with pagination
collections = client.list_collections(
    limit=10,
    offset=0
)

for collection in collections:
    print(f"Collection: {collection.name} (ID: {collection.id})")
```

---

## LangChain Text Splitters

### RecursiveCharacterTextSplitter

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Create splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # Size of chunks
    chunk_overlap=50,    # Overlap between chunks
    separators=["\n\n", "\n", ".", " ", ""]  # Priority order
)

# Split text
texts = text_splitter.split_text(document)

# Split documents (preserves metadata)
documents = text_splitter.split_documents(documents)
```

**How it works**:
- Tries to split on larger units first (paragraphs, sentences)
- Falls back to smaller units (words, characters) if needed
- Maintains semantic coherence by prioritizing natural boundaries

### CharacterTextSplitter (Token-based)

```python
from langchain_text_splitters import CharacterTextSplitter

# Create splitter with token encoder
text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    encoding_name="cl100k_base",
    chunk_size=100,
    chunk_overlap=0
)

texts = text_splitter.split_text(document)
```

---

## Ollama Embeddings

### Initialize Ollama Embeddings

```python
from langchain_ollama import OllamaEmbeddings

# Create embeddings
embeddings = OllamaEmbeddings(
    base_url="http://localhost:11434",
    model="mxbai-embed-large:latest"
)
```

### Embed Query

```python
# Embed a single query string
query_embedding = embeddings.embed_query("return policy for electronics")
```

### Embed Documents

```python
# Embed multiple documents
documents = ["Document 1", "Document 2", "Document 3"]
document_embeddings = embeddings.embed_documents(documents)
```

---

## Document Object Structure

### LangChain Document

```python
from langchain_core.documents import Document

# Create document
doc = Document(
    page_content="The actual text content",
    metadata={
        "source": "return_policy.md",
        "path": "/path/to/return_policy.md",
        "custom_field": "value"
    }
)

# Access properties
content = doc.page_content
metadata = doc.metadata
source = doc.metadata.get("source")
```

---

## Query Result Structure

### LangChain Similarity Search Results

```python
results = vector_store.similarity_search("query", k=3)

# Results is a list of Document objects
for doc in results:
    print(doc.page_content)      # Text content
    print(doc.metadata)          # Metadata dictionary
```

### ChromaDB Query Results

```python
results = collection.query(
    query_texts=["query"],
    n_results=5,
    include=["documents", "metadatas", "distances"]
)

# Results structure:
# {
#     "ids": [["id1", "id2", ...]],           # List of lists (one per query)
#     "documents": [["doc1", "doc2", ...]],   # List of lists
#     "metadatas": [[{...}, {...}, ...]],     # List of lists
#     "distances": [[0.1, 0.3, ...]],        # List of lists (lower = more similar)
#     "embeddings": [[[...], [...], ...]]     # If included
# }

# Access first query's results
documents = results["documents"][0]
metadatas = results["metadatas"][0]
distances = results["distances"][0]
```

---

## Best Practices

### 1. Use Persistent Storage

```python
# Always specify persist_directory for production
vector_store = Chroma(
    collection_name="order_return_kb",
    embedding_function=embeddings,
    persist_directory="./data/chroma_db",  # Persistent storage
)
```

### 2. Preserve Metadata

```python
# Always include metadata when creating documents
doc = Document(
    page_content=content,
    metadata={
        "source": filename,
        "path": full_path,
        # Add any other relevant metadata
    }
)
```

### 3. Handle Errors Gracefully

```python
try:
    results = vector_store.similarity_search(query, k=3)
except Exception as e:
    logger.error(f"Query failed: {e}")
    results = []  # Return empty list as fallback
```

### 4. Health Checks

```python
# Always check if vector store is initialized
if vector_store is None:
    # Re-initialize or ingest documents
    pass

# Test with a simple query
try:
    test_results = vector_store.similarity_search("test", k=1)
    is_healthy = len(test_results) > 0
except:
    is_healthy = False
```

---

## References

- **LangChain Docs**: https://docs.langchain.com/oss/python/
- **ChromaDB Docs**: https://docs.trychroma.com/
- **Ollama**: https://ollama.ai/

---

**Last Updated**: Based on Context7 documentation (2025-12-14)
