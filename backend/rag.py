import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import chromadb
import ollama

# Load environment variables
load_dotenv()

# Path configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(BASE_DIR, "..")

# Configuration from environment variables with defaults
CHROMA_DB_PATH = os.path.join(PROJECT_ROOT, os.getenv("CHROMA_DB_PATH", "chroma_db"))
LLM_MODEL = os.getenv("LLM_MODEL", "llama2")
TOP_K = int(os.getenv("TOP_K", "5"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")


class RAGSystem:
    def __init__(self):
        # Load the persisted ChromaDB
        try:
            self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
            self.collection = self.client.get_collection(name="documind")
            print(f"✓ ChromaDB loaded from {CHROMA_DB_PATH}")
        except Exception as e:
            print(f"⚠ Warning: Could not load ChromaDB: {e}")
            self.client = None
            self.collection = None
        
        # Load the same embedding model used during ingestion
        try:
            self.model = SentenceTransformer(EMBEDDING_MODEL)
            print(f"✓ Embedding model loaded: {EMBEDDING_MODEL}")
        except Exception as e:
            print(f"✗ Error loading embedding model: {e}")
            raise
    
    def retrieve_context(self, question: str, k: int = None):
        """Retrieve top-k relevant chunks from ChromaDB"""
        if k is None:
            k = TOP_K
        
        # Generate query embedding
        query_embedding = self.model.encode(question).tolist()
        
        # Query ChromaDB for similar documents
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )
        
        return results
    
    def format_context(self, results):
        """Format retrieved chunks into a single context string"""
        if not results["documents"] or not results["documents"][0]:
            return ""
        
        context_parts = []
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        
        for doc, meta in zip(documents, metadatas):
            page = meta.get("page", "unknown")
            context_parts.append(f"[Page {page}]\n{doc}")
        
        return "\n\n".join(context_parts)
    
    def generate_answer(self, question: str, context: str):
        """Generate answer using Ollama with strict prompt"""
        # Strict prompt to prevent hallucinations
        prompt = f"""You are a document assistant. Answer the question based ONLY on the provided context.

Context:
{context}

Question: {question}

Instructions:
- Answer ONLY using information from the context above
- If the answer is not in the context, respond with: "I don't know. This information is not available in the documents."
- Be concise and accurate
- Do not make up information or use external knowledge

Answer:"""
        
        # Call Ollama LLM
        response = ollama.chat(
            model=LLM_MODEL,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        return response["message"]["content"]
    
    def query(self, question: str):
        """Full RAG pipeline: retrieve + generate"""
        if not self.collection:
            return "Error: Vector database not initialized. Please ensure chroma_db exists and ingestion has been completed."
        
        # Step 1: Retrieve relevant context
        results = self.retrieve_context(question)
        
        # Step 2: Format context
        context = self.format_context(results)
        
        # Step 3: Generate answer (or return fallback if no context)
        if not context:
            return "I don't know. This information is not available in the documents."
        
        answer = self.generate_answer(question, context)
        
        return answer


# Singleton instance
rag_system = RAGSystem()
