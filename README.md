# DocuMind Enterprise

An AI-powered document intelligence system that enables accurate question-answering from enterprise documents using Retrieval-Augmented Generation (RAG).

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Docker Deployment](#docker-deployment)
- [API Documentation](#api-documentation)
- [Demo Queries](#demo-queries)
- [Configuration](#configuration)
- [Limitations](#limitations)
- [Future Improvements](#future-improvements)

---

## Overview

DocuMind Enterprise is a production-ready RAG system designed for enterprise document processing. It ingests PDF documents, generates semantic embeddings, stores them in a vector database, and provides accurate answers to questions based strictly on document content.

### Problem Statement

Organizations have vast amounts of documentation (SOPs, policies, manuals) but lack efficient ways to query this information. Manual searching is time-consuming and error-prone.

### Solution

DocuMind Enterprise provides:
- **Automated document ingestion** with semantic chunking
- **Vector-based retrieval** for relevant context finding
- **LLM-powered answers** grounded strictly in documents
- **RESTful API** for easy integration

---

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   PDF       │      │   ChromaDB   │      │   Ollama    │
│ Documents   │──────▶│   Vector     │──────▶│   LLM       │
└─────────────┘      │   Database   │      │  (LLaMA 2)  │
                     └──────────────┘      └─────────────┘
                            │                      │
                            │                      │
                     ┌──────▼──────────────────────▼──────┐
                     │      FastAPI Backend               │
                     │  (Retrieval + Generation)          │
                     └────────────────────────────────────┘
```

### Pipeline Flow

1. **Ingestion**: PDFs → Text Extraction → Semantic Chunking → Embeddings → ChromaDB
2. **Retrieval**: User Question → Query Embedding → Top-K Similar Chunks
3. **Generation**: Context + Question → LLM → Grounded Answer

---

## Features

✅ **Document-Grounded Answers** - No hallucinations, only document-based responses  
✅ **Semantic Search** - Uses sentence-transformers for high-quality embeddings  
✅ **Local LLM** - Privacy-preserving inference with Ollama  
✅ **RESTful API** - Easy integration with FastAPI  
✅ **Docker Support** - Containerized deployment  
✅ **Configurable** - Environment-based configuration  

---

## Quick Start

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) installed with `llama2` model
- Git

### 1. Clone Repository

```bash
git clone <repository-url>
cd documind-enterprise-main
```

### 2. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env if needed
```

### 4. Ingest Documents

Place PDFs in `data/pdfs/` directory, then run:

```bash
python ingestion/ingest.py
```

### 5. Start Backend

```bash
python -m uvicorn backend.app:app --reload
```

### 6. Test API

Open your browser: http://localhost:8000/docs

---

## Installation

### Local Setup (Detailed)

#### Step 1: Install Ollama

Download from [https://ollama.ai/](https://ollama.ai/) and install the `llama2` model:

```bash
ollama pull llama2
```

#### Step 2: Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

#### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### Step 4: Verify Installation

```bash
python -c "import chromadb; import ollama; print('Setup successful!')"
```

---

## Usage

### Document Ingestion

```bash
# Add PDFs to data/pdfs/
python ingestion/ingest.py
```

Expected output:
```
Loaded 2 documents
Split into 42 chunks
Stored in ChromaDB successfully
```

### Running the Backend

```bash
python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

### Querying via API

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the eligibility criteria?"}'
```

### Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={"question": "What are the main policies?"}
)
print(response.json()["answer"])
```

---

## Docker Deployment

### Build Docker Image

```bash
docker build -t documind-enterprise .
```

### Run Container

```bash
docker run -d \
  --name documind \
  -p 8000:8000 \
  -v $(pwd)/chroma_db:/app/chroma_db \
  documind-enterprise
```

### Check Health

```bash
docker logs documind
curl http://localhost:8000/health
```

### Stop Container

```bash
docker stop documind
docker rm documind
```

---

## API Documentation

### Endpoints

#### `GET /health`
Health check endpoint

**Response:**
```json
{"status": "OK"}
```

#### `POST /query`
Query documents with a question

**Request Body:**
```json
{
  "question": "What is the vacation policy?"
}
```

**Response:**
```json
{
  "answer": "Based on the provided context, the vacation policy states..."
}
```

#### `GET /docs`
Interactive Swagger UI documentation

---

## Demo Queries

### ✅ In-Scope Questions (Answerable from Documents)

```bash
# Question 1: Policy Information
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the main policies covered in the documents?"}'

# Question 2: Specific Details
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the eligibility criteria for scholarships?"}'

# Question 3: Follow-up
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the penalty for false information?"}'
```

### ❌ Out-of-Scope Questions (Expected Refusal)

```bash
# Should return: "I don't know. This information is not available in the documents."
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the weather today?"}'

curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "Who is the president of the United States?"}'
```

---

## Configuration

### Environment Variables

All configuration is managed via environment variables (see [`.env.example`](.env.example)):

| Variable | Default | Description |
|----------|---------|-------------|
| `CHROMA_DB_PATH` | `chroma_db` | Path to ChromaDB storage |
| `LLM_MODEL` | `llama2` | Ollama model name |
| `TOP_K` | `5` | Number of context chunks to retrieve |
| `API_HOST` | `0.0.0.0` | API server host |
| `API_PORT` | `8000` | API server port |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence transformer model |

### Customization

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit values as needed:

```bash
LLM_MODEL=mistral
TOP_K=10
API_PORT=9000
```

---

## Limitations

### Current Limitations

1. **PDF Text Extraction**: Scanned PDFs without OCR are not supported
2. **Single Document Collection**: No multi-tenant support yet
3. **No Source Citations**: Answers don't include page references
4. **Ollama Dependency**: Requires local Ollama installation (not included in Docker)
5. **No Reranking**: Simple vector similarity, no reranking layer
6. **Limited File Formats**: Only PDF documents supported

### Known Issues

- Large documents (>100 pages) may cause slow ingestion
- Concurrent query handling not optimized
- No authentication or rate limiting

---

## Future Improvements

### Short-Term (Next Sprint)

- ✅ Add source citations with page numbers in responses
- ✅ Support batch PDF ingestion
- ✅ Implement query caching for performance
- ✅ Add logging and monitoring

### Mid-Term

- 🔄 Build web UI (Streamlit/React)
- 🔄 Add reranking layer for better retrieval
- 🔄 Support DOCX, PPTX file formats
- 🔄 Implement authentication and RBAC

### Long-Term

- 🔮 Multi-tenant architecture
- 🔮 Cloud deployment (AWS/Azure)
- 🔮 Fine-tuned embedding models
- 🔮 GraphRAG for complex queries

---

## Project Progress

### Week 1 – Ingestion
✅ PDF text extraction with PyMuPDF  
✅ Semantic chunking with LangChain  
✅ Embedding generation with sentence-transformers  
✅ Vector storage in ChromaDB  

### Week 2 – RAG Logic
✅ Vector retrieval implementation  
✅ Prompt engineering for grounding  
✅ Local LLM integration with Ollama  
✅ Git repository setup  

### Week 3 – Backend API
✅ FastAPI application structure  
✅ `/health` and `/query` endpoints  
✅ Request/response schemas with Pydantic  
✅ CORS middleware for frontend integration  

### Week 4 – Deployment (Current)
✅ Environment-based configuration  
✅ Docker containerization  
✅ Comprehensive documentation  
✅ Production readiness  

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

## License

This project is for educational and enterprise evaluation purposes.

---

## Support

For issues or questions, please refer to:
- API Documentation: http://localhost:8000/docs
- System Health: http://localhost:8000/health

---

**Built with ❤️ using LangChain, ChromaDB, Ollama, and FastAPI**Functional Enhancements

Context-aware question answering

Error handling for missing PDFs

Clean separation between ingestion and retrieval logic


Sample Prompt Behavior

Answers only from documents

Returns fallback response when information is unavailable

Team Contribution

Arpit (Primary Contributor)

Designed overall project architecture

Implemented ingestion and embedding pipeline

Integrated ChromaDB and LangChain

Managed GitHub repository and version control

Debugged environment, path, and permission issues

Team Support & Guidance

Conceptual discussions on RAG pipeline

Debugging assistance and architectural suggestions

Documentation and workflow optimization

Challenges Faced

Handling incorrect PDF paths

Differentiating scanned vs text-based PDFs

GitHub permission and remote URL conflicts

Managing large folders like venv and vectordb
Future Progress Plan

Short-Term (Week 3–4)

Add support for multiple PDFs ingestion

Improve chunking strategy

Enhance metadata storage

Implement source citation in answers


Mid-Term

Add web-based UI (Streamlit / React)

Role-based access for enterprise users

Improve retrieval accuracy using reranking


Long-Term

Support additional document formats (DOCX, PPTX)

Multi-user authentication

Deployment on cloud infrastructure

Enterprise-ready logging and monitoring
