# RAG Document Assistant

A production-ready Retrieval Augmented Generation backend built with FastAPI, Google Gemini, ChromaDB, and Python 3.11+.

## Features

- Upload PDF or Markdown documents
- Chunk and embed content
- Store embeddings in ChromaDB
- Query the indexed knowledge base with conversational RAG
- Return source references and page numbers when available
- Re-index and delete documents

## Project Structure

- app.py
- config/settings.py
- api/upload_controller.py
- api/chat_controller.py
- services/vectorDbService.py
- services/ragService.py
- services/llmService.py
- services/documentService.py
- utils/vectorEmbeddingService.py
- utils/pdfLoader.py
- utils/markdownLoader.py
- utils/chunkingService.py
- utils/promptBuilder.py
- models/upload_request.py
- models/chat_request.py
- models/chat_response.py
- chroma_storage/
- uploads/

## Environment Setup

Create a .env file in the project root:

```env
GEMINI_API_KEY=your_google_gemini_api_key
CHROMA_PATH=./chroma_storage
UPLOAD_DIR=./uploads
```

## Install Dependencies

Using uv:

```bash
uv venv
uv pip install -r requirements.txt
```

## Run Locally

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## API Examples

### Upload PDF

```bash
curl -X POST "http://127.0.0.1:8000/documents/upload/pdf" \
  -F "file=@sample.pdf"
```

### Upload Markdown

```bash
curl -X POST "http://127.0.0.1:8000/documents/upload/markdown" \
  -F "file=@sample.md"
```

### Chat

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"question":"What is covered in the uploaded documents?"}'
```

### List Documents

```bash
curl "http://127.0.0.1:8000/documents"
```

### Delete Document

```bash
curl -X DELETE "http://127.0.0.1:8000/documents/{document_id}"
```

## ChromaDB Configuration

- Collection name: rag_documents
- Persist directory: ./chroma_storage

## Gemini Configuration

- Embedding model: models/text-embedding-004
- LLM model: gemini-2.5-pro
