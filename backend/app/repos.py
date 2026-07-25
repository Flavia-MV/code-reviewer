import base64

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import User, Repo, RepoFile, IndexStatus

router = APIRouter(prefix="/repos", tags=["repos"])

CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs",
    ".rb", ".php", ".c", ".cpp", ".h", ".cs", ".kt", ".swift",
}
IGNORED_DIRS = {"node_modules", ".git", "dist", "build", "vendor", "__pycache__"}
MAX_FILE_SIZE_BYTES = 200_000


@router.post("/import")
async def import_repo(
    full_name: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = db.query(Repo).filter(
        Repo.owner_id == user.id, Repo.full_name == full_name
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Repo already imported")

    headers = {"Authorization": f"Bearer {user.access_token}"}

    async with httpx.AsyncClient() as client:
        repo_response = await client.get(
            f"https://api.github.com/repos/{full_name}", headers=headers
        )
        if repo_response.status_code != 200:
            raise HTTPException(status_code=404, detail="Repo not found or no access")
        repo_data = repo_response.json()
        default_branch = repo_data["default_branch"]

        tree_response = await client.get(
            f"https://api.github.com/repos/{full_name}/git/trees/{default_branch}",
            params={"recursive": "1"},
            headers=headers,
        )
        tree_data = tree_response.json()

        repo = Repo(owner_id=user.id, full_name=full_name, default_branch=default_branch,
                    index_status=IndexStatus.pending)
        db.add(repo)
        db.flush()

        code_files = [
            item for item in tree_data.get("tree", [])
            if item["type"] == "blob"
            and any(item["path"].endswith(ext) for ext in CODE_EXTENSIONS)
            and not any(f"/{ignored}/" in f"/{item['path']}/" for ignored in IGNORED_DIRS)
            and item.get("size", 0) < MAX_FILE_SIZE_BYTES
        ]

        for item in code_files:
            blob_response = await client.get(
                f"https://api.github.com/repos/{full_name}/git/blobs/{item['sha']}",
                headers=headers,
            )
            blob_data = blob_response.json()
            try:
                content = base64.b64decode(blob_data["content"]).decode("utf-8")
            except (UnicodeDecodeError, KeyError):
                continue

            db.add(RepoFile(
                repo_id=repo.id,
                path=item["path"],
                language=item["path"].rsplit(".", 1)[-1],
                content=content,
                sha=item["sha"],
            ))

    db.commit()
    db.refresh(repo)

    return {
        "id": repo.id,
        "full_name": repo.full_name,
        "files_imported": len(code_files),
        "index_status": repo.index_status,
    }


@router.get("")
def list_repos(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    repos = db.query(Repo).filter(Repo.owner_id == user.id).all()
    return [
        {"id": r.id, "full_name": r.full_name, "index_status": r.index_status}
        for r in repos
    ]


@router.get("/{repo_id}/files")
def list_repo_files(
    repo_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    repo = db.query(Repo).filter(Repo.id == repo_id, Repo.owner_id == user.id).first()
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")

    files = db.query(RepoFile).filter(RepoFile.repo_id == repo_id).all()
    return [{"path": f.path, "language": f.language} for f in files]