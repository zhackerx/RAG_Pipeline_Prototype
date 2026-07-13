# RAG Pipeline Flow Diagram

This document explains what the current solution does and how requests move through the system.

## What The Solution Does

- Exposes a FastAPI backend for uploading documents and asking questions.
- Supports PDF and Markdown ingestion.
- Splits documents into chunks.
- Generates embeddings using Google Gemini embeddings.
- Stores vectors and metadata in ChromaDB.
- On chat queries, retrieves top-k similar chunks and sends context + question to Gemini LLM.
- Returns the generated answer with source file/page references.

## High-Level Architecture

```mermaid
flowchart LR
    A[Client] --> B[FastAPI app]
    B --> C[Upload Controller]
    B --> D[Chat Controller]

    C --> E[DocumentService]
    E --> F[PDFLoader / MarkdownLoader]
    E --> G[ChunkingService]
    E --> H[VectorDbService]
    H --> I[ChromaDB]
    H --> J[Gemini Embedding Model]

    D --> K[RAGService]
    K --> H
    K --> L[LLMService]
    L --> M[PromptBuilder]
    L --> N[Gemini LLM]

    I --> K
```

## Industry-Guideline Advisory Flow (Requested)

```mermaid
flowchart LR
    A[User Details PDF] --> B[Knowledge Base]
    C[Bank Guidelines PDF/Excel] --> B
    B --> D[Domain Router]
    D --> E[Contextual RAG]
    E --> F[LLM/ML Evaluator]
    F --> G[User Dashboard]

    D --> H[Hierarchical Taxonomy by Industry]
    E --> I[Vector Search on Guideline Chunks]
    F --> J[Credit Risk Assessment LOW/MEDIUM/HIGH]
```

This is implemented through:

- `Document role` metadata (`guideline` vs `applicant`) on upload.
- `Industry` metadata tagging for guideline uploads.
- `DomainRouterService` industry extraction from applicant PDF text.
- `RiskAssessmentService` retrieval of matching guideline chunks.
- `LLMService.generate_risk_assessment` for structured scoring.

## Document Upload / Indexing Flow

```mermaid
flowchart TD
    A[POST /documents/upload/pdf or /documents/upload/markdown] --> B[upload_controller]
    B --> C[Save uploaded file to ./uploads]
    C --> D[DocumentService.upload_pdf or upload_markdown]
    D --> E[Generate document_id UUID]
    E --> F[Copy file to uploads with document_id prefix]

    F --> G{File Type}
    G -->|PDF| H[PDFLoader.load pages]
    G -->|Markdown| I[MarkdownLoader.load text]

    H --> J[ChunkingService.chunk_pages]
    I --> K[ChunkingService.chunk_text]
    J --> L[Attach document_id to each chunk]
    K --> L

    L --> M[VectorDbService.insert_chunks]
    M --> N[Create metadata: document_id, source, page, chunk_id, file_type, uploaded_at]
    N --> O[Chroma.add_texts]
    O --> P[Persist vectors in Chroma storage]

    P --> Q[Return document_id, source, chunk count]
```

## Chat / Retrieval-Augmented Generation Flow

```mermaid
flowchart TD
    A[POST /chat with question] --> B[chat_controller]
    B --> C[RAGService.ask_question]

    C --> D[retrieve_context question]
    D --> E[VectorDbService.search_similar_chunks]
    E --> F[Chroma.similarity_search_with_score top_k]
    F --> G[Context chunks with metadata + score]

    G --> H[build_context concatenate chunk text]
    H --> I[LLMService.generate_response]
    I --> J[PromptBuilder.build_prompt context + question]
    J --> K[Gemini client.models.generate_content]
    K --> L[Answer text]

    G --> M[Extract sources file + page]
    L --> N[Assemble ChatResponse answer, sources, chunks_used]
    M --> N
    N --> O[Return HTTP 200 response]
```

## Other Endpoints

```mermaid
flowchart TD
    A[GET /documents] --> B[VectorDbService.list_documents]
    B --> C[Chroma.get metadatas]

    D[GET /documents/:document_id] --> E[VectorDbService.get_document]
    E --> F[Chroma.get where document_id]

    G[DELETE /documents/:document_id] --> H[DocumentService.delete_document]
    H --> I[VectorDbService.delete_document]
    I --> J[Chroma.delete where document_id]

    K[PUT /documents/:document_id] --> L[DocumentService.reindex_document]
    L --> M[Delete old vectors]
    M --> N[Re-run upload flow]
```

## Notes About Current Behavior

- `reindex_document` currently creates a new UUID through upload methods instead of preserving the requested `document_id`.
- `RAGService.ask_question` prints context and chunks to stdout for every query.
- `README.md` model names differ from `config/settings.py` defaults.
- `pyproject.toml` has no declared dependencies; runtime dependencies are in `requirements.txt`.
