import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from backend.schemas import QueryRequest, QueryResponse
from backend.rag import rag_system

# Load environment variables
load_dotenv()

# Configuration from environment
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Initialize FastAPI app
app = FastAPI(
    title="DocuMind Enterprise API",
    description="Document-grounded question answering system",
    version="1.0.0"
)

# Add CORS middleware for potential frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Frontend path
frontend_path = Path(__file__).parent.parent / "frontend"


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "OK"}


@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query the document database with a question.
    
    Returns a grounded answer based on the document context,
    or explicitly states when information is not available.
    """
    try:
        # Validate input
        if not request.question or not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Run RAG pipeline
        answer = rag_system.query(request.question)
        
        return QueryResponse(answer=answer)
    
    except Exception as e:
        # Handle errors gracefully
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF document to the knowledge base.
    File is saved to data/pdfs/ directory for ingestion.
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Create data/pdfs directory if it doesn't exist
        pdf_dir = Path(__file__).parent.parent / "data" / "pdfs"
        pdf_dir.mkdir(parents=True, exist_ok=True)
        
        # Save the uploaded file
        file_path = pdf_dir / file.filename
        content = await file.read()
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        return {
            "status": "success",
            "message": f"File '{file.filename}' uploaded successfully",
            "filename": file.filename,
            "size": len(content),
            "path": str(file_path),
            "note": "Run ingestion to add document to knowledge base"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint - serve frontend"""
    index_path = frontend_path / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {
        "message": "DocuMind Enterprise API",
        "docs": "/docs",
        "health": "/health",
        "query": "/query"
    }


@app.get("/{path:path}")
async def serve_static(path: str):
    """Serve static files (CSS, JS, etc)"""
    file_path = frontend_path / path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    # Return index.html for SPA routing
    index_path = frontend_path / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"error": "Not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT, reload=True)
