# tinyRAG

Local-first RAG assistant with:
- Next.js frontend (`frontend/`)
- FastAPI backend (`api.py`)
- ChromaDB vector store (`data/chroma`)
- SQLite app database (`data/app.db`)

## Features
- Workspace and chat management
- PDF upload and background indexing
- Streaming chat responses (SSE)
- Source citations
- Markdown/LaTeX rendering in chat
- Local/LAN usage support

## Architecture
- Frontend: Next.js + React + shadcn/ui
- Backend: FastAPI + aiohttp + sentence-transformers
- Retrieval: Chroma vector search (workspace-scoped)
- Persistence: SQLite for app entities and metadata

## Requirements
- Windows 10/11 (PowerShell)
- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- Node.js 20+
- pnpm 9+
- Ollama running with your selected model

## Quick Start (Windows)

2. Start backend + frontend:
```powershell
.\Start.ps1
```

3. Open app:
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`

## Configuration

### Backend
- File: `CONFIG.toml`
- Main options:
  - server upload path and model name
  - Chroma persistence path/collection
  - embedding model

### Frontend API base
Set in `frontend/.env`:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```
For LAN usage, set it to your backend machine IP:
```env
NEXT_PUBLIC_API_BASE_URL=http://192.168.x.x:8000
```

Important: restart frontend after changing `.env`.

## Build Instructions

### Frontend production build
```powershell
cd frontend
pnpm build
pnpm start -- --hostname 0.0.0.0 --port 3000
```

### Backend production run
```powershell
uv run uvicorn api:app --host 0.0.0.0 --port 8000
```

## Project Structure
```text
api.py
chroma.py
database.py
CONFIG.toml
shared.py
Start.ps1
Setup.ps1
frontend/
  app/
  components/
  package.json
```

## Troubleshooting
- `crypto.randomUUID is not a function` on LAN:
  - Use a fallback ID generator in client code.

## Known Limitations
- Retrieval is currently vector-first (hybrid search planned).

## Roadmap
- Hybrid retrieval (vector + keyword)
- Config/settings UI
- Improved evaluation and observability
- Optional packaging for non-dev users
