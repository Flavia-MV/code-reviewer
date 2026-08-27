# Code Reviewer

An AI assistant for exploring codebases. Connect a GitHub repo, ask questions about the code, get PR reviews and
auto-generate docs - all grounded in the actual source code through RAG, not just LLM knowledge.
**Live demo**: https://code-reviewer-zeta-ruby.vercel.app

## What it does

- Import a GitHub repo (OAuth login)
- Index it: chunk the code by function/class (AST parsing with tree-sitter), embed each chunk with OpenAI
- Ask questions about the codebase and get answers that cite the actual file and line numbers
- Get an AI review of a Pull Request's diff
- Ask it to explain a file or generate documentation for it

## Architecture

Indexing flow: pull repo files from GitHub, filter to code files, chunk with tree-sitter (function/class level, whole 
file as fallback if there's no function/class), embed each chunk, store in Postgres.

Question answering: embed the question, compare against stored chunk embeddings (cosine similarity), take the most 
relevant chunks, build prompt with that context, send to GPT-4o-mini, return the answer with sources.

## Stack

Python, FastAPI, SQLAlchemy, Postgres, Node 20+, a GitHub OAuth app and an OpenAI API key.

```bash
doecker compose up -d

cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# fill in .env with your GitHub/OpenAI credentials
uvicorn app.main:app --reload
```

```bash
cd frontend
npm install
npm run dev
```
Then go to `localhost:3000`, log in with GitHUb, import a repo, index it and ask it something.

## A few decisions worth mentioning

I chunk by functions/class instead of fixed character counts, using tree-sitter to actually parse the code means a chunk 
never gets cut off mid-function and the embeddings represent something semantically complete. Files that don't have any 
functions or classes (a plain script for example) just get treated as one chunk, so they are not invisible to search.

Retrieval isn't pure cosine similarity. I noticed early on that a file using a class (calling its methods) sometimes 
scored higher than the file that actually defines that class; both files just share a lot of the same words. I fixed it
by giving a score boost when the exact class/function name shows up in the question, which I confirmed by logging the 
raw similarity scores during testing. There's also a minimum score cutoff, so irrelevant chunks don't get passed to the 
LLM just to fill out top 5.

pgvector was in the Docker setup from the beginning, even before embeddings existed, specifically so I wouldn't have to 
migrate infrastructure later.

The HTTP layer and the actual logic are kept separate; functions like `review_pr()` or `search_relevant_chunks()` don't 
know anything about FastAPI, they just raise a plain `ValueError` if something's wrong. The API layer catches that and 
turns it into a proper HTTP response. Makes the core logic easier to test or reuse outside the API.

## What's not done / would do next

- Indexing runs synchronously right now, fine for small repos, but a bigger one would need to be a background job. Redis
is already in the stack for exactly this reason
- Embeddings are stored as plain float array, not pgvector's native vector type, so similariry search doesn't use an 
actual vector index yet. Works fine at this scale, wouldn't at a such bigger one.
- PR review is triggered mannualy (you give it a PR number) instead of reacting to GitHub webhooks automatically.
- No real test suite yet. CI currently just checks that the app boots and the frontend builds cleanly.

