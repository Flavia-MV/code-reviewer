import math
from sqlalchemy.orm import Session
from app.embeddings import generate_embedding
from app.models import CodeChunk, RepoFile

MIN_SCORE_THRESHOLD = 0.35

def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(y * y for y in b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0
    return dot_product / (magnitude_a * magnitude_b)

def search_relevant_chunks(query: str, repo_id: int, db: Session, top_k: int = 5) -> list[dict]:
    query_embedding = generate_embedding(query)
    query_lower = query.lower()

    chunks = (
        db.query(CodeChunk, RepoFile.path)
        .join(RepoFile, CodeChunk.file_id == RepoFile.id)
        .filter(RepoFile.repo_id == repo_id)
        .all()
    )

    scored_chunks = []
    for chunk, file_path in chunks:
        if chunk.embedding is None:
            continue

        score = cosine_similarity(query_embedding, chunk.embedding)

        if chunk.name and chunk.name.lower() in query_lower:
            score+=0.15
        if score < MIN_SCORE_THRESHOLD:
            continue

        scored_chunks.append({
            "chunk": chunk,
            "file_path": file_path,
            "score": score,
        })

    scored_chunks.sort(key=lambda item: item["score"], reverse=True)
    return scored_chunks[:top_k]