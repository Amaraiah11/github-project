"""Talks to the locally running Ollama server."""
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5-coder:1.5b"


def ask_llm(prompt: str, system: str = "You are a helpful assistant.") -> str:
    payload = {
        "model": MODEL,
        "stream": False,
        "options": {"temperature": 0.2, "num_ctx": 4096},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    }
    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=600)
        r.raise_for_status()
    except requests.ConnectionError:
        raise RuntimeError("Cannot reach Ollama. Is it running? Try: ollama serve")
    return r.json()["message"]["content"].strip()
