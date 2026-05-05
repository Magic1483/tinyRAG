import asyncio
import json
from pathlib import Path
from typing import AsyncIterator
from sentence_transformers import SentenceTransformer
import aiohttp

from hybrid_search import bm25_search,rrf_fuse
from chuck_text import parse_pdf_to_pages,clean_text,chunk_text
from chroma import ChromaStore
from shared import CHUNK_OVERLAP_CHARS, CHUNK_SIZE_CHARS, MODEL_NAME, OLLAMA_URL,CONFIG,DATA_PATH,PERSIST_DIR


class RagService:
    def __init__(self,database) -> None:
        self.database   = database # db module
        # chromaDB instance
        self.store      = ChromaStore(PERSIST_DIR)
        # model instance
        self.model      = SentenceTransformer(
            CONFIG['chroma']['EMBED_MODEL'],
            cache_folder=str(DATA_PATH / "models"))   

    def build_prompt(self,query:str, chunks:list, history:list) -> str:
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

    def build_hyde_prompt(self,query:str) -> str:
        return f"""
    Write a concise hypothetical answer passage that could appear in relevant documents.
    Return only passage text. Use neutral generic wording, no invented facts, no numbers unless in query.

    Question:
    {query}

    Passage:
    """

    async def hybrid_search(self,workspace_id:str, query:str, 
        query_embedding:list[float],k:int=5, use_hyde=True,use_bm25=True
        ) -> list[dict]:
        """
        Hybrid search: vector candidates from chroma + lexical overlap rerank
        1. Get all collection from chrome
        2. Search with BM25
        3. append results to others
        """
        candidate_k = max(k*4, 20)
        dense_hits = self.store.chroma_search(workspace_id,query_embedding,k=candidate_k)
        lists = [dense_hits]

        if use_bm25:
            all_docs = self.store.chrome_all(workspace_id)
            sparse_list = bm25_search(query,all_docs,k=candidate_k)
            lists.append(sparse_list)
        
        if use_hyde:
            hyde_passage = await self.generate_hyde_passage(query)
            print('fake answer is ',hyde_passage)
            if hyde_passage:
                hyde_vec = self.model.encode([hyde_passage], normalize_embeddings=True)[0].tolist()
                hyde_hits = self.store.chroma_search(workspace_id,hyde_vec,k=candidate_k)
                lists.append(hyde_hits)
        
        return rrf_fuse(lists, top_k=k)

    async def process_document(self,doc_id:str, workspace_id:str, original_name:str, pdf_path:Path):
        try:
            self.database.update_document_status(doc_id,"indexing") 

            pages = await asyncio.to_thread(parse_pdf_to_pages,pdf_path)
            all_chunks = []
            for i, page_text in enumerate(pages,start=1):
                page_chunks = chunk_text(page_text,i,CHUNK_SIZE_CHARS,CHUNK_OVERLAP_CHARS)
                all_chunks.extend(page_chunks) 
            
            texts = [c.text for c in all_chunks]
            vectors = await asyncio.to_thread(
                lambda: self.model.encode(texts, normalize_embeddings=True, batch_size=32).tolist()
            )
            await asyncio.to_thread(
                self.store.chroma_upsert, workspace_id, doc_id, original_name, all_chunks, vectors
            )

            self.database.update_document_status(doc_id,"ready")
        except Exception as e:
            print('error upload doc',e)
            self.database.update_document_status(doc_id,"failed",str(e))
    
    async def search(self,workspace_id:str, query:str,k:int,use_hyde:bool,use_bm25:bool):
        qvec = self.model.encode([query],normalize_embeddings=True)[0].tolist()
        return await self.hybrid_search(workspace_id,query,
                                        qvec,
                                        k=k,
                                        use_hyde=use_hyde,
                                        use_bm25=use_bm25)

    async def generate_answer_stream(self,prompt:str) -> AsyncIterator:
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

            if token:               yield token
            if obj.get("done"):     break
        await session.close()

    async def generate_answer(self,prompt: str) -> str:
        timeout = aiohttp.ClientTimeout(total=180)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                OLLAMA_URL,
                json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return data["response"]
            await session.close()

    async def generate_hyde_passage(self,query:str) -> str:
        try:                return (await self.generate_answer(self.build_hyde_prompt(query))).strip()
        except Exception:   return ""

    def delete_workspace_index(self,workspace_id):
        """Delete workspace from ChromaDB"""
        self.store.delete(workspace_id)