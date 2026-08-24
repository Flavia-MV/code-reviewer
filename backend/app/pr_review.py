import httpx
from app.config import settings
from app.embeddings import generate_embedding
from app.rag import client, CHAT_MODEL
from app.search import search_relevant_chunks, cosine_similarity
from app.models import Repo

REVIEW_SYSTEM_PROMPT = """You are an experienced code reviewer analyzing a Pull Request.
You will be given diff (changed lines) and relevant context from the rest of the codebase.
Focus specifically on: potential bugs, concurrency issues and edge cases that could break existing functionality.
For each issue found, cite the exact file and line from the diff.
If you find no significant issues, say so clearly instead of inventing problems.
Keep your review concise and actionable."""

async def fetch_pr_diff(full_name:str, pr_number:int, access_token:str) -> str:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3.diff",
    }
    async with httpx.AsyncClient() as client_http:
        response = await client_http.get(
            f"https://api.github.com/repos/{full_name}/pulls/{pr_number}",
            headers=headers,
        )
        if response.status_code != 200:
            raise ValueError("Pull Request not found or no access")
        return response.text

def review_pr(diff:str, repo_id:int, db) -> dict:
    relevant_chunks = search_relevant_chunks(diff[:2000], repo_id, top_k=5)

    context_parts=[]
    for item in relevant_chunks:
        chunk = item["chunk"]
        context_parts.append(
            f"File: {item['file_path']} (lines {chunk.start_line}-{chunk.end_line})\n{chunk.content}"
        )
    context = "\n\n--\n\n".join(context_parts)

    user_message = f"Relevant codebase content:\n{context}\n\nPull Request diff:\n{diff}"

    response = client.chat.conversations.create(
        model = CHAT_MODEL,
        messages = [
            {"role": "system", "content": REVIEW_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )
    return {"review": response.choices[0].message.content}
