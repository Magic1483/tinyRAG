from fastapi import FastAPI,File,UploadFile,Query,BackgroundTasks
from fastapi.responses import StreamingResponse,FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional


import uuid
import json

import database
import shared
from rag_service import RagService
from shared import UPLOAD_DIR,CONFIG,PERSIST_DIR


app = FastAPI()
origins = [
    f"http://localhost:{CONFIG['server_port']}",
    f"http://127.0.0.1:{CONFIG['server_port']}",
    f"http://{CONFIG['server_ip']}:{CONFIG['server_port']}",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex=r"^http://192\.168\.\d{1,3}\.\d{1,3}(:\d+)?$",
)

# GLOBALS
UPLOAD_DIR.mkdir(parents=True,exist_ok=True)
rag_service = RagService(database)



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
    background_tasks.add_task(rag_service.process_document,doc_id,workspace_id,file.filename,pdf_path)
    return {"doc_id":doc_id,"status":"uploaded"} 


# -- chats
@app.get("/chats/{chat_id}/messages")
async def get_chat_messages(chat_id:str, limit:int = 200):
    return database.get_recent_messages(chat_id,limit=limit)


@app.post("/chat")
async def chat(payload:dict):
    workspace_id = payload.get("workspace_id")
    chat_id = payload.get("chat_id")
    query = payload.get("query")
    k = int(payload.get("k",5))
    use_hyde = payload.get("use_hyde",False)
    use_bm25 = payload.get("use_bm25",False)
    print(f"CHAT top_k:{k} hyde:{use_hyde} bm25:{use_bm25}")

    if not query or not workspace_id or not chat_id:
        return {"error": "Missing query/workspace_id/chat_id"}
    
    database.add_message(chat_id,"user",query)
    history = database.get_recent_messages(chat_id,limit=10)

    hits = await rag_service.search(workspace_id,query,k=k,use_hyde=use_hyde,use_bm25=use_bm25)

    prompt = rag_service.build_prompt(query,hits,history)
    answer = await rag_service.generate_answer(prompt)
    citations = [
            {"file_name":h['meta']['file_name'], "page":h['meta']['page']} 
            for h in hits]
    
    if answer:
        database.add_message(chat_id,"assistant",answer,metadata={
                "citations":citations,
                "use_hyde":use_hyde,
                "use_bm25":use_bm25,
                "top_k":k
            })

    return {
        "content":answer,
        "role":"assistant"
    }


@app.post("/chat/stream")
async def chat_stream(payload:dict):
    workspace_id    = payload.get("workspace_id")
    chat_id         = payload.get("chat_id")
    query           = payload.get("query")
    k               = int(payload.get("k",5))
    use_hyde        = payload.get("use_hyde",False)
    use_bm25        = payload.get("use_bm25",False)

    print(f"CHAT_STREAM top_k:{k} hyde:{use_hyde} bm25:{use_bm25}")
    if not query or not workspace_id or not chat_id:
        return {"error": "Missing query/workspace_id/chat_id"}
    
    database.add_message(chat_id,"user",query) # no metadata
    history = database.get_recent_messages(chat_id,limit=10)

    hits = await rag_service.search(workspace_id,query,
                                    k=k,use_hyde=use_hyde,use_bm25=use_bm25)

    prompt = rag_service.build_prompt(query,hits,history)
    async def event_gen():
        citations = [
            {"file_name":h['meta']['file_name'], "page":h['meta']['page']} 
            for h in hits
        ]
        yield f"event: citations\ndata: {json.dumps(citations)}\n\n"

        full = []
        async for token in rag_service.generate_answer_stream(prompt):
            full.append(token)
            yield f"event: token\ndata: {json.dumps({'text':token})}\n\n"
        
        answer = "".join(full).strip()
        if answer:
            database.add_message(chat_id,"assistant",answer,metadata={
                "citations":citations,
                "use_hyde":use_hyde,
                "use_bm25":use_bm25,
                "top_k":k
            })

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
    rag_service.delete_workspace_index(workspace_id)
    return {"ok": True}


# -- settings
@app.get("/config")
async def get_config():
    return {
        "embedded_model":CONFIG['chroma']['EMBED_MODEL'],
        "model":         CONFIG['server']['model_name']
        }


# -- debug
@app.post("/search")
async def search(payload:dict):
    query: Optional[str] = payload.get("query")
    workspace_id: Optional[str] = payload.get("workspace_id")
    k:int = int(payload.get("k",5))
    use_hyde = payload.get("use_hyde",False)
    use_bm25 = payload.get("use_bm25",False)

    if not query or not workspace_id:
        return {"err":"missing query/workspace_id"}
    
    hits = await rag_service.search(workspace_id,query,k,use_hyde,use_bm25)
    return {"query":query,"k":k,"matches":hits}


# -- static serve
FRONTEND_DIR = shared.resource_path("frontend/out")
app.mount("/_next",StaticFiles(directory=FRONTEND_DIR / "_next"),name="next_static")

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    path = FRONTEND_DIR / full_path
    if path.is_file():
        return FileResponse(path)

    html_path = FRONTEND_DIR / f"{full_path}.html"
    if html_path.is_file():
        return FileResponse(html_path)

    return FileResponse(FRONTEND_DIR / "index.html")
