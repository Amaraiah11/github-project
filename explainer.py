"""Two-stage explanation (map-reduce) so small LLMs with small context still work.

Stage 1: summarise each file in 2-3 lines.
Stage 2: combine the summaries into the final beginner-friendly overview.
"""
from pathlib import Path

from llm_client import ask_llm
from repo_processor import clone_repo, collect_files, read_file

FILE_SYSTEM = "You are a senior developer who explains code briefly and accurately."

FINAL_SYSTEM = "You explain software projects to beginners in simple language. Only use facts from the notes."

FINAL_TEMPLATE = """Below are notes about files in a GitHub repository called "{name}".
Detected languages: {languages}

NOTES:
{notes}

Write an explanation in EXACTLY this format:

Project Overview
<2-3 simple sentences on what this project is>

The application allows users to:
• <feature>
• <feature>
• <feature>

Main Technologies:
• <technology>

How it works:
<4-6 simple sentences describing the flow from the user, to the frontend, to the backend/data, and back>

Do not invent features that are not in the notes."""


def explain_repository(url: str) -> dict:
    repo_path: Path = clone_repo(url)
    files, languages = collect_files(repo_path)
    if not files:
        raise ValueError("No supported source files found in this repository.")

    notes = []
    for f in files:
        rel = f.relative_to(repo_path)
        code = read_file(f)
        summary = ask_llm(
            f"File: {rel}\n\n```\n{code}\n```\n\n"
            "In 2-3 sentences, say what this file does.",
            system=FILE_SYSTEM,
        )
        notes.append(f"- {rel}: {summary}")

    final = ask_llm(
        FINAL_TEMPLATE.format(
            name=repo_path.name,
            languages=", ".join(languages) or "unknown",
            notes="\n".join(notes),
        ),
        system=FINAL_SYSTEM,
    )
    return {
        "repo_name": repo_path.name,
        "files_analyzed": [str(f.relative_to(repo_path)) for f in files],
        "languages": list(languages.keys()),
        "explanation": final,
    }
