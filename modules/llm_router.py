# llm_router.py
import os
import openai
# Corrected imports for the modern google-genai SDK
from google import genai # This is the main package
from google.genai import types as google_genai_types
from google.genai import errors as google_genai_errors
from dotenv import load_dotenv
import traceback

# ---------------------------------------------------------------------------
# 0.  Environment
# ---------------------------------------------------------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY_ENV_VAR_NAME = "GOOGLE_API_KEY"
GEMINI_API_KEY = os.getenv(GEMINI_API_KEY_ENV_VAR_NAME)

# ---------------------------------------------------------------------------
# 1.  Public entry point
# ---------------------------------------------------------------------------
def run_llm_task(
    task: str,
    prompt: str,
    context: dict | None = None,
    model_preference: str = "gpt-4o",
    system_prompt: str = ""
):
    print(f"INFO: [llm_router] Task '{task}' → model '{model_preference}'")
    try:
        if model_preference.startswith("gpt"):
            if not OPENAI_API_KEY:
                return {"error": "OpenAI API key not configured (OPENAI_API_KEY missing)."}
            return _call_openai(model_preference, prompt, system_prompt)
        elif model_preference.startswith("gemini"):
            if not GEMINI_API_KEY:
                return {"error": f"Gemini API key not configured ({GEMINI_API_KEY_ENV_VAR_NAME} missing)."}
            return _call_gemini(model_preference, prompt, system_prompt)
        else:
            return {"error": f"Unsupported model: {model_preference}"}
    except Exception as exc:
        print(f"ERROR: [llm_router] During task routing - {type(exc).__name__}: {exc}", flush=True)
        traceback.print_exc()
        return {"error": str(exc)}

# ---------------------------------------------------------------------------
# 2.  OpenAI helper
# ---------------------------------------------------------------------------
def _call_openai(model_name: str, user_prompt: str, system_prompt: str = "") -> dict:
    # ... (OpenAI code remains the same)
    print(f"INFO: [_call_openai] Calling {model_name}")
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        resp   = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.7,
            max_tokens=3500,
        )
        return {"output": resp.choices[0].message.content.strip()}
    except openai.APIError as api_err:
        print(f"ERROR: [_call_openai] OpenAI APIError: {api_err}", flush=True)
        return {"error": f"OpenAI APIError: {api_err}"}
    except Exception as exc:
        print(f"ERROR: [_call_openai] Unhandled {type(exc).__name__}: {exc}", flush=True)
        traceback.print_exc()
        return {"error": f"OpenAI call failed unexpectedly: {exc}"}

