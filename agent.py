import os
import sys
from typing import List, Tuple
from dotenv import load_dotenv

# Ensure the root directory is in the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Load environment variables from .env
load_dotenv()

try:
    from langchain_groq import ChatGroq
except ImportError as e:
    print(f"Error: langchain-groq not found. Details: {e}")
    ChatGroq = None

try:
    from langgraph.prebuilt import create_react_agent
except ImportError as e:
    print(f"Error: langgraph not found. Details: {e}")
    create_react_agent = None

# Import our tools
from tools.doc_search import search_documents
from tools.web_search import search_web
from tools.image_tool import describe_image

# 1. System Prompt Definition
SYSTEM_PROMPT = (
    "You are a helpful and intelligent hybrid AI agent designed for a Hackathon RAG system. "
    "You have access to local documents, real-time web search, and image analysis capabilities.\n\n"
    "Observe the following rules when resolving queries:\n"
    "1. Local Document Search: Use the `search_documents` tool for questions regarding the GenAI Summer of Code, "
    "hackathon rules, format, schedules, submission guidelines, or any material contained within the local indexed PDFs.\n"
    "2. Web Search: Use the `search_web` tool for real-time information, news, current events, or general knowledge "
    "questions that are not related to or covered in the local document index.\n"
    "3. Image Description: Use the `describe_image` tool ONLY when the user asks about an image or upload.\n"
    "4. Combined Querying: If a question spans both local resources and general/real-time knowledge, "
    "combine findings from local search and web search into a single, synthesized, cohesive response.\n"
    "5. Sources Citation: Always briefly mention at the very end of your response which sources/tools were used."
)


def run_agent(query: str) -> Tuple[str, List[str]]:
    """
    Invokes the hybrid RAG agent with the system prompt and a user query.
    
    Args:
        query (str): The question or query from the user.
        
    Returns:
        Tuple[str, List[str]]:
            - str: The final textual answer from the agent.
            - List[str]: The list of tool names that were called during execution.
    """
    if ChatGroq is None or create_react_agent is None:
        raise RuntimeError("Missing dependencies: langchain-groq or langgraph must be installed.")

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set. Please add it to your Render Environment Variables.")

    # Initialize the tools
    tools = [search_documents, search_web, describe_image]

    try:
        # Initialize the ChatGroq model (llama-3.3-70b-versatile)
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.0,
            api_key=api_key.strip(),
            max_retries=2
        )

        # Create the ReAct agent
        agent = create_react_agent(
            model=llm,
            tools=tools,
            prompt=SYSTEM_PROMPT
        )

        # Execute the query with a recursion limit of 12
        inputs = {"messages": [("user", query)]}
        config = {"recursion_limit": 12}
        
        response = agent.invoke(inputs, config=config)
    except Exception as e:
        error_msg = str(e)
        # Catch standard Groq API BadRequestError or tool use failure messages
        if "400" in error_msg or "tool_use_failed" in error_msg or "BadRequestError" in error_msg:
            print("\n[System Warning]: Llama-3.3-70b-versatile tool execution failed.")
            print("Running fallback: direct LLM without tools...\n")
            
            # Fallback: direct LLM call without tools to always get an answer
            try:
                llm_direct = ChatGroq(
                    model="llama-3.3-70b-versatile",
                    temperature=0.2,
                    api_key=api_key.strip()
                )
                direct_response = llm_direct.invoke([
                    ("system", SYSTEM_PROMPT),
                    ("user", query)
                ])
                return direct_response.content, ["direct_llm (no tools)"]
            except Exception as fallback_err:
                print(f"Direct LLM fallback also failed: {fallback_err}")
                # Try the smaller model as last resort
                llm_small = ChatGroq(
                    model="llama-3.1-8b-instant",
                    temperature=0.2,
                    api_key=api_key.strip()
                )
                small_response = llm_small.invoke([
                    ("system", "You are a helpful AI assistant. Answer the user's question clearly and thoroughly."),
                    ("user", query)
                ])
                return small_response.content, ["fallback_llm (llama-3.1-8b)"]
        else:
            # Raise other unexpected errors (e.g. invalid api keys, timeouts)
            raise e

    # Extract the final answer content from the last message
    messages = response.get("messages", [])
    final_answer = ""
    if messages:
        final_answer = messages[-1].content

    # Trace which tools were called
    called_tools = []
    for msg in messages:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                called_tools.append(tc.get("name"))

    # Deduplicate keeping order
    called_tools = list(dict.fromkeys(called_tools))

    return final_answer, called_tools


if __name__ == "__main__":
    # Ensure stdout handles potential console unicode encoding differences
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    print("=== LangGraph Hybrid RAG Agent Test Sandbox ===\n")

    # Define the 3 test queries
    test_queries = [
        # Query 1: local documents only (from test.pdf)
        "What are the rules and format for the GenAI Summer of Code Hackathon 2026?",
        
        # Query 2: web search only (current events)
        "What are the main AI-related announcements from Google I/O 2026?",
        
        # Query 3: hybrid (both documents and web search)
        "Explain what the GenAI Summer of Code Hackathon 2026 is, and compare its focus with the broader industry announcements made at Google I/O 2026."
    ]

    for idx, query in enumerate(test_queries, 1):
        print(f"=== Query {idx} ===")
        print(f"User Question: '{query}'")
        print("Invoking agent...")
        
        try:
            answer, tools_called = run_agent(query)
            
            print(f"\nTools Called: {tools_called if tools_called else 'None'}")
            print("\nAgent Answer:")
            print("-" * 60)
            try:
                print(answer)
            except UnicodeEncodeError:
                print(answer.encode('ascii', errors='replace').decode('ascii'))
            print("-" * 60)
            print("\n")
            
        except Exception as e:
            print(f"Agent failed to execute query: {e}")
            import traceback
            traceback.print_exc()
            print("\n")
