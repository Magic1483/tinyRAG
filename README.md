# tinyRAG 🍜

Local-first RAG assistant with:
- Next.js frontend (`frontend/`)
- FastAPI backend (`api.py`)
- ChromaDB vector store (`data/chroma`)
- SQLite app database (`data/app.db`)


## Demo 

![](./docs/chat_example.png)

<details>
  <summary>More screenshots</summary>
  
  ![](./docs/0222.gif)
  ![](./docs/main_page.png)
  ![](./docs/upload_dashboad.png)
</details>

## What's New in v0.2.0

- Added true hybrid retrieval:
  - dense vector retrieval (Chroma)
  - sparse lexical retrieval (BM25)
  - rank fusion with RRF
- Added optional HyDE retrieval branch for ambiguous queries.
- Added page metadata support for chunk citations.
- Expanded retrieval testing with RFC2812 benchmark scenarios.

### Retrieval Modes

1. Vector only
2. Vector + BM25 (default recommended)
3. Vector + BM25 + HyDE (optional, best for some vague queries)


## Features
- Workspace and chat management
- PDF upload and background indexing
- Hybrid search + HyDE
- JSON chat exporting
- Streaming chat responses (SSE)
- All core data stays on your machine: SQLite + ChromaDB
- Markdown/LaTeX rendering in chat
- Use it on LAN by pointing clients to your backend host

## Architecture
- Frontend: Next.js + React + shadcn/ui
- Backend: FastAPI + aiohttp + sentence-transformers
- Retrieval: Chroma vector search (workspace-scoped)
- Persistence: SQLite for app entities and metadata

## Evaluation

### Setup
- Dataset: 7 fixed questions across RFC2812, RFC3174, RFC6120
- Modes: `vector`, `vector+bm25`, `vector+hyde`, `vector+bm25+hyde`
- Retrieval depth: `k=8`
- Model: `llama3:8b-instruct-q4_K_M`
- Metrics:
  - `avg_kw_score`: expected keyword coverage in answer (0..1)
  - `avg_hit_at_5`: whether gold citation appears in top-5 retrieved chunks
  - `avg_mrr`: reciprocal rank of first gold chunk
  - `avg_answer_len`: normalized answer length (0..1, higher = longer)


### Mean Metrics by Mode

| mode | avg_kw_score | avg_hit_at_5 | avg_mrr | avg_answer_len |
|---|---:|---:|---:|---:|
| vector | 0.686 | 0.714 | 0.536 | 0.926 |
| vector+bm25 | 0.286 | 0.857 | 0.576 | 1.039 |
| vector+bm25+hyde | 0.371 | 0.857 | 0.671 | 1.023 |
| vector+hyde | 0.571 | 0.857 | 0.440 | 1.012 |


### Visuals

![Summary by mode](./docs/imgs/summary_by_mode.png)
_Summary by mode_

![Per-query Hit@5](./docs/imgs/pivot_hit_5.png)
_Per-query Hit@5_

![Per-query Keyword Score](./docs/imgs/pivot_kw_score.png)
_Per-query Keyword Score_

![Per-query MRR](./docs/imgs/pivot_mrr.png)
_Per-query MRR_

### Conclusion
- `vector+bm25+hyde` gives best ranking quality (`MRR`) but is most expensive (extra HyDE request).
- `vector+bm25` is the best default tradeoff for quality vs cost.


## Requirements
- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- Node.js 20+
- pnpm 9+
- Ollama running with your selected model

## Quick Start (Windows)
1. Setup requirements
- Fast API `uv sync`
- Next.JS `pnpm install` (inside frontend directory)

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
src/
  api.py
  chroma.py
  database.py
  CONFIG.toml
  shared.py
  hybrid_search.py
Start.ps1
frontend/
  app/
  components/
  package.json
frontend_lite
```

## Testing features
- **frontend_lite** - small frontend version without framework dependecies

## Roadmap
- Hybrid retrieval (vector + keyword)
- Config/settings UI
- Improved evaluation and observability
- Optional packaging for non-dev users

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).
See the [LICENSE](./LICENSE) file for details.