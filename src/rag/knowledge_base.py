"""RAG knowledge base implementation using ChromaDB and Ollama embeddings"""

from pathlib import Path
from typing import Optional

from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from loguru import logger

from src.config.settings import settings


class KnowledgeBase:
    """
    RAG Knowledge Base for order return agent.

    Handles document ingestion, chunking, embedding, and retrieval
    using ChromaDB and Ollama embeddings.
    """

    def __init__(self):
        """Initialize the knowledge base with ChromaDB and embeddings"""
        self.settings = settings
        self.embeddings = OllamaEmbeddings(
            base_url=self.settings.ollama_base_url,
            model=self.settings.ollama_embedding_model,
        )
        self.vector_store: Optional[Chroma] = None
        self.kb_path = self.settings.get_knowledge_base_path()

        # Initialize the vector store
        self._initialize_vector_store()

    def _initialize_vector_store(self) -> None:
        """Initialize or load existing ChromaDB vector store"""
        persist_dir = self.settings.get_chroma_path()
        persist_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Try to load existing vector store
            self.vector_store = Chroma(
                collection_name=self.settings.chroma_collection_name,
                embedding_function=self.embeddings,
                persist_directory=str(persist_dir),
            )
            logger.info(f"Loaded existing vector store from {persist_dir}")
        except Exception as e:
            logger.warning(f"Could not load existing vector store: {e}")
            # Will create new one on ingest
            self.vector_store = None

    def ingest_documents(self) -> int:
        """
        Ingest all knowledge base documents into vector store.

        Loads markdown files from knowledge_base directory,
        chunks them, and stores embeddings in ChromaDB.

        Returns:
            Number of documents ingested
        """
        documents = self._load_documents()
        if not documents:
            logger.warning(f"No documents found in {self.kb_path}")
            return 0

        chunked_docs = self._chunk_documents(documents)
        self._store_vectors(chunked_docs)

        logger.info(f"Successfully ingested {len(documents)} documents with {len(chunked_docs)} chunks")
        return len(documents)

    def _load_documents(self) -> list[Document]:
        """
        Load markdown documents from knowledge base directory.

        Returns:
            List of Document objects
        """
        documents = []

        if not self.kb_path.exists():
            logger.warning(f"Knowledge base path does not exist: {self.kb_path}")
            return documents

        md_files = sorted(self.kb_path.glob("*.md"))
        logger.info(f"Found {len(md_files)} markdown files")

        for file_path in md_files:
            try:
                content = file_path.read_text(encoding="utf-8")
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": file_path.name,
                        "path": str(file_path),
                    },
                )
                documents.append(doc)
                logger.debug(f"Loaded document: {file_path.name} ({len(content)} chars)")
            except Exception as e:
                logger.error(f"Error loading document {file_path}: {e}")

        return documents

    def _chunk_documents(self, documents: list[Document]) -> list[Document]:
        """
        Split documents into chunks for embedding.

        Uses RecursiveCharacterTextSplitter with settings from config.

        Args:
            documents: List of Document objects to chunk

        Returns:
            List of chunked Document objects
        """
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.rag_chunk_size,
            chunk_overlap=self.settings.rag_chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""],
        )

        chunked_docs = []
        for doc in documents:
            chunks = splitter.split_documents([doc])
            chunked_docs.extend(chunks)
            logger.debug(f"Split {doc.metadata['source']} into {len(chunks)} chunks")

        return chunked_docs

    def _store_vectors(self, documents: list[Document]) -> None:
        """
        Store documents in ChromaDB vector store.

        Args:
            documents: List of Document objects to store
        """
        persist_dir = self.settings.get_chroma_path()
        persist_dir.mkdir(parents=True, exist_ok=True)

        self.vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            collection_name=self.settings.chroma_collection_name,
            persist_directory=str(persist_dir),
        )
        logger.info(f"Stored {len(documents)} chunks in ChromaDB")

    def query(self, query_text: str, top_k: Optional[int] = None) -> list[Document]:
        """
        Query the knowledge base for relevant documents.

        Args:
            query_text: The query string
            top_k: Number of top results (uses settings default if None)

        Returns:
            List of relevant Document objects
        """
        if self.vector_store is None:
            logger.warning("Vector store not initialized")
            return []

        k = top_k or self.settings.rag_top_k

        try:
            results = self.vector_store.similarity_search(
                query_text,
                k=k,
            )
            logger.debug(f"Query returned {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Error querying knowledge base: {e}")
            return []

    def get_policy_context(self, reason_code: str) -> str:
        """
        Get policy explanation for a specific eligibility reason code.

        Maps reason codes to policy queries and retrieves relevant context.

        Args:
            reason_code: Eligibility reason code (TIME_EXP, ITEM_EXCL, etc.)

        Returns:
            Policy context as formatted string
        """
        reason_queries = {
            "TIME_EXP": "return window policy time limit expiration",
            "ITEM_EXCL": "final sale items non-returnable restrictions",
            "DAMAGED_MANUAL": "damaged defective items escalation manual review",
            "RISK_MANUAL": "fraud prevention high return frequency manual escalation",
            "DATA_ERR": "missing order information data error",
        }

        query = reason_queries.get(reason_code, f"policy for {reason_code}")
        results = self.query(query, top_k=2)

        if not results:
            return f"No policy information found for {reason_code}"

        context = "\n\n---\n\n".join(doc.page_content for doc in results)
        return context

    def get_communication_template(self, scenario: str) -> str:
        """
        Get communication template for a specific scenario.

        Args:
            scenario: Communication scenario (e.g., "approval", "rejection", "escalation")

        Returns:
            Communication template
        """
        results = self.query(f"{scenario} response template communication", top_k=1)

        if not results:
            return f"No template found for {scenario}"

        return results[0].page_content

    def get_exception_guidance(self, exception_type: str) -> str:
        """
        Get guidance for handling specific exceptions or edge cases.

        Args:
            exception_type: Type of exception (e.g., "damaged", "compassionate")

        Returns:
            Exception handling guidance
        """
        results = self.query(f"{exception_type} exception handling edge case", top_k=2)

        if not results:
            return f"No guidance found for {exception_type} exception"

        context = "\n\n".join(doc.page_content for doc in results)
        return context

    def health_check(self) -> bool:
        """
        Check if knowledge base is properly initialized and accessible.

        Returns:
            True if healthy, False otherwise
        """
        try:
            if self.vector_store is None:
                logger.warning("Vector store not initialized")
                return False

            # Try a simple query
            results = self.vector_store.similarity_search("return policy", k=1)
            return len(results) > 0
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
