"""Streamlit frontend. Run: streamlit run app.py"""
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/explain"

st.set_page_config(page_title="GitHub Repo Explainer", page_icon="📦")
st.title("📦 GitHub Repository Explainer")
st.caption("Runs fully locally: GitPython + Ollama + FastAPI + Streamlit")

repo_url = st.text_input("GitHub repository URL", placeholder="https://github.com/username/repository")

if st.button("Explain this repository", type="primary"):
    if not repo_url.strip():
        st.warning("Please enter a URL.")
    else:
        with st.spinner("Cloning, reading code and asking the local LLM... (can take a few minutes)"):
            try:
                resp = requests.post(API_URL, json={"repo_url": repo_url}, timeout=900)
            except requests.ConnectionError:
                st.error("Backend not running. Start it with: uvicorn backend:app --reload")
                st.stop()

        if resp.status_code == 200:
            data = resp.json()
            st.success(f"Done: {data['repo_name']}")
            st.markdown(data["explanation"])
            with st.expander("Files analyzed"):
                for f in data["files_analyzed"]:
                    st.write(f"- `{f}`")
            st.write("**Languages detected:**", ", ".join(data["languages"]) or "n/a")
        else:
            detail = resp.json().get("detail", resp.text)
            st.error(f"Error: {detail}")
