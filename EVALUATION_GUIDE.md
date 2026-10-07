# DocuMind Enterprise - Evaluation Q&A Guide

This document prepares you for technical evaluation questions about the project.

---

## Architecture & Design Questions

### Q: Explain the high-level architecture of your system.

**Answer:**
DocuMind uses a three-stage RAG pipeline:

1. **Ingestion Stage**: PDFs are parsed with PyMuPDF, split into semantic chunks using RecursiveCharacterTextSplitter, embedded with Sentence Transformers (all-MiniLM-L6-v2), and stored in ChromaDB persistent vector database.

2. **Retrieval Stage**: User questions are embedded with the same model, ChromaDB performs semantic similarity search, and top-K (default 5) most relevant chunks are retrieved.

3. **Generation Stage**: Retrieved context is formatted with page metadata, combined with the question in a strict prompt, and sent to Ollama's LLaMA 2 model for grounded answer generation.

The system is exposed via FastAPI with endpoints for health checks and queries.

---

### Q: Why did you choose these specific technologies?

**Answer:**

- **ChromaDB**: Lightweight, embedded vector database with no separate server needed. Perfect for prototyping and small-to-medium deployments. Supports persistent storage.

- **Sentence Transformers**: State-of-the-art embeddings with good balance of quality and speed. all-MiniLM-L6-v2 is efficient (384 dimensions) and widely tested.

- **Ollama**: Enables local LLM inference without cloud dependencies. Critical for enterprise privacy. Easy to swap models.

- **FastAPI**: Modern Python framework with automatic API documentation, type validation via Pydantic, and excellent async support.

- **PyMuPDF**: Fast, reliable PDF text extraction with good handling of various PDF formats.

---

### Q: How do you prevent hallucinations?

**Answer:**
We use multiple strategies:

1. **Strict Prompting**: The system prompt explicitly instructs the LLM to answer ONLY from provided context and refuse when information is unavailable.

2. **Context Grounding**: We retrieve actual document chunks and include them in the prompt, making the answer traceable to source material.

3. **Fallback Logic**: If no relevant context is retrieved (empty results), we return a predefined refusal message without calling the LLM.

4. **Temperature Control**: Could be added (temperature=0) to reduce creativity, though not currently implemented.

**Limitation**: The LLM may still attempt to be helpful with general knowledge questions. Future improvement: add a question classification layer to detect out-of-scope queries before retrieval.

---

## Technical Implementation Questions

### Q: Walk me through what happens when a user submits a query.

**Answer:**

```python
# 1. Request arrives at FastAPI endpoint
POST /query {"question": "What are eligibility criteria?"}

# 2. Request validation (Pydantic)
QueryRequest model validates the question is non-empty

# 3. RAG system query method called
rag_system.query(question)

# 4. Question embedding
query_embedding = model.encode(question)  # 384-dim vector

# 5. Vector similarity search
results = chromadb.query(
    query_embeddings=[query_embedding],
    n_results=5  # TOP_K from env
)

# 6. Context formatting
context = format_context(results)  # Combine chunks with page numbers

# 7. LLM prompt construction
prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer ONLY from context..."

# 8. LLM inference
response = ollama.chat(model="llama2", messages=[...])

# 9. Response return
return {"answer": response["message"]["content"]}
```

Typical latency: 2-5 seconds depending on context size and LLM load.

---

### Q: How do you handle document chunking?

