
a = """Abstract
The IRC (Internet Relay Chat) protocol is for use with text based
conferencing."""

b = """Document defines the Client Protocol, and assumes that the
reader is familiar with the IRC Architecture [IRC-ARCH]."""

c = """This document defines the Client Protocol, and assume that
reader familiar with the IRC Architecture """

from sentence_transformers import SentenceTransformer

model = SentenceTransformer('BAAI/bge-small-en-v1.5')
sentence_embeddings = model.encode([a,b,c])

from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

scores = np.zeros((sentence_embeddings.shape[0],sentence_embeddings.shape[0]))
for i in range(sentence_embeddings.shape[0]):
    scores[i,:] = cosine_similarity(
        [sentence_embeddings[i]],
        sentence_embeddings
    )[0]

print(scores)