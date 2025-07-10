# analysis_note/core_analyzer.py

import google.generativeai as genai
import json
import time
import config
import traceback
from google.generativeai.types import File # Changed: Direct import for the File type
from .prompt_manager import get_news_analysis_prompt

def _upload_with_retry(
    pdf_path: str, max_retries: int = 3
) -> File | None: # Changed: Use the directly imported File type
    """
    A file upload function with retry logic.
    Retries on failure, increasing the wait time with each attempt.
    This is to handle potential transient network fluctuations.
    """
    attempt = 0
    while attempt < max_retries:
        try:
            print(f"[*] Uploading {pdf_path} (Attempt {attempt + 1}/{max_retries})...")
            uploaded_file = genai.upload_file(path=pdf_path, display_name=pdf_path)
            print(f"[*] Upload successful. File name: {uploaded_file.name}")
            return uploaded_file
        except Exception as e:
            # Only retry on recoverable errors like network timeouts
            if "timed out" in str(e).lower():
                attempt += 1
                if attempt < max_retries:
                    wait_time = 5 * (2**attempt)
                    print(f"[!] Upload timed out. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"[!] Upload failed after {max_retries} attempts.")
                    raise e
            else:
                # For other errors (e.g., file not found, permission issues), fail immediately
                print(f"[!] An unrecoverable error occurred during upload: {e}")
                raise e
    return None

def _load_custom_instructions():
    """
    Attempts to load custom instructions from a JSON file.
    Returns an empty dictionary if the file is not found or has a format error.
    """
    try:
        # File path is relative to the project root
        with open("analysis_note/prompt_customization.json", "r", encoding="utf-8") as f:
            print("[*] Loading custom instructions from prompt_customization.json...")
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[*] Could not load custom instructions ({e}). Proceeding with standard analysis.")
        return {}

def analyze_document(pdf_path: str, api_key: str) -> dict | None:
    """
    Performs a full multimodal analysis on a single PDF document using the File API.
    This function loads and applies custom instructions and includes upload retry logic.
    """
    print(f"[*] Analyzing document with File API: {pdf_path}")

    uploaded_file = None  # Initialize for use in exception handling
    try:
        # 1. Configure Gemini
        genai.configure(api_key=api_key)
        model_name = config.AI_CONFIG.get("MODEL_NAME", "gemini-1.5-pro-latest")

        # 2. Upload the file using the function with retry logic
        uploaded_file = _upload_with_retry(pdf_path)
        if not uploaded_file:
            # Abort if the upload ultimately fails
            return None

        # 3. Load custom instructions
        custom_instructions = _load_custom_instructions()

        # 4. Pass instructions to the prompt manager to generate the final prompt
        prompt = get_news_analysis_prompt(custom_instructions)

        # 5. Initialize the model and send the request
        model = genai.GenerativeModel(model_name)
        print("[*] Sending request with file reference and custom prompt to AI...")
        response = model.generate_content([uploaded_file, prompt])

        # 6. Parse the result
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        analysis_result = json.loads(cleaned_response)
        print(f"[+] Successfully parsed AI response.")

        return analysis_result

    except Exception as e:
        print(f"[!] An error occurred during multimodal analysis for {pdf_path}: {e}")

        print("\n--- Full Error Traceback ---")
        traceback.print_exc()  # <--- 2. 增加这一行来打印完整的错误堆栈
        print("--------------------------\n")

        if 'response' in locals() and hasattr(response, "text"):
            print(f"[!] Raw response from AI: {response.text}")
        return None

    finally:
        # 7. Regardless of success, if a file was uploaded, try to delete it
        if uploaded_file:
            print(f"[*] Cleaning up: Deleting uploaded file {uploaded_file.name}")
            genai.delete_file(uploaded_file.name)