from multiprocessing import synchronize

from sqlalchemy.orm import Session

from app.chunking import chunk_file
from app.embeddings import generate_embeddings_batch
from app.models import Repo, RepoFile, CodeChunk, IndexStatus

BATCH_SIZE = 50

def index_repo(repo_id: int, db: Session):
    repo = db.query(Repo).filter(Repo.id == repo_id).first()
    if repo is None:
        return

    repo.index_status = IndexStatus.indexing
    db.commit()

    try:
        db.query(CodeChunk).filter(
            CodeChunk.file_id.in_(
                db.query(RepoFile.id).filter(RepoFile.repo_id == repo_id)
            )
        ).delete(synchronize_session=False)
        files = db.query(RepoFile).filter(RepoFile.id == repo_id).all()

        all_chunks = []
        for file in files:
            file_chunks = chunk_file(file.content, file.language)
            for chunk in file_chunks:
                chunk["file_id"] = file.id
                all_chunks.append(chunk)

        for i in range(0, len(all_chunks), BATCH_SIZE):
            batch = all_chunks[i:i + BATCH_SIZE]
            texts = [c["content"] for c in batch]
            embeddings = generate_embeddings_batch(texts)

            for chunk, embedding in zip(batch, embeddings):
                db.add(CodeChunk(
                    file_id=chunk["file_id"],
                    content=chunk["content"],
                    chunk_type=chunk["chunk_type"],
                    name=chunk["name"],
                    start_line=chunk["start_line"],
                    end_line=chunk["end_line"],
                    embedding=embedding,
                ))
        repo.index_status = IndexStatus.ready
        db.commit()
    except Exception:
        repo.index_status = IndexStatus.failed
        db.commit()
        raise