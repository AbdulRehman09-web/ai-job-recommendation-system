# src/helper.py
import os
import fitz  # PyMuPDF
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def extract_text_from_pdf(uploaded_file):
    """
    uploaded_file: a file-like object (Streamlit UploadedFile or BytesIO).
    Returns extracted text (concatenated pages).
    """
    # Ensure stream is at start
    try:
        uploaded_file.seek(0)
    except Exception:
        pass

    # If stream is bytes (BytesIO), pass directly; if Streamlit UploadedFile, it has read()
    data = uploaded_file.read() if hasattr(uploaded_file, "read") else uploaded_file
    if not data:
        return ""

    doc = fitz.open(stream=data, filetype="pdf")
    pages = []
    for page in doc:
        pages.append(page.get_text())
    return "\n".join(pages).strip()

def ask_openrouter(prompt: str, max_tokens: int = 500, model: str = "gpt-3.5-turbo"):
    """
    Call OpenRouter's chat/completions HTTP API (OpenAI-style response).
    Returns assistant text (string).
    """
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY not configured in environment")

    # Trim prompt to avoid huge inputs (simple heuristic)
    if len(prompt) > 4000:
        prompt = prompt[:4000] + "\n\n[TRUNCATED]"

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
    except requests.RequestException as e:
        raise RuntimeError(f"Network error contacting OpenRouter: {e}")

    if resp.status_code != 200:
        try:
            info = resp.json()
        except Exception:
            info = resp.text
        raise RuntimeError(f"OpenRouter returned status {resp.status_code}: {info}")

    data = resp.json()
    # Expect OpenAI-like response: choices[0].message.content
    try:
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        # Fallback: try 'choices[0].text' or return full json truncated
        try:
            return data["choices"][0]["text"].strip()
        except Exception:
            return str(data)[:2000]
