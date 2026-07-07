import sys
import os

try:
    from langchain_core.tools import tool
except ImportError:
    try:
        from langchain.agents import tool
    except ImportError:
        # Simple decorator fallback
        def tool(func):
            return func

try:
    from langchain_community.tools import DuckDuckGoSearchRun
except ImportError:
    # Fallback to langchain.tools if community tool is not found directly
    from langchain.tools import DuckDuckGoSearchRun


from tools.safe_call import safe_call


@tool
@safe_call
def search_web(query: str) -> str:
    """
    Search the web to retrieve real-time information, news, or answers
    to questions that are not answered by local indexed documents.

    Args:
        query (str): The search query to submit to the web search engine.

    Returns:
        str: A summary of the search results or a failure message.
    """
    try:
        # Instantiate and run DuckDuckGo search
        search = DuckDuckGoSearchRun()
        result = search.run(query)
        
        if not result or not result.strip():
            return f"No search results found for: '{query}'."
            
        return result
    except Exception as e:
        raise e


if __name__ == "__main__":
    # Ensure stdout handles potential console unicode encoding differences
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    print("=== Web Search Tool Standalone Test Sandbox ===")
    
    test_query = "latest AI news 2026"
    print(f"Submitting query: '{test_query}'...")
    
    # Run the tool's invoke method (standard for LangChain tools)
    output = search_web.invoke(test_query)
    
    print("\nSearch Output:")
    print("-" * 60)
    try:
        print(output)
    except UnicodeEncodeError:
        print(output.encode('ascii', errors='replace').decode('ascii'))
    print("-" * 60)
