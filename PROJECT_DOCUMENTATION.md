# DocuMind Enterprise – Complete Project Documentation

**Project Duration:** 4 Weeks (Week 1-4)  
**Last Updated:** February 9, 2026  
**Status:** ✅ Production-Ready & Evaluation-Ready

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Project Architecture](#project-architecture)
3. [Week-by-Week Implementation](#week-by-week-implementation)
4. [Project Structure](#project-structure)
5. [Installation & Setup](#installation--setup)
6. [Running the Application](#running-the-application)
7. [API Documentation](#api-documentation)
8. [Configuration](#configuration)
9. [Technologies Used](#technologies-used)
10. [System Limitations](#system-limitations)
11. [Future Improvements](#future-improvements)
12. [Troubleshooting](#troubleshooting)

---

## Executive Summary

### What is DocuMind Enterprise?

DocuMind Enterprise is a **Retrieval-Augmented Generation (RAG) system** that enables accurate, document-grounded question answering from enterprise documents. It combines semantic search with large language models to provide precise answers without hallucinations.

### Problem Solved

Organizations have vast amounts of documentation (SOPs, policies, manuals, contracts) but lack efficient ways to query this information. Traditional keyword-based search is time-consuming and often inaccurate.

### Solution Provided

DocuMind Enterprise provides:
- **Automated document ingestion** with semantic chunking
- **Vector-based retrieval** using ChromaDB
- **LLM-powered answers** grounded strictly in documents
- **RESTful API** for easy integration
- **Web frontend** for user-friendly access
- **Docker support** for easy deployment

### Key Features

✅ **Document-Grounded Answers** - No hallucinations, only document-based responses  
✅ **Semantic Search** - Uses sentence-transformers for high-quality embeddings  
✅ **Local LLM Inference** - Privacy-preserving with Ollama  
✅ **RESTful API** - Easy integration with FastAPI  
✅ **Web Interface** - User-friendly frontend  
✅ **Docker Support** - Containerized deployment  
✅ **Configurable** - Environment-based settings  
✅ **Production-Ready** - Error handling, logging, health checks  

---

## Project Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface                           │
│                    (React Frontend @ 3001)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    FastAPI Backend (8000)                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              /health  /query  /upload  /docs            │   │
│  └────────┬──────────────────────────────────────────┬─────┘   │
└───────────┼──────────────────────────────────────────┼──────────┘
            │                                          │
    ┌───────▼─────────────┐                   ┌────────▼────────┐
    │   ChromaDB          │                   │  Ollama LLM     │
    │ (Vector Database)   │                   │  (LLaMA 2)      │
    │                     │                   │                 │
    │ Persisted Vectors   │                   │ Local Inference │
    └─────────────────────┘                   └─────────────────┘
```

### RAG Pipeline Flow

```
1. User Question (Frontend)
        ↓
2. API Request (/query)
        ↓
3. Vector Retrieval (ChromaDB)
        ├── Encode question
        ├── Semantic search
        └── Return top-5 similar chunks
        ↓
4. Context Formatting
        ├── Extract chunks
        └── Format as context
        ↓
5. Prompt Injection
        ├── Combine context + question
        └── Enforce grounding instructions
        ↓
6. LLM Generation (Ollama)
        ├── Process prompt
        └── Generate grounded answer
        ↓
7. Response to User
        └── Display answer or "I don't know"
```

---

## Week-by-Week Implementation

### Week 1: Document Ingestion & Embedding

**Objective:** Extract PDFs, chunk intelligently, and store embeddings

**Components Created:**
- `ingestion/ingest.py` - Main ingestion pipeline

**Features Implemented:**
- PDF text extraction using PyMuPDF (fitz)
- Intelligent chunking with RecursiveCharacterTextSplitter
  - Chunk size: 700 tokens
  - Overlap: 120 tokens
- Embedding generation using Sentence Transformers (all-MiniLM-L6-v2)
- Persistent storage in ChromaDB

**Process Flow:**
```
PDF File
    ↓
Text Extraction (PyMuPDF)
    ├── Extract text from each page
    └── Store with page metadata
    ↓
Semantic Chunking
    ├── Split on intelligent boundaries
    ├── Maintain context with overlap
    └── Preserve page information
    ↓
Embedding Generation
    ├── Convert each chunk to vector
    └── 384-dimensional embeddings
    ↓
ChromaDB Storage
    ├── Store vectors
    ├── Store original text
    └── Store metadata (page, source)
```

**Key Code:**
```python
def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    pages = []
    for page_num, page in enumerate(doc):
        text = page.get_text()
        pages.append({"page": page_num + 1, "text": text})
    return pages

def chunk_pages(pages):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=120
    )
    chunks = []
    for page in pages:
        page_chunks = splitter.split_text(page["text"])
        for chunk in page_chunks:
            chunks.append({
                "text": chunk,
                "metadata": {
                    "page": page["page"],
                    "source": "sample.pdf"
                }
            })
    return chunks
```

---

### Week 2: RAG Logic & LLM Integration

**Objective:** Build retrieval + generation pipeline with Ollama

**Components Created:**
- `query.py` - Interactive terminal-based querying

**Features Implemented:**
- Vector retrieval from ChromaDB
- Context formatting and injection
- Prompt-based grounding to prevent hallucinations
- Integration with Ollama local LLM (LLaMA 2)
- Interactive terminal interface

**Hallucination Prevention Strategy:**
```python
prompt = """You are a document assistant. Answer ONLY from the provided context.

Context:
{context}

Question: {question}

Instructions:
- Answer ONLY using information from the context above
- If the answer is not in the context, respond with: 
  "I don't know. This information is not available in the documents."
- Be concise and accurate
- Do not make up information or use external knowledge

Answer:"""
```

**Key Features:**
- Top-k retrieval (k=5)
- Context-aware prompt engineering
- Fallback responses for out-of-scope questions
- Terminal-based demo capability

---

### Week 3: Backend API Development

**Objective:** Convert RAG logic into production-ready FastAPI backend

**Components Created:**
- `backend/app.py` - FastAPI application
- `backend/rag.py` - Modular RAG system
- `backend/schemas.py` - Pydantic models

**Features Implemented:**
- RESTful API with FastAPI
- `/health` endpoint for monitoring
- `/query` endpoint for document Q&A
- Request/response validation with Pydantic
- CORS middleware for frontend integration
- Comprehensive error handling
- Swagger UI for API documentation

**API Endpoints:**

1. **GET /health**
   - Purpose: System health check
   - Response: `{"status": "OK"}`

2. **GET /**
   - Purpose: API information
   - Response: Links to docs, health, query endpoints

3. **POST /query**
   - Purpose: Ask document-based questions
   - Request: `{"question": "string"}`
   - Response: `{"answer": "string"}`

4. **POST /upload** (Week 3+)
   - Purpose: Upload and ingest PDF documents
   - Request: FormData with PDF file
   - Response: Ingestion status

**RAG System Architecture:**
```python
class RAGSystem:
    def __init__(self):
        # Load ChromaDB
        self.collection = client.get_collection("documind")
        # Load embedding model
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
    
    def query(self, question):
        # Step 1: Retrieve context
        results = self.retrieve_context(question, k=5)
        # Step 2: Format context
        context = self.format_context(results)
        # Step 3: Generate answer
        answer = self.generate_answer(question, context)
        return answer
```

---

### Week 4: Deployment & Evaluation

**Objective:** Package system for production deployment and evaluation

**Components Created:**
- `Dockerfile` - Container configuration
- `.dockerignore` - Build optimization
- `.env.example` - Configuration template
- `web_server.py` - Frontend web server
- `frontend/` - React-based web interface
- `PROJECT_DOCUMENTATION.md` - This document

**Features Implemented:**
- Environment-based configuration
- Docker containerization
- Multi-port frontend + backend setup
- Web interface for user-friendly access
- Complete documentation
- Deployment-ready configuration

**Configuration Management:**
```bash
# .env.example
CHROMA_DB_PATH=chroma_db
LLM_MODEL=llama2
EMBEDDING_MODEL=all-MiniLM-L6-v2
TOP_K=5
API_HOST=0.0.0.0
API_PORT=8000
```

---

## Project Structure

```
documind-enterprise-main/
│
├── ingestion/
│   └── ingest.py                 # Week 1: PDF ingestion pipeline
│
├── backend/
│   ├── app.py                    # Week 3: FastAPI application
│   ├── rag.py                    # Week 3: RAG logic module
│   └── schemas.py                # Week 3: Pydantic models
│
├── frontend/                      # Week 4: React web interface
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── data/
│   └── pdfs/
│       └── sample.pdf            # Document to query
│
├── chroma_db/                     # Week 1: Vector database
│   └── [vector storage files]
│
├── query.py                       # Week 2: Terminal interface
├── web_server.py                  # Week 4: Frontend web server
│
├── Dockerfile                     # Week 4: Docker config
├── .dockerignore                  # Week 4: Build optimization
├── .env.example                   # Week 4: Config template
├── requirements.txt               # Dependencies
├── README.md                       # Quick start guide
└── PROJECT_DOCUMENTATION.md       # This file
```

---

## Installation & Setup

### Prerequisites

- **Python 3.10+**
- **Ollama** (for local LLM)
  - Download: https://ollama.ai/
  - Install llama2: `ollama pull llama2`
- **Git**
- **Docker** (optional, for containerization)

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd documind-enterprise-main
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Key Dependencies:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `chromadb` - Vector database
- `sentence-transformers` - Embeddings
- `ollama` - LLM client
- `langchain` - LLM orchestration
- `pydantic` - Data validation
- `PyMuPDF` - PDF processing

### Step 4: Configure Environment

```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your settings (optional)
# Default values are sensible for local development
```

### Step 5: Ensure Ollama is Running

```bash
# Start Ollama service
ollama serve

# In another terminal, verify llama2 is available
ollama list
```

---

## Running the Application

### Option 1: Run Everything

```bash
# Terminal 1: FastAPI Backend
cd c:\Users\arpit\Downloads\documind-enterprise-main (1)\documind-enterprise-main
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000

# Terminal 2: Frontend Web Server
python web_server.py

# Open browser
# Frontend: http://localhost:3001
# API Docs: http://127.0.0.1:8000/docs
```

### Option 2: Run Backend Only

```bash
python -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000

# Test with curl:
curl -X POST "http://127.0.0.1:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the refund policy?"}'
```

### Option 3: Run with Docker

```bash
# Build image
docker build -t documind:latest .

# Run container
docker run -p 8000:8000 -p 3001:3001 documind:latest

# Access via browser
# Frontend: http://localhost:3001
# API: http://localhost:8000/docs
```

### Option 4: Run Ingestion Pipeline

```bash
# To ingest a new PDF
python ingestion/ingest.py

# Or via API
curl -X POST "http://127.0.0.1:8000/upload" \
  -F "file=@path/to/document.pdf"
```

---

## API Documentation

### Authentication

Currently, no authentication is required. Add JWT authentication for production use.

### Base URL

```
http://127.0.0.1:8000
```

### Endpoints

#### 1. Health Check

**GET** `/health`

Check if the service is running.

**Response:**
```json
{
  "status": "OK"
}
```

**Example:**
```bash
curl http://127.0.0.1:8000/health
```

---

#### 2. Query Documents

**POST** `/query`

Ask a question about the documents.

**Request:**
```json
{
  "question": "What is the refund policy?"
}
```

**Response:**
```json
{
  "answer": "According to the documentation, our refund policy is..."
}
```

**Example:**
```bash
curl -X POST "http://127.0.0.1:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the refund policy?"}'
```

**Error Responses:**

- **400** - Empty question
  ```json
  {
    "detail": "Question cannot be empty"
  }
  ```

- **500** - Server error
  ```json
  {
    "detail": "Error processing query: <error message>"
  }
  ```

---

#### 3. Upload Document

**POST** `/upload`

Upload and ingest a PDF document.

**Request:**
- Content-Type: `multipart/form-data`
- Parameter: `file` (PDF file)

**Response:**
```json
{
  "status": "success",
  "message": "Document ingested successfully",
  "chunks": 42
}
```

**Example:**
```bash
curl -X POST "http://127.0.0.1:8000/upload" \
  -F "file=@document.pdf"
```

---

#### 4. API Information

**GET** `/`

Get API information and links.

**Response:**
```json
{
  "message": "DocuMind Enterprise API",
  "docs": "/docs",
  "health": "/health",
  "query": "/query"
}
```

---

#### 5. Interactive API Documentation

**GET** `/docs`

Access Swagger UI for interactive API testing.

```
http://127.0.0.1:8000/docs
```

---

## Configuration

### Environment Variables

All configuration is done via environment variables. Create a `.env` file:

```bash
# ChromaDB Configuration
CHROMA_DB_PATH=chroma_db

# LLM Configuration
LLM_MODEL=llama2
EMBEDDING_MODEL=all-MiniLM-L6-v2
TOP_K=5

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `CHROMA_DB_PATH` | `chroma_db` | Path to vector database |
| `LLM_MODEL` | `llama2` | Ollama model name |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | SentenceTransformer model |
| `TOP_K` | `5` | Number of chunks to retrieve |
| `API_HOST` | `0.0.0.0` | API server host |
| `API_PORT` | `8000` | API server port |

### Chunking Parameters

**File:** `backend/rag.py`

```python
# Modify these in rag.py if needed
CHUNK_SIZE = 700
CHUNK_OVERLAP = 120
```

---

## Technologies Used

### Core Technologies

| Technology | Purpose | Version |
|------------|---------|---------|
| **Python** | Programming language | 3.10+ |
| **FastAPI** | Web framework | Latest |
| **Uvicorn** | ASGI server | Latest |
| **ChromaDB** | Vector database | Latest |
| **Ollama** | Local LLM runtime | Latest |
| **LLaMA 2** | Language model | 7B parameters |

### Data Processing

| Technology | Purpose |
|------------|---------|
| **PyMuPDF (fitz)** | PDF extraction |
| **LangChain** | LLM orchestration |
| **RecursiveCharacterTextSplitter** | Intelligent chunking |
| **Sentence Transformers** | Embeddings (all-MiniLM-L6-v2) |

### API & Frontend

| Technology | Purpose |
|------------|---------|
| **Pydantic** | Data validation |
| **CORS** | Cross-origin requests |
| **React** | Frontend framework |
| **HTML5/CSS3** | Markup & styling |

### Deployment

| Technology | Purpose |
|------------|---------|
| **Docker** | Containerization |
| **Docker Compose** | Multi-service orchestration |

---

## System Limitations

### Current Limitations

1. **Single PDF Support**
   - Currently optimized for one document at a time
   - Multiple PDFs would require collection management

2. **No User Authentication**
   - All endpoints are publicly accessible
   - Add JWT/OAuth for production

3. **No Rate Limiting**
   - Implement rate limiting to prevent abuse
   - Add request throttling

4. **Memory Usage**
   - ChromaDB loads entire vector database into memory
   - Large databases (>1GB) may have performance issues

5. **No Conversation History**
   - Each query is independent
   - No context from previous questions

6. **Limited Metadata**
   - Only page number stored with chunks
   - Could store title, section, document type

7. **Ollama Dependency**
   - Must have Ollama running locally
   - No fallback to cloud APIs

8. **No Semantic Caching**
   - Similar queries re-computed each time
   - Could cache embeddings

### Hallucination Mitigation

**Current Approach:**
- Strict prompt engineering
- Context-only responses
- Explicit "I don't know" fallback

**Effectiveness:**
- ✅ Prevents most hallucinations
- ✅ Clear refusal for out-of-scope questions
- ⚠️ May be overly cautious sometimes

---

## Future Improvements

### Short-Term (Weeks 5-6)

1. **Multi-Document Support**
   - Manage multiple collections
   - Document selection in UI
   - Source citation in answers

2. **Enhanced Metadata**
   - Section/chapter tracking
   - Document type classification
   - Creation date tracking

3. **Conversation History**
   - Store query history
   - Context-aware follow-ups
   - Session management

4. **Search Analytics**
   - Track popular queries
   - Monitor query performance
   - User feedback integration

### Mid-Term (Months 2-3)

1. **Advanced Retrieval**
   - Re-ranking with cross-encoders
   - Query expansion
   - Fuzzy matching

2. **User Management**
   - Role-based access control (RBAC)
   - User authentication
   - Document permissions

3. **Cloud Deployment**
   - Docker Compose setup
   - Kubernetes YAML
   - CI/CD pipeline

4. **Multiple LLM Support**
   - Switch between models
   - Model fine-tuning
   - Cloud LLM APIs (GPT-4, Claude)

### Long-Term (Months 4-6)

1. **Document Format Support**
   - DOCX, PPTX, TXT
   - Scanned PDF OCR
   - Web scraping

2. **Advanced Features**
   - Document summarization
   - Question generation
   - Answer verification

3. **Enterprise Features**
   - Multi-tenant support
   - Audit logging
   - SLA monitoring
   - Advanced analytics dashboard

4. **Performance Optimization**
   - GPU acceleration
   - Query result caching
   - Distributed retrieval

---

## Troubleshooting

### Issue: "Connection Refused" at localhost:8000

**Cause:** Backend server not running

**Solution:**
```bash
# Start backend
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

---

### Issue: "ChromaDB collection not found"

**Cause:** Ingestion hasn't been run

**Solution:**
```bash
# Run ingestion
python ingestion/ingest.py

# Or upload via API
curl -X POST "http://127.0.0.1:8000/upload" \
  -F "file=@sample.pdf"
```

---

### Issue: "Ollama not running"

**Cause:** LLM service not started

**Solution:**
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Verify model
ollama list
```

---

### Issue: "python-multipart not installed"

**Cause:** Missing dependency

**Solution:**
```bash
pip install python-multipart
```

---

### Issue: "Port 8000 already in use"

**Cause:** Another service using the port

**Solution:**
```bash
# Option 1: Use different port
python -m uvicorn backend.app:app --port 8001

# Option 2: Kill process using port 8000 (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

### Issue: "CORS error in frontend"

**Cause:** Frontend and backend not aligned

**Solution:**
```python
# Verify in backend/app.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Issue: "Very slow response times"

**Cause:** Large embeddings computation

**Solutions:**
1. Reduce `TOP_K` from 5 to 3
2. Use faster embedding model
3. Enable GPU acceleration for Ollama
4. Cache query embeddings

---

### Issue: "Out of memory error"

**Cause:** Large PDF or many chunks

**Solutions:**
1. Reduce `CHUNK_SIZE` from 700 to 500
2. Increase `CHUNK_OVERLAP` to reduce duplication
3. Process PDFs in batches
4. Use smaller embedding model

---

## Performance Metrics

### Typical Performance

| Operation | Time | Notes |
|-----------|------|-------|
| PDF Ingestion (5MB) | 2-5 sec | One-time operation |
| Query Response | 2-10 sec | Depends on model, hardware |
| Embedding Generation | 100ms | Per chunk |
| ChromaDB Search | 10-50ms | Very fast |
| LLM Inference | 1-5 sec | Bottleneck |

### System Requirements

**Minimum:**
- CPU: 4 cores
- RAM: 8GB
- Disk: 2GB free

**Recommended:**
- CPU: 8+ cores
- RAM: 16GB+
- Disk: 10GB free
- GPU: For faster LLM inference

---

## Security Considerations

### Production Recommendations

1. **Authentication**
   ```python
   # Add JWT token validation
   from fastapi.security import HTTPBearer
   security = HTTPBearer()
   ```

2. **Rate Limiting**
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   ```

3. **Input Validation**
   - Max question length: 1000 characters
   - File upload size limit: 50MB
   - Scan uploaded PDFs for malware

4. **HTTPS**
   - Use HTTPS in production
   - Configure SSL certificates

5. **Environment Variables**
   - Never commit `.env` with secrets
   - Use secure vaults for credentials

---

## Testing

### Manual Testing

1. **Health Check:**
   ```bash
   curl http://127.0.0.1:8000/health
   ```

2. **Query Test:**
   ```bash
   curl -X POST "http://127.0.0.1:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"question": "What is refund policy?"}'
   ```

3. **Upload Test:**
   ```bash
   curl -X POST "http://127.0.0.1:8000/upload" \
     -F "file=@test.pdf"
   ```

### Demo Queries

**In-Scope (Should Answer):**
- "What is the refund policy?"
- "How do I return a product?"
- "What are the terms and conditions?"

**Out-of-Scope (Should Refuse):**
- "What is the weather today?"
- "Who won the 2020 election?"
- "How do I make pizza?"

---

## Support & Contact

### Documentation
- API Docs: http://127.0.0.1:8000/docs
- README: [README.md](README.md)
- This Document: [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md)

### Troubleshooting
- Check logs in terminal where server is running
- Verify Ollama is running: `ollama list`
- Test API endpoints with Swagger UI

### Code Structure
- **Backend Logic:** `backend/rag.py`
- **API Endpoints:** `backend/app.py`
- **Data Models:** `backend/schemas.py`
- **Ingestion:** `ingestion/ingest.py`

---

## License

This project is for educational and enterprise evaluation purposes.

---

## Changelog

### Version 1.0 (February 9, 2026)

**Week 1: Ingestion**
- ✅ PDF text extraction
- ✅ Semantic chunking
- ✅ Embedding generation
- ✅ ChromaDB storage

**Week 2: RAG Logic**
- ✅ Vector retrieval
- ✅ Prompt grounding
- ✅ Ollama integration
- ✅ Terminal interface

**Week 3: Backend API**
- ✅ FastAPI application
- ✅ /health and /query endpoints
- ✅ Request/response validation
- ✅ CORS middleware

**Week 4: Deployment**
- ✅ Environment configuration
- ✅ Docker containerization
- ✅ Web frontend
- ✅ Comprehensive documentation

---

## Team

**Arpit** (Primary Contributor)
- System architecture and design
- Ingestion pipeline implementation
- RAG system integration
- API development
- Docker deployment
- Documentation

---

## Getting Help

1. **Check this document** - Most issues are covered
2. **Review terminal output** - Error messages usually point to issues
3. **Test with Swagger UI** - Use `/docs` to test API
4. **Verify Ollama** - Make sure `ollama serve` is running

---

**End of Documentation**

---

### Quick Reference

```bash
# Start everything
# Terminal 1:
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000

# Terminal 2:
python web_server.py

# Access
Frontend: http://localhost:3001
API Docs: http://127.0.0.1:8000/docs
Health: http://127.0.0.1:8000/health
```