# ---------------------------------------------------------------------------
# 3.  Gemini helper
# ---------------------------------------------------------------------------
def _call_gemini(model_name: str, user_prompt: str, system_prompt: str = "") -> dict:
    # print(f"INFO: [_call_gemini] Calling {model_name}")
    try:
        client = genai.Client(api_key=GEMINI_API_KEY) # Uses the corrected 'genai'
        effective_system_instruction = system_prompt if system_prompt else None
        cfg = google_genai_types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=4096,
            system_instruction=effective_system_instruction
        )
        # print(f"DEBUG: [_call_gemini] Using model: {model_name}")
        contents_for_model = [user_prompt]
        response = client.models.generate_content(
            model=model_name,
            contents=contents_for_model,
            config=cfg,
        )
        if not response.candidates:
            block_reason_msg = "Unknown reason (no candidates in response)."
            # ... (rest of no candidates logic as before) ...
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                if hasattr(response.prompt_feedback, 'block_reason_message') and response.prompt_feedback.block_reason_message:
                    block_reason_msg = f"Prompt feedback: {response.prompt_feedback.block_reason_message} (Reason: {response.prompt_feedback.block_reason})."
                elif hasattr(response.prompt_feedback, 'block_reason'):
                    block_reason_msg = f"Prompt feedback: {response.prompt_feedback.block_reason}."
            print(f"ERROR: [_call_gemini] Gemini call resulted in no candidates. {block_reason_msg}")
            return {"error": f"Gemini API Error: No content generated. {block_reason_msg}", "details": str(response.prompt_feedback)}
        return {"output": response.text}

    # ----------- Specific known Google API errors (from google.genai.errors) -----------
    except (google_genai_errors.NotFoundError,
            google_genai_errors.PermissionDeniedError,
            # ... (all other specific errors from google_genai_errors) ...
            google_genai_errors.InvalidArgumentError,
            google_genai_errors.ResourceExhaustedError,
            google_genai_errors.InternalServerError,
            google_genai_errors.DeadlineExceededError,
            google_genai_errors.AbortedError,
            google_genai_errors.CancelledError,
            google_genai_errors.UnauthenticatedError,
            google_genai_errors.APINotEnabledError,
            google_genai_errors.AlreadyExistsError,
            google_genai_errors.FailedPreconditionError,
            google_genai_errors.OutOfRangeError,
            google_genai_errors.DataLossError,
            google_genai_errors.UnavailableError) as specific_api_err:
        print(f"ERROR: [_call_gemini] Specific Gemini Error - {type(specific_api_err).__name__}: {specific_api_err}", flush=True)
        return {"error": f"Gemini API Error ({type(specific_api_err).__name__}): {specific_api_err}"}
    # ----------- Catch the base GoogleGenerativeAIError from types if not caught above -----------
    except google_genai_types.GoogleGenerativeAIError as base_gg_api_err: # Uses 'google_genai_types'
        print(f"ERROR: [_call_gemini] Base Gemini Error - {type(base_gg_api_err).__name__}: {base_gg_api_err}", flush=True)
        return {"error": f"Gemini API Error ({type(base_gg_api_err).__name__}): {base_gg_api_err}"}
    # ----------- General Python errors (anything else) -----------
    except Exception as exc: # General catch-all
        print(f"!!!!!!!!!!!!!! RAW EXCEPTION CAUGHT IN _call_gemini !!!!!!!!!!!!!!")
        print(f"ERROR TYPE: {type(exc)}")
        print(f"ERROR DETAILS: {exc}")
        traceback.print_exc()
        return {"error": f"Gemini call failed unexpectedly: {exc}"}

# ... (if __name__ == "__main__" block as before) ...
if __name__ == "__main__":
    print("\n--- Testing OpenAI ---")
    if OPENAI_API_KEY:
        gpt_response = run_llm_task(
            task="test_gpt",
            prompt="Hello, world! Tell me a joke.",
            model_preference="gpt-3.5-turbo"
        )
        print("GPT Response:", gpt_response)
    else:
        print("Skipping OpenAI test: OPENAI_API_KEY not found.")

    print("\n--- Testing Gemini ---")
    if GEMINI_API_KEY:
        gemini_response_flash = run_llm_task(
            task="test_gemini_flash",
            prompt="Hello, Gemini! What's the capital of France?",
            system_prompt="You are a helpful geography assistant.",
            model_preference="gemini-1.5-flash-latest" # Test with a stable model
        )
        print("Gemini Flash Response:", gemini_response_flash)

        # gemini_2_5_pro_model_id = "gemini-2.5-pro-preview-06-05" # Example from your logs
        # print(f"\nAttempting Gemini 2.5 Pro Preview ({gemini_2_5_pro_model_id})...")
        # gemini_response_2_5_pro = run_llm_task(
        #     task="test_gemini_2_5_pro",
        #     prompt="Explain quantum entanglement.",
        #     system_prompt="You are a physics teacher.",
        #     model_preference=gemini_2_5_pro_model_id
        # )
        # print(f"Gemini {gemini_2_5_pro_model_id} Response:", gemini_response_2_5_pro)
    else:
        print(f"Skipping Gemini test: {GEMINI_API_KEY_ENV_VAR_NAME} not found.")
    print("\n--- Test complete ---")