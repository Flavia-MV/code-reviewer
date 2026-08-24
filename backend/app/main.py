from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.auth import router as auth_router, get_current_user
from app.repos import router as repos_router
from app.models import User

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Code Reviewer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(repos_router)


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.get("/me")
def get_me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "avatar_url": user.avatar_url,
    }