import streamlit as st
import tempfile
import os
from src.parser import MultimodalDocumentParser
from src.vectorstore import VectorStoreManager
from src.rag_pipeline import MultimodalRAGPipeline

st.set_page_config(
    page_title="Multimodal Document RAG",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Multimodal Enterprise Document RAG")
st.markdown("Query dense PDFs, financial balance sheets, and technical manuals with **auditable, page-level citations**.")

@st.cache_resource
def load_engine():
    vector_store = VectorStoreManager()
    pipeline = MultimodalRAGPipeline(vector_store)
    parser = MultimodalDocumentParser()
    return parser, vector_store, pipeline

parser, vector_store, pipeline = load_engine()

# Sidebar: File Upload
with st.sidebar:
    st.header("📥 Ingestion Center")
    uploaded_file = st.file_uploader("Upload Target PDF", type=["pdf"])
    
    if uploaded_file and st.button("Ingest Document"):
        with st.spinner("Extracting text and tables..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            chunks = parser.parse_pdf(tmp_path)
            added = vector_store.add_chunks(chunks)
            os.remove(tmp_path)
            st.success(f"Successfully indexed {added} chunks from {uploaded_file.name}!")

# Main Panel: Query Interface
user_query = st.text_input("Enter your research question or prompt:", placeholder="What are the key financial performance metrics mentioned?")

if st.button("Generate Grounded Answer", type="primary") and user_query:
    with st.spinner("Executing similarity search & context synthesis..."):
        res = pipeline.run(query=user_query)

        st.subheader("💡 Synthesized Answer")
        st.write(res.answer)

        col1, col2 = st.columns(2)
        col1.metric("Confidence Score", f"{res.confidence_score * 100:.1f}%")
        col2.metric("Retrieved Chunks", res.retrieved_chunks)

        if res.citations:
            st.subheader("📚 Verified Source Citations")
            for idx, cit in enumerate(res.citations, start=1):
                with st.expander(f"Citation #{idx}: {cit.source_document} — Page {cit.page_number} (Match: {cit.relevance_score * 100:.1f}%)"):
                    st.code(cit.content_snippet, language="markdown")
