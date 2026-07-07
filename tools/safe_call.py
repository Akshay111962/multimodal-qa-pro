import functools
import sys
import traceback

def safe_call(func):
    """
    Decorator that wraps any tool function to:
    - Catch any exception raised inside the function.
    - Log the real error and its traceback to the console for debugging.
    - Return a clean fallback string instead of raising the exception.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Log the real error to stderr
            print(f"\n[SafeCall Decorator] Exception caught in tool '{func.__name__}': {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            print("[SafeCall Decorator] Returning standard fallback message.\n", file=sys.stderr)
            return "This tool encountered an error and could not complete the request."
    return wrapper


if __name__ == "__main__":
    print("=== SafeCall Decorator Test Sandbox ===")
    
    # 1. Define a dummy tool decorated with @safe_call
    @safe_call
    def buggy_tool(param: str) -> str:
        if param == "fail":
            raise RuntimeError("Simulated crash in buggy_tool!")
        return f"buggy_tool succeeded with: {param}"
        
    print("\nCalling buggy_tool with 'success'...")
    res_success = buggy_tool("success")
    print(f"Result: {res_success}")
    
    print("\nCalling buggy_tool with 'fail' (deliberately crashing it)...")
    res_fail = buggy_tool("fail")
    print(f"Result: {res_fail}")
    
    # Verify it returned the standard fallback
    assert res_fail == "This tool encountered an error and could not complete the request."
    print("Assertion passed: buggy_tool returned fallback message successfully.")

    # 2. Test importing an actual decorated tool and triggering an exception
    # (e.g. passing an invalid API key to describe_image to force a Groq API error)
    try:
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from tools.image_tool import describe_image
        
        # Backup original key
        original_key = os.environ.get("GROQ_API_KEY")
        os.environ["GROQ_API_KEY"] = "gsk_invalid_test_key_for_triggering_safecall_decorator"
        
        print("\nCalling describe_image with invalid API key (deliberately triggering Groq API exception)...")
        # Since describe_image is a LangChain tool, we invoke it
        res_image = describe_image.invoke({"image_path": "./test.jpg"})
        print(f"Result: {res_image}")
        
        # Restore key
        if original_key:
            os.environ["GROQ_API_KEY"] = original_key
        else:
            del os.environ["GROQ_API_KEY"]
            
        assert res_image == "This tool encountered an error and could not complete the request."
        print("Assertion passed: describe_image returned fallback message successfully.")
        
    except Exception as ex:
        print(f"Failed to run import/tool test: {ex}")

