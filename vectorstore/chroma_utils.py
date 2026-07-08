import os
import sys
import math
import sqlite3
from typing import List, Any
import pypdf
from langchain_core.documents import Document

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter


class SQLiteVectorStore:
    """
    A lightweight, SQLite-backed text search engine mimicking LangChain's Chroma vector store.
    Uses TF-IDF approximation / term frequency overlap for fast, 0-RAM retrieval without PyTorch.
    """
    def __init__(self, collection_name: str = "documents"):
        self.collection_name = collection_name
        self.db_path = "documents.db"
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    collection_name TEXT,
                    page_content TEXT,
                    source TEXT,
                    page INTEGER
                )
            """)
            conn.commit()
        finally:
            conn.close()

    def get(self) -> dict:
        """Mimics Chroma's get() method, returning all indexed records for the collection."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, page_content, source, page FROM documents WHERE collection_name = ?",
                (self.collection_name,)
            )
            rows = cursor.fetchall()
        finally:
            conn.close()

        ids = []
        documents = []
        metadatas = []
        for row in rows:
            ids.append(row[0])
            documents.append(row[1])
            metadatas.append({"source": row[2], "page": row[3]})
        return {"ids": ids, "documents": documents, "metadatas": metadatas}

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Mimics similarity_search using a TF-IDF approximation scoring system."""
        data = self.get()
        docs = data["documents"]
        metadatas = data["metadatas"]

        if not docs:
            return []

        # Tokenize query
        query_words = [w.lower().strip(",.?!()[]{}:;\"'") for w in query.split() if len(w) > 1]
        if not query_words:
            query_words = [query.lower()]

        # Simple inverse document frequency (IDF) calculation helper
        num_docs = len(docs)
        word_doc_counts = {}
        for qw in query_words:
            count = sum(1 for doc in docs if qw in doc.lower())
            word_doc_counts[qw] = count

        scores = []
        for doc_text, meta in zip(docs, metadatas):
            doc_lower = doc_text.lower()
            score = 0.0
            
            # Simple TF-IDF scoring formula
            for qw in query_words:
                tf = doc_lower.count(qw)
                if tf > 0:
                    # IDF with smoothing
                    doc_freq = word_doc_counts.get(qw, 0)
                    idf = math.log((1.0 + num_docs) / (1.0 + doc_freq)) + 1.0
                    # Length normalization factor
                    length_factor = 1.0 / (1.0 + math.log(1.0 + len(doc_text.split())))
                    score += tf * idf * length_factor

            scores.append((score, doc_text, meta))

        # Sort descending by score
        scores.sort(key=lambda x: x[0], reverse=True)

        results = []
        # Return top-k matching documents
        for score, text, meta in scores[:k]:
            results.append(Document(page_content=text, metadata=meta))
        return results

    @classmethod
    def from_documents(cls, documents: List[Document], embedding: Any, persist_directory: str, collection_name: str):
        """Mimics Chroma.from_documents by saving documents to the SQLite database."""
        store = cls(collection_name)
        
        conn = sqlite3.connect(store.db_path)
        try:
            cursor = conn.cursor()
            # Clear existing entries in this collection to match indexing overwrite behavior
            cursor.execute("DELETE FROM documents WHERE collection_name = ?", (collection_name,))
            
            # Insert each document chunk
            for idx, doc in enumerate(documents):
                doc_id = f"{collection_name}_{idx}_{hash(doc.page_content)}"
                source = doc.metadata.get("source", "Unknown Source")
                page = doc.metadata.get("page", 1)
                cursor.execute(
                    "INSERT OR REPLACE INTO documents (id, collection_name, page_content, source, page) VALUES (?, ?, ?, ?, ?)",
                    (doc_id, collection_name, doc.page_content, source, page)
                )
            conn.commit()
        finally:
            conn.close()
        return store


def index_pdf(file_path: str, collection_name: str = "documents") -> SQLiteVectorStore:
    """
    Extracts text from a PDF file page-by-page, splits the text into smaller chunks
    with page-tracking metadata, and stores them in the persistent SQLite text store.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The PDF file could not be found at: {file_path}")

    if os.path.getsize(file_path) == 0:
        raise ValueError(f"The PDF file '{file_path}' is empty (0 bytes).")

    try:
        reader = pypdf.PdfReader(file_path)
        num_pages = len(reader.pages)
    except Exception as e:
        raise ValueError(f"Failed to parse PDF file '{file_path}'. Details: {e}")

    if num_pages == 0:
        raise ValueError(f"The PDF file '{file_path}' contains zero pages.")

    documents: List[Document] = []
    source_filename = os.path.basename(file_path)

    for page_idx in range(num_pages):
        page_num = page_idx + 1
        try:
            page = reader.pages[page_idx]
            text = page.extract_text()
        except Exception as e:
            raise ValueError(f"Failed to extract text from page {page_num} in '{file_path}'. Details: {e}")

        if text and text.strip():
            documents.append(Document(
                page_content=text,
                metadata={
                    "source": source_filename,
                    "page": page_num
                }
            ))

    if not documents:
        raise ValueError(f"No readable text could be extracted from PDF file '{file_path}'.")

    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    chunks = text_splitter.split_documents(documents)

    if not chunks:
        raise ValueError("Text splitting resulted in zero chunks.")

    # Save to SQLite store
    db = SQLiteVectorStore.from_documents(
        documents=chunks,
        embedding=None,
        persist_directory=None,
        collection_name=collection_name
    )

    return db


def get_chroma_collection(collection_name: str = "documents") -> SQLiteVectorStore:
    """
    Retrieves the existing SQLite text store client wrapper for querying.
    Note: Keep the name 'get_chroma_collection' for backward compatibility.
    """
    return SQLiteVectorStore(collection_name=collection_name)


if __name__ == "__main__":
    test_pdf_path = "./test.pdf"
    collection_name = "documents"

    print("=== SQLite Text Store Verification Sandbox ===")
    
    # Simple check on get_chroma_collection
    try:
        db = get_chroma_collection(collection_name=collection_name)
        print("Successfully initialized SQLiteVectorStore.")
    except Exception as e:
        print(f"Failed initialization: {e}")
