# RAG Document Assistant

A production-ready Retrieval Augmented Generation backend built with FastAPI, Google Gemini, ChromaDB, and Python 3.11+.

## Features

- Upload PDF or Markdown documents
- Upload Excel guideline matrices (terms and score factors)
- Chunk and embed content
- Store embeddings in ChromaDB
- Query the indexed knowledge base with conversational RAG
- Return source references and page numbers when available
- Re-index and delete documents
- Industry-aware domain routing for guideline retrieval
- MSME risk scoring (LOW/MEDIUM/HIGH) for loan advisory support

## Project Structure

- app.py
- FLOW_DIAGRAM.md
- ARCHITECTURE_DIAGRAMS.md
- config/settings.py
- api/upload_controller.py
- api/chat_controller.py
- api/application_controller.py
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
- models/application_request.py
- chroma_storage/
- frontend/
- uploads/

## Architecture Overview

The backend follows a layered RAG pipeline:

- API layer (`app.py`, `api/*`) handles HTTP requests for upload and chat.
- Service layer (`services/*`) orchestrates ingestion, retrieval, and generation.
- Utility layer (`utils/*`) performs loading, chunking, embedding setup, and prompt building.
- Storage layer (ChromaDB in `./chroma_storage`) persists vectorized chunks and metadata.
- Model layer (Google Gemini) is used for both embeddings and final answer generation.

See the end-to-end flow here: [FLOW_DIAGRAM.md](FLOW_DIAGRAM.md)

Detailed architecture/process/use-case diagrams are available at [ARCHITECTURE_DIAGRAMS.md](ARCHITECTURE_DIAGRAMS.md)

## Environment Setup

Create a .env file in the project root:

```env
GEMINI_API_KEY=your_google_gemini_api_key
CHROMA_PATH=./chroma_storage
UPLOAD_DIR=./uploads
GUIDELINES_DIR=./guidelines
AUTO_INDEX_GUIDELINES=true
TARGET_INDUSTRY=food_processing
TARGET_GUIDELINE_STANDARD=fssai
ENABLE_DATA_MASKING=true
MASK_PII=true
MASK_PHI=true
```

## Internal Guideline Assumption

If all bank guidelines are internally available, place them under `./guidelines` and the app will auto-index them at startup.

See repository convention: [guidelines/README.md](guidelines/README.md)

## Current Prototype Scope

- Target segment: MSME Food Processing
- Guideline standard: FSSAI only
- Retrieval scope: only `document_role=guideline` and `industry=food_processing`

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

Open the role-based UI at:

- http://127.0.0.1:8000/

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

### Upload Guideline PDF (Industry Tagged)

```bash
curl -X POST "http://127.0.0.1:8000/documents/upload/pdf" \
  -F "file=@fssai_food_processing_guideline.pdf" \
  -F "document_role=guideline" \
  -F "industry=food_processing"
```

### Upload Guideline Excel (Industry Tagged)

```bash
curl -X POST "http://127.0.0.1:8000/documents/upload/excel" \
  -F "file=@fssai_scoring_matrix.xlsx" \
  -F "document_role=guideline" \
  -F "industry=food_processing"
```

### Chat

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"question":"What is covered in the uploaded documents?"}'
```

### MSME Risk Assessment (Applicant PDF)

```bash
curl -X POST "http://127.0.0.1:8000/assessment/upload/pdf" \
  -F "file=@msme_application.pdf"
```

### Prototype Risk Assessment (No PDF Required)

Use this for quick demos with sample data or existing Chroma guideline data.

```bash
curl -X POST "http://127.0.0.1:8000/assessment/prototype" \
  -H "Content-Type: application/json" \
  -d '{
    "industry": "food_processing",
    "applicant_profile": "Industry: Food Processing. FSSAI license renewal due in 20 days. Two minor hygiene non-conformities in last audit. Batch traceability available for 70 percent lots. Working capital cycle 135 days."
  }'
```

### MSME Application Receiver (JSON Form API)

```bash
curl -X POST "http://127.0.0.1:8000/application/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "business_name": "FreshHarvest Foods",
    "promoter_name": "Amit Sharma",
    "annual_turnover_crore": 3.2,
    "dscr": 1.08,
    "gst_delay_months": 2,
    "top_customer_revenue_percent": 52,
    "working_capital_days": 135,
    "existing_overdues_90_plus": false,
    "notes": "Two hygiene non-conformities found in last audit"
  }'
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
