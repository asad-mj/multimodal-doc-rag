import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from src.config import settings
from src.parser import MultimodalDocumentParser
from src.vectorstore import VectorStoreManager
from src.rag_pipeline import MultimodalRAGPipeline
from src.schemas import QueryRequest, QueryResponse, IngestResponse

os.makedirs(settings.STORAGE_DIR, exist_ok=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise Multimodal Document RAG engine parsing text and tables with grounded citations."
)

parser = MultimodalDocumentParser()
vector_store = VectorStoreManager()
pipeline = MultimodalRAGPipeline(vector_store)

@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

@app.post("/ingest", response_model=IngestResponse, tags=["Document Operations"])
async def ingest_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF documents are supported.")

    dest_path = os.path.join(settings.STORAGE_DIR, file.filename)
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        chunks = parser.parse_pdf(dest_path)
        indexed_count = vector_store.add_chunks(chunks)
        
        pages_detected = len(set(c.page_number for c in chunks)) if chunks else 0
        return IngestResponse(
            filename=file.filename,
            total_pages=pages_detected,
            extracted_chunks=indexed_count,
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@app.post("/query", response_model=QueryResponse, tags=["RAG Inference"])
def execute_rag_query(payload: QueryRequest):
    return pipeline.run(query=payload.query, top_k=payload.top_k or 4)
