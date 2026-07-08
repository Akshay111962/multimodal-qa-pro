import os
import sys

# Ensure root directory is in the Python path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from vectorstore.chroma_utils import index_pdf
from tools.image_tool import describe_image
from agent import run_agent


def process_pdf(file_path: str) -> str:
    """
    Indexes the provided PDF file into the local Chroma vector store.

    Args:
        file_path (str): The file path to the PDF document.

    Returns:
        str: A status message indicating success or details of the failure.
    """
    try:
        if not file_path:
            return "Error: No file path provided."

        filename = os.path.basename(file_path)
        
        # Call the indexing function
        db = index_pdf(file_path, collection_name="documents")
        
        # Query database to count the number of chunks indexed in the collection
        results = db.get()
        num_chunks = len(results.get("ids", []))
        
        return f"Successfully indexed {filename} ({num_chunks} chunks created)"
    except Exception as e:
        return f"Failed to index PDF: {e}"


def process_image(image_path: str) -> str:
    """
    Analyzes the provided image using Groq vision-capable model.

    Args:
        image_path (str): The file path to the image.

    Returns:
        str: The image description text or a clean failure message.
    """
    try:
        if not image_path:
            return "Error: No image path provided."
            
        # Describe image using the LangChain tool's invoke method
        # describe_image is decorated with safe_call and handles internal exceptions gracefully
        description = describe_image.invoke({"image_path": image_path})
        return description
    except Exception as e:
        return f"Failed to process image: {e}"


def run_agent_query(query: str) -> dict:
    """
    Submits a query to the hybrid LangGraph RAG agent.

    Args:
        query (str): The search query or conversation input.

    Returns:
        dict: A dictionary containing:
              - "answer": the text response from the agent.
              - "tools_used": list of tools called during execution.
    """
    try:
        if not query or not query.strip():
            return {
                "answer": "Please provide a valid query.",
                "tools_used": []
            }

        answer, tools_used = run_agent(query)
        
        return {
            "answer": answer,
            "tools_used": tools_used
        }
    except Exception as e:
        print(f"Error in backend_interface.run_agent_query: {e}", file=sys.stderr)
        return {
            "answer": f"Something went wrong processing your request: {str(e)}",
            "tools_used": []
        }


if __name__ == "__main__":
    # Ensure stdout handles potential console unicode encoding differences
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    print("=== Backend Interface End-to-End Verification Sandbox ===\n")

    # 1. Test process_pdf
    pdf_path = "./test.pdf"
    print(f"1. Testing process_pdf with: '{pdf_path}'")
    pdf_status = process_pdf(pdf_path)
    print(f"Status Result: {pdf_status}\n")

    # 2. Test process_image
    image_path = "./test.jpg"
    print(f"2. Testing process_image with: '{image_path}'")
    image_description = process_image(image_path)
    print("Description Result:")
    print("-" * 60)
    try:
        print(image_description)
    except UnicodeEncodeError:
        print(image_description.encode('ascii', errors='replace').decode('ascii'))
    print("-" * 60)
    print("\n")

    # 3. Test run_agent_query
    agent_query = "What is the GenAI Summer of Code Hackathon 2026, and is there any related AI announcements from Google in 2026?"
    print(f"3. Testing run_agent_query with query: '{agent_query}'")
    query_result = run_agent_query(agent_query)
    print(f"Tools Used Result: {query_result.get('tools_used')}")
    print("Answer Result:")
    print("-" * 60)
    try:
        print(query_result.get("answer"))
    except UnicodeEncodeError:
        print(query_result.get("answer").encode('ascii', errors='replace').decode('ascii'))
    print("-" * 60)
    print("\n")
