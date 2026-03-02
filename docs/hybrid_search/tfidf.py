import numpy as np
from pprint import pprint

a = """IESG NOTE:
The IRC protocol itself enables several possibilities of transferring
data between clients, and just like with other transfer mechanisms
like email, the receiver of the data has to be careful about how the
data is handled. For more information on security issues with the IRC
protocol, see for example http://www.irchelp.org/irchelp/security/.""".lower().split()

b = """Abstract
The IRC (Internet Relay Chat) protocol is for use with text based
conferencing; the simplest client being any socket program capable of
connecting to the server.""".lower().split()

c = """This document defines the Client Protocol, and assumes that the
reader is familiar with the IRC Architecture [IRC-ARCH].""".lower().split()

docs = [a,b,c]

def tfidf(word,sentence):
    tf = sentence.count(word) / len(sentence)
    print(f'"{word}" tf - {tf:.04}')
    idf = np.log10(len(docs) / sum([1 for d in docs if word in d]))
    print(f'"{word}" weight - {idf:.04}')
    return round(tf*idf,4) # producs of term frequency and term weight

# create all docs vocabulary
vocab = set(a+b+c)

# vectorize query
vec_a = []
vec_b = []
for word in vocab:
    vec_a.append(tfidf(word,a))
    vec_b.append(tfidf(word,b))

pprint(vec_a)

