import os
import sys
from typing import List

# Ensure the root directory is in the Python path so imports work seamlessly
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from langchain_core.tools import tool
except ImportError:
    try:
        from langchain.agents import tool
    except ImportError:
        # Fallback if langchain tools are not installed in the context
        def tool(func):
            return func

from vectorstore.chroma_utils import get_chroma_collection
from tools.safe_call import safe_call


@tool
@safe_call
def search_documents(query: str) -> str:
    """
    Search indexed PDF documents for information relevant to the given query.

    Args:
        query (str): The search query or question to find in the documents.

    Returns:
        str: A formatted string containing the top relevant text chunks,
             their source filenames, and page numbers, or an informative message.
    """
    try:
        # Load the collection
        db = get_chroma_collection(collection_name="documents")
        
        # Verify if database has any records before querying
        # db.get() fetches stored items; an empty response implies no indexed documents.
        db_items = db.get()
        if not db_items or not db_items.get("ids"):
            return (
                "No documents have been indexed in the database yet.\n"
                "Please run the indexing process (index_pdf) to add documents first."
            )
            
        # Perform similarity search retrieving top 4 chunks
        results = db.similarity_search(query, k=4)
        
        if not results:
            return f"No relevant results were found in the indexed documents for the query: '{query}'."
            
        formatted_results = []
        for idx, doc in enumerate(results):
            source = doc.metadata.get("source", "Unknown Source")
            page = doc.metadata.get("page", "Unknown Page")
            content = doc.page_content.strip()
            
            # Format the output clearly labeling each attribute
            formatted_results.append(
                f"=== Result {idx + 1} ===\n"
                f"Source: {source} (Page {page})\n"
                f"Content: {content}"
            )
            
        return "\n\n".join(formatted_results)
        
    except Exception as e:
        raise e


if __name__ == "__main__":
    # Configure stdout to handle potential Unicode characters when printing to console
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    print("=== Document Search Tool Standalone Test Sandbox ===")
    
    # We will attempt a search on the default collection.
    # Note: If test.pdf was indexed in the test_collection, we might want to check that database too, 
    # but the tool defaults to the main "documents" collection. Let's test both!
    
    for collection in ["documents", "test_collection"]:
        print(f"\n--- Testing Search on Collection: '{collection}' ---")
        
        try:
            # We bypass the default collection_name in search_documents temporarily for test_collection
            # by overriding the function dynamically or testing the flow using direct retrieval.
            # To run a clean standalone test, we will perform a similarity search directly 
            # using get_chroma_collection and print the results.
            
            db = get_chroma_collection(collection_name=collection)
            
            # Check if there are documents
            items = db.get()
            if not items or not items.get("ids"):
                print(f"Status: Collection '{collection}' is empty.")
                continue
                
            test_query = "hackathon rules"
            print(f"Running similarity search query: '{test_query}'...")
            
            # Use search_documents on the collection.
            # Since search_documents is a tool and is hardcoded to collection_name="documents",
            # we will temporarily use the retriever or search logic.
            # However, if we test with the actual tool, let's also query the main "documents" collection.
            
            # Let's run the search logic directly for this print test to support both collections:
            results = db.similarity_search(test_query, k=4)
            if not results:
                print("Status: No relevant results found.")
            else:
                for idx, doc in enumerate(results):
                    source = doc.metadata.get("source", "Unknown Source")
                    page = doc.metadata.get("page", "Unknown Page")
                    print(f"\n[Result {idx + 1}] Source: {source} | Page: {page}")
                    content = doc.page_content.strip()
                    try:
                        print(f"Content: {content[:200]}...")
                    except UnicodeEncodeError:
                        print(f"Content: {content[:200].encode('ascii', errors='replace').decode('ascii')}...")
                        
        except Exception as e:
            print(f"Failed to query collection '{collection}': {e}")

    # Now run the actual tool itself to verify its output signature and fallback behavior
    print("\n--- Testing the tool function search_documents() directly ---")
    tool_output = search_documents.invoke("hackathon submission requirements")
    print("\nTool Output:")
    print("-" * 60)
    try:
        print(tool_output)
    except UnicodeEncodeError:
        print(tool_output.encode('ascii', errors='replace').decode('ascii'))
    print("-" * 60)
