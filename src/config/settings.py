"""Application configuration settings"""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Ollama Configuration
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Base URL for Ollama API",
    )
    ollama_model: str = Field(
        default="llama3.1:8b-instruct-q4_K_M",
        description="Ollama model name for agent",
    )
    ollama_embedding_model: str = Field(
        default="mxbai-embed-large:latest",
        description="Ollama embedding model for RAG",
    )

    # Database Configuration
    database_path: str = Field(
        default="data/order_return.db",
        description="Path to SQLite database file",
    )

    # ChromaDB Configuration
    chroma_persist_dir: str = Field(
        default="data/chroma_db",
        description="Directory for ChromaDB persistence",
    )
    chroma_collection_name: str = Field(
        default="order_return_kb",
        description="ChromaDB collection name",
    )

    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    # Application Configuration
    app_name: str = Field(
        default="Order Return Agent",
        description="Application name",
    )
    debug_mode: bool = Field(
        default=False,
        description="Enable debug mode",
    )

    # RAG Configuration
    rag_similarity_threshold: float = Field(
        default=0.7,
        description="Minimum similarity score for RAG retrieval",
    )
    rag_top_k: int = Field(
        default=3,
        description="Number of top documents to retrieve",
    )
    rag_chunk_size: int = Field(
        default=500,
        description="Size of text chunks for embedding",
    )
    rag_chunk_overlap: int = Field(
        default=50,
        description="Overlap between chunks",
    )

    # Agent Configuration
    agent_temperature: float = Field(
        default=0.0,
        description="LLM temperature for agent responses",
    )
    agent_max_iterations: int = Field(
        default=15,
        description="Maximum iterations for agent",
    )
    agent_max_execution_time: Optional[float] = Field(
        default=120.0,
        description="Maximum execution time in seconds",
    )

    def get_database_url(self) -> str:
        """Get SQLAlchemy database URL"""
        db_path = Path(self.database_path)
        return f"sqlite:///{db_path}"

    def get_chroma_path(self) -> Path:
        """Get ChromaDB persistence path"""
        return Path(self.chroma_persist_dir)

    def get_knowledge_base_path(self) -> Path:
        """Get knowledge base documents path"""
        return Path("data/knowledge_base")


# Global settings instance
settings = Settings()
