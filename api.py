
from fastapi import FastAPI,File,UploadFile,Query,BackgroundTasks,HTTPException
from fastapi.responses import StreamingResponse
import uuid
from pathlib import Path
from sentence_transformers import SentenceTransformer
from chroma import ChromaStore
from chuck_text import parse_pdf_to_pages,clean_text,chunk_text
import aiohttp
import json
from typing import Optional,AsyncIterator
import database
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import shared

CONFIG = shared.get_config()
UPLOAD_DIR  = Path(CONFIG['server']['upload_path'])
MODEL_NAME  = CONFIG['server']['model_name']

OLLAMA_URL = "http://localhost:11434/api/generate"

PERSIST_DIR = CONFIG['chroma']['PERSIST_DIR']
EMBED_MODEL = CONFIG['chroma']['EMBED_MODEL']

CHUNK_SIZE_CHARS = 3500
CHUNK_OVERLAP_CHARS = 400


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR.mkdir(parents=True,exist_ok=True)

model = SentenceTransformer(CONFIG['chroma']['EMBED_MODEL'])
store = ChromaStore(PERSIST_DIR)


async def generate_answer_stream(prompt:str) -> AsyncIterator:
    timeout = aiohttp.ClientTimeout(total=300)
    session =  aiohttp.ClientSession(timeout=timeout)

    response = await session.post(
        OLLAMA_URL,
        json={"model":MODEL_NAME,"prompt":prompt,"stream":True}
    )

    async for raw in response.content:
        line = raw.decode('utf-8').strip()
        if not line: continue

        obj = json.loads(line)

        token = obj.get("response","")
        if token: 
            yield token
        
        if obj.get("done"): 
            break

    await session.close()

async def generate_answer(prompt: str) -> str:
    timeout = aiohttp.ClientTimeout(total=180)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return data["response"]


def build_prompt(query:str, chunks:list, history:list) -> str:
    context_blocks = [f"[{i}] {c['text']}" for i,c in enumerate(chunks)]
    context_text = "\n\n".join(context_blocks)

    history_text = ""
    if history:
        lines = []
        for m in history:
            role = m["role"]
            lines.append(f"{role.upper()}: {m['content']}")
        history_text = "\n".join(lines)

    return f"""
You are a the best LLM in the world
Answer ONLY using the provided context.
If the answer is not in the context, say you don't know.

Conversation so far:
{history_text}

Context:
{context_text}

Question:
{query}

Answer:
"""


async def process_document(doc_id:str, workspace_id:str, original_name:str, pdf_path:Path):
    try:
        database.update_document_status(doc_id,"indexing") 

        pages = await asyncio.to_thread(parse_pdf_to_pages,pdf_path)
        full_text = clean_text("\n\n".join(pages))
        chunks = chunk_text(full_text,CHUNK_SIZE_CHARS,CHUNK_OVERLAP_CHARS)
        if not chunks:
            database.update_document_status(doc_id,"failed","no chunks")
            return
        
        texts = [c.text for c in chunks]
        vectors = await asyncio.to_thread(
            lambda: model.encode(texts, normalize_embeddings=True, batch_size=32).tolist()
        )
        await asyncio.to_thread(
            store.chroma_upsert, workspace_id, doc_id, original_name, chunks, vectors
        )

        database.update_document_status(doc_id,"ready")
    except Exception as e:
        database.update_document_status(doc_id,"failed",str(e))







@app.on_event("startup")
def _startup():
    database.init_db()

@app.get("/health")
def health():
    return {"ok":True}

# -- workspaces
@app.get("/workspaces")
async def get_workspaces():
    return database.fetch_workspaces_with_chats()

@app.post("/workspaces")
async def new_workspace(payload:dict):
    name = (payload.get("name") or "").strip()
    if not name:
        return {"err":"Missing workspace name"}
    ws_id = database.create_workspace(name)
    return {"id":ws_id,"name":name}

# -- chat
@app.post("/workspaces/{workspace_id}/chats")
async def new_chat(workspace_id:str,  payload:dict):
    name = (payload.get("name") or "New Chat").strip()
    chat_id = database.create_chat(workspace_id,name)
    return {"id":chat_id,"name":name,"workspace_id":workspace_id}

@app.get("/docs/{workspace_id}/documents")
async def get_documents(workspace_id: str):
    if not workspace_id: 
        return {"err":"workspace missing"}
    
    return database.get_documents(workspace_id)


# -- docs
@app.post("/docs/upload")
async def upload_doc(
    background_tasks: BackgroundTasks,
    workspace_id: str = Query(...),
    file: UploadFile = File(...),
):
    if not file.filename or  not file.filename.lower().endswith(".pdf"):
        return {"err":"Only PDF allowed for now"}
    
    doc_id = str(uuid.uuid4())
    pdf_path = UPLOAD_DIR / f'{doc_id}.pdf'
    pdf_path.write_bytes(await file.read())

    database.insert_documents(doc_id,workspace_id,file.filename,str(pdf_path),"uploaded","")
    background_tasks.add_task(process_document,doc_id,workspace_id,file.filename,pdf_path)
    return {"doc_id":doc_id,"status":"uploaded"} 



# -- chats
@app.get("/chats/{chat_id}/messages")
async def get_chat_messages(chat_id:str, limit:int = 200):
    return database.get_recent_messages(chat_id,limit=limit)

@app.post("/chat/stream")
async def chat_stream(payload:dict):
    workspace_id = payload.get("workspace_id")
    chat_id = payload.get("chat_id")
    query = payload.get("query")
    k = int(payload.get("k",5))

    if not query or not workspace_id or not chat_id:
        return {"error": "Missing query/workspace_id/chat_id"}
    
    database.add_message(chat_id,"user",query)
    history = database.get_recent_messages(chat_id,limit=10)

    qvec = model.encode([query],normalize_embeddings=True)[0].tolist()
    hits = store.chroma_search(workspace_id,qvec,k=k)

    prompt = build_prompt(query,hits,history)

    async def event_gen():
        citation = [
            {"file_name":h['meta']['file_name'], "chunk_id":h['meta']['chunk_id']} 
            for h in hits
        ]
        yield f"event: citations\ndata: {json.dumps(citation)}\n\n"

        full = []
        async for token in generate_answer_stream(prompt):
            full.append(token)
            yield f"event: token\ndata: {json.dumps({'text':token})}\n\n"
        
        answer = "".join(full).strip()
        if answer:
            database.add_message(chat_id,"assistant",answer)

        yield "event: done\ndata: {}\n\n"
    
    return StreamingResponse(event_gen(),media_type="text/event-stream")

# -- delete
@app.delete("/chats/{chat_id}")
async def remove_chat(chat_id: str):
    database.delete_chat(chat_id)
    return {"ok": True}

@app.delete("/workspaces/{workspace_id}")
async def remove_workspace(workspace_id: str):
    database.delete_workspace(workspace_id)
    store.delete(workspace_id)
    return {"ok": True}

# -- settings
@app.get("/config")
async def get_config():
    return {
        "embedded_model":CONFIG['chroma']['EMBED_MODEL'],
        "model":CONFIG['server']['model_name']
        }

# -- debug
@app.post("/search")
async def search(payload:dict):
    query: Optional[str] = payload.get("query")
    workspace_id: Optional[str] = payload.get("workspace_id")
    k:int = int(payload.get("k",5))

    if not query or not workspace_id:
        return {"err":"missing query/workspace_id"}
    
    qvec = model.encode([query],normalize_embeddings=True)[0].tolist()
    hits = store.chroma_search(workspace_id,qvec,k=k)

    return {"query":query,"k":k,"matches":hits}