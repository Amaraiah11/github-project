# Local GitHub Repository Code Explainer

Flow: GitHub URL -> GitPython clone -> file filtering -> Ollama (local LLM) -> FastAPI -> Streamlit

## Setup
1. Install Python 3.10+, Git, and Ollama (https://ollama.com).
2. Pull a model:   `ollama pull qwen2.5-coder:3b`
3. Create venv:
   - Windows: `python -m venv venv` then `venv\Scripts\activate`
   - Mac/Linux: `python3 -m venv venv && source venv/bin/activate`
4. `pip install -r requirements.txt`

## Run (3 terminals in VS Code)
1. `ollama serve`   (skip if Ollama already runs in the background)
2. `uvicorn backend:app --reload`
3. `streamlit run app.py`

Open http://localhost:8501 and paste a repo URL.

## Change the model
Edit `MODEL` in `llm_client.py` (qwen2.5:3b, phi3:mini, gemma2:2b, llama3.2:3b).
