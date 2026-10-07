import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_DB_PATH = os.path.join(BASE_DIR, "chroma_db")

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


db = Chroma(
    persist_directory=CHROMA_DB_PATH,
    embedding_function=embeddings
)


retriever = db.as_retriever(search_kwargs={"k": 5})
                            
prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are a helpful assistant that answers questions based on the provided context.
Use the information from the context to answer the question accurately.
If you cannot find the answer in the context, say "I don't know. This information is not available in the documents."

Context:
{context}

Question:
{question}

Answer:
"""
)


llm = Ollama(model="llama2")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)


while True:
    query = input("\nAsk a question (or type 'exit'): ")
    if query.lower() == "exit":
        break

    # Retrieve and display context for debugging
    docs = retriever.invoke(query)
    print("\n[DEBUG] Retrieved documents:")
    for i, doc in enumerate(docs):
        print(f"Doc {i+1}: {doc.page_content[:200]}...")
    
    result = rag_chain.invoke(query)
    print("\nAnswer:", result)