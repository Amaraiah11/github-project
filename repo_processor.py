"""Repository processing: clone -> filter -> extract code."""
import os
import re
import shutil
import stat
from collections import Counter
from pathlib import Path

from git import Repo

REPOS_DIR = Path("cloned_repos")

GITHUB_RE = re.compile(r"^https://github\.com/[\w.-]+/[\w.-]+?(\.git)?/?$")

IGNORE_DIRS = {
    ".git", "node_modules", "venv", ".venv", "env", "__pycache__", "dist",
    "build", ".idea", ".vscode", "target", "vendor", "site-packages", "migrations",
}

CODE_EXTENSIONS = {
    ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript", ".jsx": "React (JSX)",
    ".tsx": "React (TSX)", ".java": "Java", ".go": "Go", ".rs": "Rust",
    ".c": "C", ".cpp": "C++", ".cs": "C#", ".php": "PHP", ".rb": "Ruby",
    ".html": "HTML", ".css": "CSS", ".sql": "SQL", ".kt": "Kotlin", ".swift": "Swift",
}

# Files that describe the project; we read them first.
IMPORTANT_NAMES = {
    "readme.md", "requirements.txt", "package.json", "pyproject.toml", "pom.xml",
    "go.mod", "cargo.toml", "dockerfile", "docker-compose.yml",
}
ENTRY_POINTS = {"main.py", "app.py", "server.py", "index.js", "app.js", "server.js",
                "index.ts", "main.go", "main.java", "manage.py"}

MAX_FILE_BYTES = 5_000_000
MAX_CHARS_PER_FILE = 1500
MAX_FILES = 5

def is_valid_github_url(url: str) -> bool:
    return bool(GITHUB_RE.match(url.strip()))


def _force_remove(func, path, _exc):
    """Windows fix: .git files are read-only, so rmtree needs this."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def clone_repo(url: str) -> Path:
    url = url.strip().rstrip("/")
    name = url.split("/")[-1].removesuffix(".git")
    dest = REPOS_DIR / name
    REPOS_DIR.mkdir(exist_ok=True)
    if dest.exists():
        shutil.rmtree(dest, onerror=_force_remove)
    Repo.clone_from(url, dest, depth=1)  # shallow clone = fast
    return dest


def collect_files(repo_path: Path):
    """Return (files_to_read, language_counter). files_to_read is a list of Paths."""
    candidates = []
    languages = Counter()

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            p = Path(root) / f
            ext = p.suffix.lower()
            lname = f.lower()
            is_important = lname in IMPORTANT_NAMES
            if ext not in CODE_EXTENSIONS and not is_important:
                continue
            try:
                if p.stat().st_size > MAX_FILE_BYTES or p.stat().st_size == 0:
                    continue
            except OSError:
                continue
            if ext in CODE_EXTENSIONS:
                languages[CODE_EXTENSIONS[ext]] += 1

            # lower score = read earlier
            depth = len(p.relative_to(repo_path).parts)
            if lname in IMPORTANT_NAMES:
                score = 0
            elif lname in ENTRY_POINTS:
                score = 1
            else:
                score = 2 + depth
            candidates.append((score, p))

    candidates.sort(key=lambda x: (x[0], str(x[1])))
    return [p for _, p in candidates[:MAX_FILES]], languages


def read_file(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""
    return text[:MAX_CHARS_PER_FILE]
