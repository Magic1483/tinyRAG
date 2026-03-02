

# Hybrid Search

The RAG retrieve two chunks frm the database
1. Dense retrieval: top-k from vector index
2. Sparse retriveal: top-k from BM23/TF-IDF index over same chunks
3. Fuse results with RRF

**RRF (Reciprocal Rank Fusion)** - formula that combines ranked result lists (e.g. vector search + BM25) using rank positions.


# HyDE

**"Fake answer"** - LLM create fake answer for query user asked and retreive results from the vector DB, using it.
Because of database ncludes answers (not queries) the chance to get back relevant chunks significantly increased with this approach.



