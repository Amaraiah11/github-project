"""FastAPI backend. Run: uvicorn backend:app --reload"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator

from explainer import explain_repository
from repo_processor import is_valid_github_url

app = FastAPI(title="GitHub Repo Explainer")


class RepoRequest(BaseModel):
    repo_url: str

    @field_validator("repo_url")
    @classmethod
    def check_url(cls, v: str) -> str:
        if not is_valid_github_url(v):
            raise ValueError("Enter a URL like https://github.com/username/repository")
        return v.strip()


class ExplainResponse(BaseModel):
    repo_name: str
    files_analyzed: list[str]
    languages: list[str]
    explanation: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/explain", response_model=ExplainResponse)
def explain(req: RepoRequest):
    try:
        return explain_repository(req.repo_url)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
