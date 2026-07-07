import base64
import os
import sys
import mimetypes
from dotenv import load_dotenv

# Ensure the root directory is in the Python path
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
        # Fallback decorator
        def tool(func):
            return func

try:
    from groq import Groq
except ImportError:
    Groq = None

# Load environment variables from .env
load_dotenv()


from tools.safe_call import safe_call


@tool
@safe_call
def describe_image(image_path: str) -> str:
    """
    Analyzes an image file from the local file system and returns a detailed description 
    of its contents using Groq's vision-capable LLM model.

    Args:
        image_path (str): The absolute or relative path to the image file.

    Returns:
        str: A detailed description of the image, or a fallback error message.
    """
    if Groq is None:
        return "Error: The 'groq' Python SDK is not installed. Please install it to use this tool."

    # Validate file existence
    if not os.path.exists(image_path):
        return f"Error: The image file was not found at path: {image_path}"

    if os.path.getsize(image_path) == 0:
        return f"Error: The image file at {image_path} is empty (0 bytes)."

    # Determine the MIME type
    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type:
        mime_type = "image/jpeg"  # Fallback MIME type

    try:
        # 1. Base64 encode the image
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        # 2. Get API key and verify
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            return "Error: GROQ_API_KEY environment variable is not set in .env."

        # 3. Instantiate Groq client
        client = Groq(api_key=api_key)

        # 4. Request vision completion
        # Groq's current recommended vision model: "llama-3.2-11b-vision-preview"
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this image in detail. Focus on the key visual elements, text, layout, colors, and overall context."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            model="meta-llama/llama-4-scout-17b-16e-instruct",
        )

        response_text = chat_completion.choices[0].message.content
        if not response_text or not response_text.strip():
            return "The model returned an empty description for the image."

        return response_text

    except Exception as e:
        raise e


if __name__ == "__main__":
    # Ensure stdout handles potential console unicode encoding differences
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    print("=== Describe Image Tool Standalone Test Sandbox ===")
    
    test_image_path = "./test.jpg"
    
    # Check if test image exists. If not, generate a simple placeholder JPEG to test the pipeline.
    if not os.path.exists(test_image_path):
        print(f"'{test_image_path}' not found. Attempting to generate a placeholder image...")
        try:
            from PIL import Image, ImageDraw
            
            # Create a 300x300 pixel RGB image with a gradient-like background color
            img = Image.new('RGB', (300, 300), color=(30, 41, 59)) # Slate background
            d = ImageDraw.Draw(img)
            
            # Draw simple geometric shapes
            d.rectangle([(50, 50), (250, 250)], outline=(56, 189, 248), width=3) # Blue box
            d.ellipse([(100, 100), (200, 200)], fill=(244, 63, 94)) # Rose circle
            
            # Add text
            d.text((80, 260), "GenAI Hackathon 2026", fill=(255, 255, 255))
            
            img.save(test_image_path, "JPEG")
            print(f"Generated placeholder image at '{test_image_path}'.")
        except Exception as ex:
            print(f"Could not generate placeholder image: {ex}")
            print("Please provide a valid JPEG image at './test.jpg' to run the test.")

    if os.path.exists(test_image_path):
        print(f"Describing image at: '{test_image_path}'...")
        # Invoke the tool directly
        description = describe_image.invoke(test_image_path)
        
        print("\nModel Description:")
        print("-" * 60)
        try:
            print(description)
        except UnicodeEncodeError:
            print(description.encode('ascii', errors='replace').decode('ascii'))
        print("-" * 60)