**Answer:**
We use LangChain's RecursiveCharacterTextSplitter:

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # Characters per chunk
    chunk_overlap=50,    # Overlap to preserve context
    separators=["\n\n", "\n", ". ", " "]  # Priority order
)
```

**Why these settings?**
- **500 chars**: Balance between semantic coherence and embedding quality
- **50 char overlap**: Prevents information loss at chunk boundaries
- **Separators**: Respects document structure (paragraphs > sentences > words)

**Metadata preservation**: Each chunk stores original page number for citation capability (not yet implemented in responses).

---

### Q: Explain your configuration management approach.

**Answer:**
We follow 12-factor app methodology:

1. **Environment Variables**: All config in `.env` file, loaded via python-dotenv
2. **Defaults**: Safe fallbacks in code (`os.getenv("VAR", "default")`)
3. **No Hardcoding**: All paths, model names, parameters are configurable
4. **Example Template**: `.env.example` documents all variables

**Benefits:**
- Different configs for dev/staging/prod without code changes
- Secrets management (API keys, DB URLs) without git commits
- Easy testing with different parameters
- Docker-friendly (environment variables in `docker run`)

**Variables:**
- `CHROMA_DB_PATH`: Database location
- `LLM_MODEL`: Ollama model name
- `TOP_K`: Retrieval results count
- `API_HOST` / `API_PORT`: Server binding
- `EMBEDDING_MODEL`: Sentence transformer model

---

## Deployment Questions

### Q: Why containerize with Docker?

**Answer:**

**Benefits:**
1. **Reproducibility**: Same environment everywhere (dev, staging, prod)
2. **Dependency Isolation**: No conflicts with system Python or other apps
3. **Portability**: Runs identically on Windows, Linux, Mac, cloud
4. **Scalability Foundation**: Easy to scale with Kubernetes or Docker Swarm
5. **Version Control**: Dockerfile is code, tracked in git

**Our Approach:**
- Python 3.10-slim base image (smaller size)
- Multi-stage potential (could optimize further)
- Health check endpoint for orchestration
- Volume mount for ChromaDB persistence

**Limitation**: Ollama not included in container due to size/complexity. Future: docker-compose with separate Ollama service.

---

### Q: How would you deploy this to production?

**Answer:**

**Short-term (Single Server):**
1. Deploy Docker container on cloud VM (AWS EC2, Azure VM)
2. Ollama on same VM or separate GPU instance
3. NGINX reverse proxy for SSL and load balancing
4. Mount ChromaDB to persistent volume
5. Environment-specific `.env` file
6. Monitoring with Prometheus/Grafana

**Long-term (Scalable):**
1. **API Layer**: Kubernetes cluster with multiple backend pods
2. **Vector DB**: Migrate to managed service (Pinecone, Weaviate) or self-hosted Qdrant cluster
3. **LLM Layer**: API-based LLM (OpenAI, Anthropic) or self-hosted vLLM cluster
4. **Caching**: Redis for frequently asked questions
5. **Queue**: Celery for async long-running queries
6. **Observability**: ELK stack for logging, APM for tracing

**Security Additions:**
- JWT authentication
- Rate limiting (per user/API key)
- Input sanitization
- HTTPS only
- API key rotation

---

## Evaluation & Testing Questions

### Q: How do you evaluate the quality of your RAG system?

**Answer:**

**Current (Manual):**
- Demo script with known questions
- Visual inspection of answers
- Out-of-scope refusal testing

**Production Approach Would Include:**

1. **Retrieval Metrics:**
   - MRR (Mean Reciprocal Rank): Is correct chunk in top-K?
   - NDCG (Normalized Discounted Cumulative Gain): Ranking quality
   - Recall@K: Coverage of relevant chunks

2. **Generation Metrics:**
   - BLEU/ROUGE: Overlap with reference answers
   - BERTScore: Semantic similarity to gold answers
   - Faithfulness: Does answer stay grounded in context?

3. **End-to-End:**
   - Human evaluation on sample queries
   - User feedback loop (thumbs up/down)
   - Answer latency tracking

4. **Test Set:**
   - 50-100 question-answer pairs from documents
   - Mix of easy/hard questions
   - Include negatives (unanswerable questions)

---

### Q: What are the system's limitations?

**Answer:**

**Current Limitations:**

1. **Document Support**:
   - PDF only (no DOCX, PPTX, HTML)
   - Scanned PDFs without OCR fail
   - Tables and images not extracted

2. **Retrieval**:
   - Simple semantic search, no hybrid (keyword + semantic)
   - No reranking layer
   - Fixed chunk size (not adaptive)

3. **Generation**:
   - No source citations in answers
   - Occasional helpfulness despite strict prompting
   - No multi-hop reasoning

4. **Scalability**:
   - Single collection (no multi-tenancy)
   - No caching
   - Synchronous processing only

5. **Production Readiness**:
   - No authentication
   - No rate limiting
   - Basic error handling
   - No comprehensive logging

---

### Q: What would you improve given more time?

**Answer:**

**Immediate (1-2 days):**
1. Add page number citations in answers
2. Implement query classification for better refusal
3. Add structured logging (JSON logs)
4. Improve error messages

**Short-term (1-2 weeks):**
1. Web UI with Streamlit or React
2. Reranking with cross-encoder
3. Query caching with Redis
4. Comprehensive test suite
5. API authentication (JWT)

**Medium-term (1 month):**
1. Hybrid search (BM25 + semantic)
2. Multiple document collections
3. Conversational memory (chat history)
4. Advanced chunking strategies
5. Monitoring dashboard

**Long-term (3+ months):**
1. Fine-tuned embedding model on domain
2. GraphRAG for relationship queries
3. Multi-modal support (images, tables)
4. Active learning from user feedback
5. Enterprise features (SSO, audit logs)

---

## Bonus Technical Questions

### Q: How would you handle a 1000-page document?

**Answer:**

**Challenges:**
- 1000 pages ≈ 500,000 words ≈ 1000 chunks
- Slow ingestion (embedding time)
- Large vector search space

**Solutions:**

1. **Hierarchical Chunking**:
   - Summarize each section
   - Two-stage retrieval: find relevant section → find relevant chunk

2. **Metadata Filtering**:
   - Store chapter/section metadata
   - User can specify scope: "Search in Chapter 3"

3. **Batch Processing**:
   - Async ingestion with progress tracking
   - Parallel embedding generation

4. **Index Optimization**:
   - Use HNSW index in ChromaDB (already default)
   - Consider dimension reduction if needed

---

### Q: What if the user's question requires information from multiple chunks?

**Answer:**

**Current**: TOP_K=5 retrieves multiple chunks, LLM synthesizes across them.

**Improvements:**

1. **Increase TOP_K**: More context (but watch token limits)
2. **Iterative Retrieval**: Multi-hop like:
   - Retrieve initial chunks
   - Generate sub-questions
   - Retrieve for each sub-question
   - Synthesize final answer

3. **MapReduce**:
   - Answer question on each chunk independently
   - Reduce answers into final summary

4. **GraphRAG**:
   - Build knowledge graph from documents
   - Use graph traversal for multi-hop reasoning

---

### Q: Security concerns with user queries?

**Answer:**

**Current Risks:**
1. **Prompt Injection**: User could try to manipulate system prompt
2. **Data Leakage**: All users see all documents
3. **DoS**: Long queries could overload system

**Mitigations:**

1. **Input Validation**:
   - Max query length (e.g., 500 chars)
   - Sanitize special characters
   - Rate limiting per IP/user

2. **Prompt Hardening**:
   - Separate system and user prompts
   - Use delimiters clearly marking user input
   - LangChain's PromptGuard

3. **Access Control**:
   - Document-level permissions
   - User authentication (JWT)
   - Audit logging of queries

4. **Resource Limits**:
   - Timeout on LLM calls
   - Circuit breaker pattern
   - Queue management

---

## Demonstration Tips

### What to Show:

1. **Architecture Diagram**: Walk through data flow
2. **Code Walkthrough**: Key files (rag.py, app.py)
3. **Live Demo**: 
   - Health check
   - In-scope question (good answer)
   - Follow-up question
   - Out-of-scope question (refusal)
4. **Swagger UI**: Show API docs
5. **Configuration**: Show `.env` flexibility
6. **Docker**: Build and run (if time permits)

### What to Highlight:

- ✅ Clean code structure
- ✅ Modular design
- ✅ Type hints and docstrings
- ✅ Configuration management
- ✅ Documentation quality
- ✅ Reproducibility

### Be Honest About:

- ⚠️ Out-of-scope handling imperfect
- ⚠️ No source citations yet
- ⚠️ Single-tenant only
- ⚠️ Room for improvement

---

## Conclusion

**Key Message**: DocuMind Enterprise is a solid, working RAG system demonstrating understanding of:
- Vector databases and embeddings
- Retrieval-augmented generation
- API design and deployment
- Configuration management
- Documentation and reproducibility

It's production-ready for small deployments and has clear path to enterprise scale.

---

**Good luck with your evaluation! 🚀**
