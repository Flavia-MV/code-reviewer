from openai import OpenAI
from app.config import settings
from app.search import search_relevant_chunks

client = OpenAI(api_key=settings.openai_api_key)

CHAT_MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """You are a helpful assistant that answers questions about a codebase.
You will be given relevant code snippets, each labeled with its file path and line numbers.
Answer the user's question using only the provided context. Cite the exact file and line numbers you used.
If the context doesn't contain enough information to answer, say so clearly instead of guessing."""

def build_context(chunks: list[dict]) -> str:
    parts = []
    for item in chunks:
        chunk = item["chunk"]
        header = f"File: {item['file_path']} (lines {chunk.start_line}-{chunk.end_line})"
        parts.append(f"{header}\n{chunk.content}")

    return "\n\n--\n\n".join(parts)

def answer_question(query: str, repo_id: int, db) -> dict:
    relevant_chunks = search_relevant_chunks(query, repo_id, db)

    if not relevant_chunks:
        return {
            "answer": "I couldn't find core relevant enough to answer this question confidently.",
            "sources": [],
        }
    context = build_context(relevant_chunks)
    response = client.chat.completions.create(
        model = CHAT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
        ],
    )

    answer = response.choices[0].message.content
    sources = [
        {
            "file_path": item["file_path"],
            "start_line": item["chunk"].start_line,
            "end_line": item["chunk"].end_line,
            "name": item["chunk"].name,
        }
        for item in relevant_chunks
    ]
    return {"answer": answer, "sources": sources}
