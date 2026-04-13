import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import uuid

DB_PATH = Path("data/app.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS workspaces (
              id TEXT PRIMARY KEY,
              name TEXT NOT NULL,
              created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS chats (
              id TEXT PRIMARY KEY,
              workspace_id TEXT NOT NULL,
              title TEXT NOT NULL,
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS messages (
              id TEXT PRIMARY KEY,
              chat_id TEXT NOT NULL,
              role TEXT NOT NULL CHECK(role IN ('user','assistant','system')),
              content TEXT NOT NULL,
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS documents (
              id TEXT PRIMARY KEY,
              workspace_id TEXT NOT NULL,
              file_name TEXT NOT NULL,
              stored_path TEXT NOT NULL,
              status TEXT NOT NULL CHECK(status IN ('uploaded','indexing','ready','failed')) DEFAULT 'uploaded',
              error TEXT,
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_chats_workspace ON chats(workspace_id);
            CREATE INDEX IF NOT EXISTS idx_messages_chat ON messages(chat_id, created_at);
            CREATE INDEX IF NOT EXISTS idx_docs_workspace ON documents(workspace_id);
            """
        )

def fetch_workspaces_with_chats() -> List[Dict[str, Any]]:
    with get_conn() as conn:
        wss = conn.execute("SELECT id, name FROM workspaces ORDER BY created_at DESC").fetchall()
        out: List[Dict[str, Any]] = []
        for ws in wss:
            chats = conn.execute(
                "SELECT id, title FROM chats WHERE workspace_id=? ORDER BY created_at DESC",
                (ws["id"],),
            ).fetchall()
            out.append(
                {
                    "id": ws["id"],
                    "name": ws["name"],
                    "chats": [{"id": c["id"], "name": c["title"]} for c in chats],
                }
            )
        return out

def create_workspace(name: str) -> str:
    ws_id = str(uuid.uuid4())
    with get_conn() as conn:
        conn.execute("INSERT INTO workspaces(id, name) VALUES(?,?)", (ws_id, name))
    return ws_id

def create_chat(workspace_id: str, title: str) -> str:
    chat_id = str(uuid.uuid4())
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO chats(id, workspace_id, title) VALUES(?,?,?)",
            (chat_id, workspace_id, title),
        )
    return chat_id

def delete_chat(chat_id:str) -> None:
    with get_conn() as conn:
        conn.execute("DELETE from chats WHERE id=?",(chat_id,))

def delete_workspace(workspace_id:str) -> None:
    with get_conn() as conn:
        conn.execute("DELETE from workspaces WHERE id=?",(workspace_id,))

def add_message(chat_id: str, role: str, content: str) -> str:
    msg_id = str(uuid.uuid4())
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO messages(id, chat_id, role, content) VALUES(?,?,?,?)",
            (msg_id, chat_id, role, content),
        )
    return msg_id

def get_recent_messages(chat_id: str, limit: int = 12) -> List[Dict[str, str]]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, role, content FROM messages WHERE chat_id=? ORDER BY created_at DESC LIMIT ?",
            (chat_id, limit),
        ).fetchall()
    # reverse into chronological order
    return [{"id":r["id"] ,"role": r["role"], "content": r["content"]} for r in reversed(rows)]


# documents
def get_documents(workspace_id: str) -> List[Dict[str, str]]:
    with get_conn() as conn:
        print(workspace_id)
        rows = conn.execute(
            "SELECT file_name, status, id FROM documents WHERE workspace_id=? ORDER BY created_at DESC",
            (workspace_id,),
        ).fetchall()
    return [{"file_name": r["file_name"], "status": r["status"],"id":r['id'] } for r in reversed(rows)]

def insert_documents(id,workspace_id,file_name, storead_path,status,error ) -> List[Dict[str, str]]:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO documents (id, workspace_id, file_name, stored_path, status, error) VALUES(?,?,?,?,?,?)",
            (id,workspace_id,file_name, storead_path,status,error))

def update_document_status(doc_id:str, status:str, error:str = None):
    with get_conn() as conn:
        if not error:
            conn.execute(
                "UPDATE documents set status = ? where id = ? ",
                (status,doc_id))
        else:
            conn.execute(
                "UPDATE documents set status = ?, error = ? where id = ?  ",
                (status,error,doc_id))
            
