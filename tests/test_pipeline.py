import pytest
from fastapi.testclient import TestClient
from main import app
from src.schemas import DocumentChunk
from src.vectorstore import VectorStoreManager
from src.rag_pipeline import MultimodalRAGPipeline

@pytest.fixture
def clean_pipeline(tmp_path):
    temp_dir = str(tmp_path / "chroma_test")
    vs = VectorStoreManager(persist_dir=temp_dir)
    pipe = MultimodalRAGPipeline(vs)
    return vs, pipe

def test_api_health():
    with TestClient(app) as client:
        res = client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"

def test_vectorstore_and_pipeline(clean_pipeline):
    vs, pipe = clean_pipeline
    sample_chunk = DocumentChunk(
        chunk_id="test_doc_p1_tbl1",
        source_document="report.pdf",
        page_number=1,
        content_type="table",
        content="| Metric | Value |\n| --- | --- |\n| Revenue | $50M |"
    )
    indexed = vs.add_chunks([sample_chunk])
    assert indexed == 1

    query_res = pipe.run("What is the revenue?", top_k=1)
    assert query_res.retrieved_chunks == 1
    assert query_res.confidence_score > 0.0
    assert query_res.citations[0].source_document == "report.pdf"
    assert query_res.citations[0].page_number == 1

def test_empty_knowledge_base(clean_pipeline):
    _, pipe = clean_pipeline
    res = pipe.run("What is quantum computing?", top_k=2)
    assert res.retrieved_chunks == 0
    assert res.confidence_score == 0.0
    assert len(res.citations) == 0
