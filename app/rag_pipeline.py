import os
import pickle
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

VECTOR_DIR = "data/vectorstore"
INDEX_PATH = os.path.join(VECTOR_DIR, "faiss_index.pkl")

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


def build_vectorstore(texts):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    docs = []
    for text in texts:
        chunks = splitter.split_text(text)
        docs.extend([Document(page_content=c) for c in chunks])

    vectorstore = FAISS.from_documents(docs, embedding_model)

    os.makedirs(VECTOR_DIR, exist_ok=True)
    with open(INDEX_PATH, "wb") as f:
        pickle.dump(vectorstore, f)


def load_vectorstore():
    if not os.path.exists(INDEX_PATH):
        return None
    with open(INDEX_PATH, "rb") as f:
        return pickle.load(f)


def rag_tool(query):
    vectorstore = load_vectorstore()
    if not vectorstore:
        return None

    docs = vectorstore.similarity_search(query, k=3)

    if not docs:
        return None

    return "\n\n".join(d.page_content for d in docs)

