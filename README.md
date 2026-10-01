# 📄 Multimodal Document RAG & Citation Engine

[![CI Pipeline](https://github.com/asad-mj/multimodal-doc-rag/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/asad-mj/multimodal-doc-rag/actions/workflows/ci-cd.yml)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?style=flat-square&logo=streamlit)](https://streamlit.io)
[![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-blue?style=flat-square)](https://trychroma.com)

An enterprise retrieval-augmented generation (RAG) platform that extracts unstructured paragraphs and structured financial/technical tables from complex PDFs, stores them in persistent vector collections, and synthesizes answers backed by page-level citations.

---

## 🏛️ System Architecture

```text
       ┌────────────────────────┐
       │   Complex PDF Upload   │
       └───────────┬────────────┘
                   │
         [Multimodal Parser]
        ┌──────────┴──────────┐
        ▼                     ▼
  Dense Paragraphs     Markdown Tables
        └──────────┬──────────┘
                   ▼
         [ChromaDB Vector Store]
                   │
           [User Query Input]
                   │
                   ▼
       [Hybrid Cosine Retrieval]
                   │
                   ▼
      [Auditable Page Citations + Grounded Response]
