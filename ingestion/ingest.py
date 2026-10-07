import os
import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(BASE_DIR, "..")
PDF_PATH = os.path.join(PROJECT_ROOT, "data", "pdfs", "sample.pdf")
CHROMA_DB_PATH = os.path.join(PROJECT_ROOT, "chroma_db")


def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    pages = []

    for page_num, page in enumerate(doc):
        text = page.get_text()
        pages.append({
            "page": page_num + 1,
            "text": text
        })

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


def store_embeddings(chunks):
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    
    # Delete existing collection if it exists
    try:
        client.delete_collection(name="documind")
    except:
        pass
    
    collection = client.create_collection(name="documind")

    model = SentenceTransformer("all-MiniLM-L6-v2")

    for i, chunk in enumerate(chunks):
        embedding = model.encode(chunk["text"]).tolist()

        collection.add(
            ids=[str(i)],
            documents=[chunk["text"]],
            metadatas=[chunk["metadata"]],
            embeddings=[embedding]
        )

    return collection


# 🔴 THIS FUNCTION WAS MISSING OR NOT DEFINED PROPERLY
def search(collection, query):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    return results


if __name__ == "__main__":
    print("Starting PDF ingestion...")
    pages = extract_text(PDF_PATH)
    print(f"Extracted {len(pages)} pages from PDF")
    
    chunks = chunk_pages(pages)
    print(f"Created {len(chunks)} chunks")
    
    collection = store_embeddings(chunks)
    print("Embeddings stored successfully in 'chroma_db' directory")

    results = search(collection, "refund policy")

    print("\n--- SEARCH RESULT ---\n")
    print(results["documents"][0])
    print(results["metadatas"][0])
    print("\nIngestion complete! You can now run query.py to ask questions.")
