
from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from typing import Dict, List

WORD_RE = re.compile(r"[a-zA-Z0-9_]{2,}")


def tokenize(text:str) -> list[str]:
    """Split text into words"""
    return [t.lower() for t in WORD_RE.findall(text or "")]

def bm25_search(
        query:str,
        docs: List[Dict],
        k: int = 20,        # count of chunks
        k1:float = 1.5,     # term frequency control, higher k - repeated term occurrences matter more.
        b:float = 0.75      # document lenght control, b=0 ignore length, b=1 full length nomalization
) -> List[Dict]:
    if not docs: return []

    q_terms = set(tokenize(query))
    if not q_terms: return []

    doc_tokens: Dict[str,List[str]] = {}    # tokens
    doc_tf:Dict[str,Counter]        = {}    # term frequency
    df        = defaultdict(int)            # document frequency
    total_len = 0

    # calculate term frequency in each document
    for d in docs:
        doc_id              = d['id']
        tokens              = tokenize(d.get("text",""))
        doc_tokens[doc_id]  = tokens
        doc_tf[doc_id]      = Counter(tokens)
        total_len          += len(tokens)
        for term in set(tokens): 
            df[term] += 1 # calculate count of chunks that contains query/term
    
    n_docs = max(len(docs),1)
    avg_dl = total_len / n_docs if total_len else 1.0 # average chunk length
    scored: List[tuple[float,Dict]] = []

    for d in docs:
        doc_id  = d['id']
        tokens  = doc_tokens[doc_id]
        tf      = doc_tf[doc_id]
        dl      = max(len(tokens),1) # doc length
        score   = 0.0

        for term in q_terms:
            f = tf.get(term,0)
            if f == 0: continue

            # calculate bm25 score
            n_qi    = df.get(term,0)
            idf     = math.log(1 + (n_docs - n_qi + 0.5) / (n_qi + 0.5))
            denom   = f + k1 * (1 - b + b*dl / avg_dl)
            score  += idf * (f * (k1 + 1) / denom)

        if score > 0.0:
            scored.append((
                score,
                {
                    "id":d['id'],
                    "text": d.get("text",""),
                    "meta": d.get("meta",{}),
                    "bm25_score": score
                }
            ))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [h for _,h in scored[:k]]


def rrf_fuse(result_list: List[List[Dict]], top_k: int = 5, rrf_k: int = 60) -> List[Dict]:
    fused = defaultdict(float)  # accumulate contributions across retrieves for same doc_id
    by_id: Dict[str,Dict] = {}

    for result in result_list:
        for rank,item in enumerate(result,start=1):
            doc_id = item['id']
            fused[doc_id] += 1.0 / (rrf_k + rank)
            if doc_id not in by_id:
                by_id[doc_id] = dict(item)
    
    ranked = sorted(fused.items(),key=lambda x: x[1], reverse=True)
    out: List[Dict] = []
    for doc_id,score in ranked[:top_k]:
        item = dict(by_id[doc_id])
        item["rrf_score"] = score
        out.append(item)
    
    return out
    