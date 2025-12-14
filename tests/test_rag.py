"""Tests for RAG knowledge base implementation"""

import pytest
from src.rag.knowledge_base import KnowledgeBase
from src.config.settings import settings


class TestKnowledgeBaseInitialization:
    """Test knowledge base initialization"""

    def test_knowledge_base_init(self):
        """Test that knowledge base initializes without errors"""
        kb = KnowledgeBase()
        assert kb is not None
        assert kb.settings is not None
        assert kb.embeddings is not None

    def test_knowledge_base_path_exists(self):
        """Test that knowledge base path is configured correctly"""
        kb = KnowledgeBase()
        assert kb.kb_path.exists()
        assert kb.kb_path.is_dir()

    def test_embeddings_configured(self):
        """Test that Ollama embeddings are configured"""
        kb = KnowledgeBase()
        assert kb.embeddings is not None
        assert kb.settings.ollama_embedding_model is not None
        assert kb.settings.ollama_base_url is not None


class TestDocumentLoading:
    """Test document loading functionality"""

    def test_load_documents(self):
        """Test loading documents from knowledge base directory"""
        kb = KnowledgeBase()
        documents = kb._load_documents()

        assert len(documents) > 0, "Should load at least one document"
        assert len(documents) >= 4, "Should load all 4 knowledge base files"

    def test_document_metadata(self):
        """Test that documents have proper metadata"""
        kb = KnowledgeBase()
        documents = kb._load_documents()

        for doc in documents:
            assert "source" in doc.metadata
            assert "path" in doc.metadata
            assert doc.metadata["source"].endswith(".md")

    def test_document_content_not_empty(self):
        """Test that documents have content"""
        kb = KnowledgeBase()
        documents = kb._load_documents()

        for doc in documents:
            assert len(doc.page_content) > 0
            assert len(doc.page_content) > 100, "Documents should have substantial content"


class TestDocumentChunking:
    """Test document chunking functionality"""

    def test_chunk_documents(self):
        """Test that documents are properly chunked"""
        kb = KnowledgeBase()
        documents = kb._load_documents()
        chunked = kb._chunk_documents(documents)

        assert len(chunked) > len(documents), "Chunking should create more items than original documents"
        assert all(len(chunk.page_content) <= settings.rag_chunk_size * 2 for chunk in chunked), \
            "Chunks should respect size limit (with some tolerance)"

    def test_chunk_metadata_preserved(self):
        """Test that metadata is preserved during chunking"""
        kb = KnowledgeBase()
        documents = kb._load_documents()
        chunked = kb._chunk_documents(documents)

        for chunk in chunked:
            assert "source" in chunk.metadata, "Chunk should preserve source metadata"


class TestDocumentIngestion:
    """Test document ingestion into vector store"""

    def test_ingest_documents(self):
        """Test ingesting documents into ChromaDB"""
        kb = KnowledgeBase()
        count = kb.ingest_documents()

        assert count > 0, "Should ingest at least one document"
        assert count >= 4, "Should ingest all knowledge base files"

    def test_vector_store_initialized(self):
        """Test that vector store is initialized after ingestion"""
        kb = KnowledgeBase()
        kb.ingest_documents()

        assert kb.vector_store is not None, "Vector store should be initialized"


class TestDocumentRetrieval:
    """Test document retrieval from knowledge base"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup knowledge base before each test"""
        self.kb = KnowledgeBase()
        self.kb.ingest_documents()

    def test_query_returns_results(self):
        """Test that queries return relevant documents"""
        results = self.kb.query("return policy 30 days")

        assert len(results) > 0, "Query should return results"
        assert len(results) <= self.kb.settings.rag_top_k

    def test_query_with_custom_top_k(self):
        """Test query with custom top_k parameter"""
        results = self.kb.query("return policy", top_k=1)

        assert len(results) == 1, "Should return exactly 1 result with top_k=1"

    def test_query_relevance(self):
        """Test that retrieved documents are relevant"""
        results = self.kb.query("return policy electronics")

        assert len(results) > 0
        # Check that results mention relevant keywords
        content = " ".join(doc.page_content.lower() for doc in results)
        assert any(keyword in content for keyword in ["return", "electronics", "policy", "days"])

    def test_empty_query_handling(self):
        """Test handling of empty or None queries"""
        results = self.kb.query("")
        # Should handle gracefully
        assert isinstance(results, list)


