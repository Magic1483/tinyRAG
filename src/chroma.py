from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from chuck_text import Chunk




def load_chunks(chunks_root:Path) -> List[Dict]:
    docs = [p for p in chunks_root.iterdir() if p.is_dir()]
    if not docs:
        raise SystemExit(f"No chunked docs found in {chunks_root.resolve()}")

    all_chunks: List[Dict]     = []
    for doc_dir in sorted(docs):
        doc_id = doc_dir.name
        chunk_files = sorted(doc_dir.glob("chunk_*.txt"))
        for cf in chunk_files:
            chunk_id = cf.stem
            text = cf.read_text(encoding='utf-8').strip()
            if not text: continue
            
            all_chunks.append({"doc_id":doc_id,"chunk_id":chunk_id,"text":text})
        
    if not all_chunks:
        raise SystemExit("No chunks loaded (empty files)")
    return all_chunks

class ChromaStore:
    def __init__(self,persist_dir):
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )

    def chroma_upsert(self, collection_name:str, doc_id:str,original_name:str, 
        chunks:List[Chunk], embeddings:List[List[float]]) -> int:
        ids = [f'{doc_id}:{c.chunk_id}' for c in chunks]
        metadatas = [
                {
                    "doc_id": doc_id, 
                    "file_name" : original_name,
                    "chunk_id": c.chunk_id,
                    "start_char": c.start_char,
                    "end_char": c.end_char
                } 
                for c in chunks
            ]
        documents = [c.text for c in chunks]

        collection = self.client.get_or_create_collection(collection_name)
        collection.upsert(ids,embeddings,metadatas,documents)
        return len(ids)
    
    def delete(self,collection_name:str):
        try:
            self.client.delete_collection(collection_name)
        except: pass


    def chroma_search(self, collection_name:str, query_embedding:List[float],k:int = 5,where=None):
        collection = self.client.get_or_create_collection(collection_name)
        res = collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents","metadatas","distances"],
            where=where
            )
        out = []
        for i in range(len(res["ids"][0])):
            out.append({
                "id":res['ids'][0][i],
                "distance":res['distances'][0][i],
                "text":res['documents'][0][i],
                "meta":res['metadatas'][0][i],
            })
        return out

