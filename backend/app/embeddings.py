from openai import OpenAI
from app.config import settings

client = OpenAI(api_key=settings.openai_api_key)

EMBEDDING_MODEL = "text-embedding-3-small"

def generate_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model = EMBEDDING_MODEL,
        input = text
    )
    return response.data[0].embedding

def generate_embeddings_batch(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    response = client.embeddings.create(
        model = EMBEDDING_MODEL,
        input = texts
    )
    return [item.embedding for item in response.data]