class TestPolicyContext:
    """Test policy context retrieval"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup knowledge base before each test"""
        self.kb = KnowledgeBase()
        self.kb.ingest_documents()

    def test_get_policy_context_time_exp(self):
        """Test getting policy context for TIME_EXP reason"""
        context = self.kb.get_policy_context("TIME_EXP")

        assert len(context) > 0
        assert "No policy information" not in context or "time" in context.lower() or "window" in context.lower()

    def test_get_policy_context_item_excl(self):
        """Test getting policy context for ITEM_EXCL reason"""
        context = self.kb.get_policy_context("ITEM_EXCL")

        assert len(context) > 0
        assert "No policy information" not in context or "final" in context.lower() or "sale" in context.lower()

    def test_get_policy_context_damaged(self):
        """Test getting policy context for DAMAGED_MANUAL reason"""
        context = self.kb.get_policy_context("DAMAGED_MANUAL")

        assert len(context) > 0

    def test_get_policy_context_returns_string(self):
        """Test that policy context returns string"""
        for reason in ["TIME_EXP", "ITEM_EXCL", "DAMAGED_MANUAL", "RISK_MANUAL"]:
            context = self.kb.get_policy_context(reason)
            assert isinstance(context, str)
            assert len(context) > 0


class TestCommunicationTemplates:
    """Test communication template retrieval"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup knowledge base before each test"""
        self.kb = KnowledgeBase()
        self.kb.ingest_documents()

    def test_get_approval_template(self):
        """Test retrieving approval communication template"""
        template = self.kb.get_communication_template("approval")

        assert len(template) > 0
        assert isinstance(template, str)

    def test_get_rejection_template(self):
        """Test retrieving rejection communication template"""
        template = self.kb.get_communication_template("rejection")

        assert len(template) > 0
        assert isinstance(template, str)

    def test_communication_template_returns_string(self):
        """Test that templates are returned as strings"""
        for scenario in ["approval", "rejection", "escalation"]:
            template = self.kb.get_communication_template(scenario)
            assert isinstance(template, str)
            assert len(template) > 0


class TestExceptionGuidance:
    """Test exception handling guidance retrieval"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup knowledge base before each test"""
        self.kb = KnowledgeBase()
        self.kb.ingest_documents()

    def test_get_damaged_guidance(self):
        """Test getting guidance for damaged items"""
        guidance = self.kb.get_exception_guidance("damaged")

        assert len(guidance) > 0
        assert isinstance(guidance, str)

    def test_get_fraud_guidance(self):
        """Test getting guidance for fraud prevention"""
        guidance = self.kb.get_exception_guidance("fraud")

        assert len(guidance) > 0
        assert isinstance(guidance, str)

    def test_exception_guidance_returns_string(self):
        """Test that exception guidance returns string"""
        for exception in ["damaged", "fraud", "compassionate"]:
            guidance = self.kb.get_exception_guidance(exception)
            assert isinstance(guidance, str)
            assert len(guidance) > 0


class TestHealthCheck:
    """Test knowledge base health check"""

    def test_health_check_after_init(self):
        """Test health check after initialization"""
        kb = KnowledgeBase()
        # Might fail if vector store not ingested yet
        health = kb.health_check()
        # Just verify it returns a boolean
        assert isinstance(health, bool)

    def test_health_check_after_ingest(self):
        """Test health check after document ingestion"""
        kb = KnowledgeBase()
        kb.ingest_documents()
        health = kb.health_check()

        assert health is True, "Health check should pass after ingestion"

    def test_health_check_returns_boolean(self):
        """Test that health check returns boolean"""
        kb = KnowledgeBase()
        result = kb.health_check()
        assert isinstance(result, bool)
