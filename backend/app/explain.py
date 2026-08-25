from app.rag import client, CHAT_MODEL
from app.models import RepoFile

EXPLAIN_SYSTEM_PROMPT = """You are a senior engineer explaining code to a teammate.
Explain what the given file does, in plain language. Cover its main purpose, 
key functions/classes, and how it likely fits into the rest of the application.
Keep it concise but thorough enough for someone unfamiliar with this file to understand quickyly."""

DOCS_SYSTEM_PROMPT = """You are a technical writer generating documentation for a source file.
Write a short module-level doctstring/summary (3-6 sentences) describing the file's purpose and
its main exported functions and classes. Output only the documentation text, no code, no extra commentary."""

def explain_file(repo_id:int, file_path:str, db) -> dict:
    file = (
        db.query(RepoFile)
        .filter(RepoFile.repo_id == repo_id, RepoFile.file_path == file_path)
        .first()
    )
    if file is None:
        raise ValueError("File not found in this repo")
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": EXPLAIN_SYSTEM_PROMPT},
            {"'role": "user", "content": f"File: {file_path}\n\n{file.content}"},
        ]
    )
    return {"explanation": response.choices[0].message.content}

def generate_docs(repo_id:int, file_path:str, db) -> dict:
    file = (
        db.query(RepoFile)
        .filter(RepoFile.repo_id == repo_id, RepoFile.file_path == file_path)
        .first()
    )
    if file is None:
        raise ValueError("File not found in this repo")
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": DOCS_SYSTEM_PROMPT},
            {"role": "user", "content": f"File: {file_path}\n\n{file.content}"},
        ],
    )
    return {"documentation": response.choices[0].message.content}