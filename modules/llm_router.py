import os
import openai
from google import genai          # ← keep this import form
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# 0.  Environment
# ---------------------------------------------------------------------------
load_dotenv()
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY  = os.getenv("GOOGLE_API_KEY")   # renamed in .env

if OPENAI_API_KEY:
    print("INFO: [llm_router] OpenAI API Key found.")
    openai.api_key = OPENAI_API_KEY
else:
    print("WARNING: [llm_router] OPENAI_API_KEY not found – OpenAI models disabled.")

if GOOGLE_API_KEY:
    print("INFO: [llm_router] Google API Key found.")
else:
    print("WARNING: [llm_router] GOOGLE_API_KEY not found – Gemini models disabled.")


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
    """
    Route a prompt to GPT‑4‑family, Gemini 1.5 (Pro/Flash) or Gemini 2.5 Pro.
    """
    print(f"INFO: [llm_router] Task '{task}' → model '{model_preference}'")

    try:
        if model_preference.startswith("gpt"):
            if not OPENAI_API_KEY:
                return {"error": "OpenAI API key not configured."}
            return _call_openai(model_preference, prompt, system_prompt)

        elif model_preference.startswith("gemini"):
            if not GOOGLE_API_KEY:
                return {"error": "Gemini API key not configured."}
            return _call_gemini(model_preference, prompt, system_prompt)

        else:
            return {"error": f"Unsupported model: {model_preference}"}

    except Exception as exc:
        print(f"ERROR: [llm_router] {type(exc).__name__}: {exc}", flush=True)
        return {"error": str(exc)}


# ---------------------------------------------------------------------------
# 2.  OpenAI helper
# ---------------------------------------------------------------------------
def _call_openai(model_name: str,
                 user_prompt: str,
                 system_prompt: str = "") -> dict:
    print(f"INFO: [_call_openai] Calling {model_name}")
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    client = openai.OpenAI(api_key=OPENAI_API_KEY)  # openai ≥ 1.0
    resp   = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.7,
        max_tokens=3500,
    )
    return {"output": resp.choices[0].message.content.strip()}


# ---------------------------------------------------------------------------
# 3.  Gemini helper  (new + fallback)
# ---------------------------------------------------------------------------
def _call_gemini(model_name: str,
                 user_prompt: str,
                 system_prompt: str = "") -> dict:
    """Handles google‑genai ≥ 0.6 (Client) and < 0.5 (GenerativeModel)."""
    print(f"INFO: [_call_gemini] Calling {model_name}")
    prompt_text = f"{system_prompt}\n\n{user_prompt}" if system_prompt else user_prompt

    try:
        # ─────────────── New SDK path ───────────────
        if hasattr(genai, "Client"):
            client = genai.Client(api_key=GOOGLE_API_KEY)

            cfg = genai.types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=4096,
            )

            resp = client.models.generate_content(
                model=model_name,
                contents=prompt_text,
                config=cfg,
            )
            return {"output": resp.text}

        # ─────────────── Old SDK path ───────────────
        model = genai.GenerativeModel(model_name)
        resp  = model.generate_content(
            prompt_text,
            generation_config=genai.GenerationConfig(
                temperature=0.7,
                max_output_tokens=4096,
            ),
        )
        return {"output": resp.text}

    # ----------- specific Google API errors -----------
    except genai_errors.APIError as api_err:
        print(
            f"ERROR: [_call_gemini] APIError {api_err.code} – {api_err.message}",
            flush=True,
        )
        return {
            "error": f"Gemini APIError {api_err.code}: {api_err.message}"
        }

    # ----------- anything else -----------
    except Exception as exc:
        print(f"ERROR: [_call_gemini] {type(exc).__name__}: {exc}", flush=True)
        return {"error": f"Gemini call failed: {exc}"}