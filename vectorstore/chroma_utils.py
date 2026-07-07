import os
from typing import List, Any
import pypdf
from langchain_core.documents import Document

# Robust imports supporting older and newer LangChain versions
try:
    from langchain_chroma import Chroma
except ImportError:
    try:
        from langchain_community.vectorstores import Chroma
    except ImportError:
        from langchain.vectorstores import Chroma

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
    except ImportError:
        from langchain.embeddings import HuggingFaceEmbeddings


def index_pdf(file_path: str, collection_name: str = "documents") -> Chroma:
    """
    Extracts text from a PDF file page-by-page, splits the text into smaller chunks
    with page-tracking metadata, embeds them using HuggingFace all-MiniLM-L6-v2,
    and stores them in a persistent ChromaDB vector database.

    Args:
        file_path (str): Absolute or relative path to the PDF file.
        collection_name (str): Name of the Chroma collection. Defaults to "documents".

    Returns:
        Chroma: The persistent Chroma vector store containing the indexed chunks.

    Raises:
        FileNotFoundError: If the PDF file does not exist at file_path.
        ValueError: If the PDF file is corrupted, empty, has no pages, or contains no readable text.
        RuntimeError: If storing the chunks in ChromaDB fails.
    """
    # 1. Input Validation and Error Handling
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The PDF file could not be found at: {file_path}")

    # Check for empty file
    if os.path.getsize(file_path) == 0:
        raise ValueError(f"The PDF file '{file_path}' is empty (0 bytes).")

    try:
        reader = pypdf.PdfReader(file_path)
        num_pages = len(reader.pages)
    except Exception as e:
        raise ValueError(f"Failed to parse PDF file '{file_path}'. It may be corrupted or invalid. Details: {e}")

    if num_pages == 0:
        raise ValueError(f"The PDF file '{file_path}' contains zero pages.")

    # 2. Extract Text Page-by-Page
    documents: List[Document] = []
    source_filename = os.path.basename(file_path)

    for page_idx in range(num_pages):
        page_num = page_idx + 1
        try:
            page = reader.pages[page_idx]
            text = page.extract_text()
        except Exception as e:
            # We raise a ValueError to avoid silently skipping corrupted pages
            raise ValueError(f"Failed to extract text from page {page_num} in '{file_path}'. Details: {e}")

        # Only create a document if the page contains readable, non-whitespace text
        if text and text.strip():
            documents.append(Document(
                page_content=text,
                metadata={
                    "source": source_filename,
                    "page": page_num
                }
            ))

    if not documents:
        raise ValueError(
            f"No readable text could be extracted from PDF file '{file_path}'. "
            "It may consist purely of scanned images or have non-extractable text content."
        )

    # 3. Split Text into Chunks (preserving source and page metadata)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    chunks = text_splitter.split_documents(documents)

    if not chunks:
        raise ValueError("Text splitting resulted in zero chunks.")

    # 4. Initialize Embeddings Model (all-MiniLM-L6-v2)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 5. Store Chunks in a Persistent ChromaDB Collection
    persist_dir = "./chroma_db"
    try:
        db = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=persist_dir,
            collection_name=collection_name
        )
    except Exception as e:
        raise RuntimeError(f"Failed to store documents in Chroma collection '{collection_name}': {e}")

    return db


def get_chroma_collection(collection_name: str = "documents") -> Chroma:
    """
    Retrieves the existing Chroma vector store client/collection wrapper for querying later.

    Args:
        collection_name (str): Name of the Chroma collection to load. Defaults to "documents".

    Returns:
        Chroma: The LangChain Chroma vector store instance initialized with the collection.
    """
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    persist_dir = "./chroma_db"
    
    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_dir
    )


if __name__ == "__main__":
    import shutil
    import sys
    
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    
    test_pdf_path = "./test.pdf"
    collection_name = "documents"

    print("=== Chroma RAG Utils Test Sandbox ===")
    
    # Check if a test PDF exists
    if not os.path.exists(test_pdf_path):
        print(f"Warning: '{test_pdf_path}' not found.")
        print("To verify page numbers and indexing, a sample 'test.pdf' will be created dynamically.")
        
        # We can dynamically generate a simple PDF using pypdf itself, or warn the user.
        # Since generating PDFs is standard in reportlab, we try to create a basic test PDF if possible.
        try:
            # We can write a simple test PDF with multiple pages to test page tracking.
            # We use reportlab if it can be imported, else we print instructions.
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            
            print("Generating a test multi-page PDF using reportlab...")
            c = canvas.Canvas(test_pdf_path, pagesize=letter)
            
            # Page 1
            c.drawString(100, 750, "This is page one of our test document.")
            c.drawString(100, 700, "It contains some sample text to test our text chunking and splitting.")
            c.drawString(100, 650, "We want to make sure the vector database maps the chunk metadata to page 1.")
            c.showPage()
            
            # Page 2
            c.drawString(100, 750, "This is page two of the test document.")
            c.drawString(100, 700, "Here we have more sentences that will be split by the RecursiveCharacterTextSplitter.")
            c.drawString(100, 650, "Page boundaries are crucial for citation and referencing in RAG systems.")
            c.showPage()
            
            # Page 3
            c.drawString(100, 750, "This is page three of our test document.")
            c.drawString(100, 700, "Finally, we conclude the document with this page. Langchain's splitter will partition")
            c.drawString(100, 650, "all this text, and we expect page 3 to show up correctly in metadata.")
            c.showPage()
            
            c.save()
            print(f"Successfully generated a 3-page test PDF at '{test_pdf_path}'.")
        except ImportError:
            print("ReportLab is not installed, so we cannot generate 'test.pdf' automatically.")
            print("Please place a valid PDF file at './test.pdf' to run the test block.")
            
    if os.path.exists(test_pdf_path):
        # Clean up any existing test collection to ensure fresh test
        if os.path.exists("./chroma_db"):
            print("Clearing existing './chroma_db' directory for a clean run...")
            try:
                shutil.rmtree("./chroma_db")
            except Exception as e:
                print(f"Non-blocking warning: Failed to clean ./chroma_db: {e}")
                
        print(f"\nIndexing '{test_pdf_path}' into collection '{collection_name}'...")
        try:
            db = index_pdf(test_pdf_path, collection_name=collection_name)
            print("PDF indexed successfully!")
            
            # Retrieve collection using get_chroma_collection
            print("\nRetrieving the collection using get_chroma_collection...")
            retrieved_db = get_chroma_collection(collection_name=collection_name)
            
            # Fetch some content to print
            # Let's get the raw collection data using get() to show the first 3 chunks and their metadata
            results = retrieved_db.get()
            
            documents = results.get("documents", [])
            metadatas = results.get("metadatas", [])
            ids = results.get("ids", [])
            
            num_to_print = min(3, len(documents))
            print(f"\nSuccessfully retrieved {len(documents)} chunks from collection.")
            print(f"Printing the first {num_to_print} chunks to verify page numbers:")
            
            for i in range(num_to_print):
                print("-" * 50)
                print(f"Chunk ID: {ids[i]}")
                print(f"Metadata: {metadatas[i]}")
                content_to_print = documents[i].strip()
                try:
                    print(f"Content:  {content_to_print}")
                except UnicodeEncodeError:
                    # Fallback for Windows consoles that don't support unicode
                    print(f"Content:  {content_to_print.encode('ascii', errors='replace').decode('ascii')}")
            print("-" * 50)
            
        except Exception as e:
            print(f"Test failed with error: {e}")
            import traceback
            traceback.print_exc()
