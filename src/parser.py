import os
import re
from typing import List
import pdfplumber
from pypdf import PdfReader
from src.schemas import DocumentChunk

class MultimodalDocumentParser:
    """Extracts unstructured text paragraphs and structured tables from PDFs."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Removes excessive whitespace while preserving semantic line breaks."""
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()

    def parse_pdf(self, file_path: str) -> List[DocumentChunk]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        chunks: List[DocumentChunk] = []
        filename = os.path.basename(file_path)

        with pdfplumber.open(file_path) as pdf:
            for page_idx, page in enumerate(pdf.pages, start=1):
                # 1. Structured Table Extraction
                tables = page.extract_tables()
                for table_idx, table in enumerate(tables):
                    if not table or len(table) < 2:
                        continue
                    # Convert raw table rows into readable Markdown representation
                    headers = [str(col).replace("\n", " ").strip() if col else f"Col_{i}" for i, col in enumerate(table[0])]
                    markdown_rows = [f"| {' | '.join(headers)} |", f"| {' | '.join(['---'] * len(headers))} |"]
                    for row in table[1:]:
                        clean_row = [str(cell).replace("\n", " ").strip() if cell else "-" for cell in row]
                        markdown_rows.append(f"| {' | '.join(clean_row)} |")
                    
                    table_content = "\n".join(markdown_rows)
                    chunks.append(
                        DocumentChunk(
                            chunk_id=f"{filename}_p{page_idx}_tbl{table_idx}",
                            source_document=filename,
                            page_number=page_idx,
                            content_type="table",
                            content=table_content
                        )
                    )

                # 2. Dense Narrative Text Extraction
                raw_text = page.extract_text()
                if raw_text:
                    cleaned = self.clean_text(raw_text)
                    # Break long pages into dense paragraph blocks (~500 chars)
                    paragraphs = [p.strip() for p in cleaned.split("\n\n") if len(p.strip()) > 30]
                    for para_idx, para in enumerate(paragraphs):
                        chunks.append(
                            DocumentChunk(
                                chunk_id=f"{filename}_p{page_idx}_txt{para_idx}",
                                source_document=filename,
                                page_number=page_idx,
                                content_type="text",
                                content=para
                            )
                        )

        return chunks
