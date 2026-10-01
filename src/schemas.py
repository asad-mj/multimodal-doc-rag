from typing import List, Optional
from pydantic import BaseModel, Field

class DocumentChunk(BaseModel):
    chunk_id: str
    source_document: str
    page_number: int
    content_type: str = Field(..., description="text | table")
    content: str

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, description="Natural language prompt/question")
    top_k: Optional[int] = Field(4, ge=1, le=10)

class Citation(BaseModel):
    source_document: str
    page_number: int
    content_snippet: str
    relevance_score: float

class QueryResponse(BaseModel):
    query: str
    answer: str
    confidence_score: float
    citations: List[Citation]
    retrieved_chunks: int

class IngestResponse(BaseModel):
    filename: str
    total_pages: int
    extracted_chunks: int
    status: str
