# Architecture and Flow Diagrams

This file includes the requested architecture, process flow, and use case diagrams for the FSSAI-focused loan advisory prototype.

## 1) Architecture Diagram

```mermaid
flowchart TB
    subgraph UI[USER INTERFACE LAYER]
        A1[Bank Admin\nUpload Advisory]
        A2[MSME Requester\nSubmit Loan Form]
        A3[Bank Officer or Manager\nQuery Business and Policy]
    end

    subgraph API[CORE API AND ORCHESTRATION LAYER]
        B1[Advisory Ingestion API]
        B2[Application Receiver API]
        B3[Query Orchestrator API]
        B4[Data Validation and Processing Agent]
    end

    subgraph AIML[AI AND ML PROCESSING LAYER]
        C1[Document Parser and Chunking Engine]
        C2[Risk Labeling Model]
        C3[Context Retriever]
        C4[LLM Summarizer]
        C5[Embedding Model]
        C6[LLM Synthesis Engine]
        C7[Security Masking Layer\nPII and PHI Redaction]
    end

    subgraph DB[DATABASE LAYER]
        D1[(Vector DB\nAdvisory Chunks\nBusiness Summaries\nRisk Labels)]
    end

    A1 --> B1
    A2 --> B2
    A3 --> B3

    B1 --> B4
    B2 --> B4
    B3 --> B4

    B4 --> C7
    C7 --> C1
    C7 --> C2
    C7 --> C3

    C1 --> C5
    C5 --> D1
    C3 --> D1
    D1 --> C3

    C2 --> C6
    C3 --> C6
    C4 --> C6

    C6 --> A3
    C2 --> A2
```

## 2) Process Flow Diagram

```mermaid
flowchart LR
    U1[Admin uploads FSSAI guideline files] --> P1[Ingestion API]
    U2[MSME requester submits application form] --> P2[Application API]
    U3[Officer submits policy or business query] --> P3[Query API]

    P1 --> V[Validation and security masking]
    P2 --> V
    P3 --> V

    V --> D1[Parse and chunk content]
    D1 --> D2[Generate embeddings]
    D2 --> D3[Store in vector DB]

    V --> R1[Risk labeling evaluation]
    V --> R2[Retrieve guideline and business context]
    R2 --> D3
    D3 --> R2

    R1 --> S1[LLM synthesis and reason generation]
    R2 --> S1
    S1 --> O1[Dashboard response with score, reasons, citations]
```

## 3) Use Case Diagram

```mermaid
flowchart TB
    subgraph Actors
        UA[Bank Admin]
        UB[MSME Requester]
        UC[Bank Officer or Manager]
    end

    subgraph System[Loan Advisory System]
        U1((Upload FSSAI Guidelines))
        U2((Submit MSME Loan Application))
        U3((Run Risk Evaluation))
        U4((Query Policy and Business Context))
        U5((Review Summary with Citations))
        U6((Mask PII and PHI Data))
    end

    UA --> U1
    UB --> U2
    UB --> U3
    UC --> U4
    UC --> U5

    U1 --> U6
    U2 --> U6
    U4 --> U6
```

## Notes

- Scope is fixed to food processing and FSSAI guideline context.
- Security masking runs before indexing and before model evaluation.
- UI layer now directly supports all three personas.
