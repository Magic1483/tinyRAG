from requests import Session
from dataclasses import dataclass
import json
import csv

session = Session()

@dataclass
class Query:
    question: str
    expected_keywords: list[str]
    expected_doc:  str
    expected_page: int

questions = [
    # --- IRC Specification (RFC 2812) ---
    Query("Describe the NICK command and its error replies",
        ["NICK", "<nickname>", "ERR_NONICKNAMEGIVEN", "ERR_ERRONEUSNICKNAME", "ERR_NICKNAMEINUSE"],
        "rfc2812_IRC_Proto.pdf", 10),
    
    Query("What are the parameters and purpose of the KICK command?",
        ["KICK", "<channel>", "<user>", "[<comment>]", "ERR_CHANOPRIVSNEEDED"],
        "rfc2812_IRC_Proto.pdf", 22),

    # --- SHA-1 Specification (RFC 3174) ---
    Query("List the five initial hash values (H0-H4) used in SHA-1",
        ["67452301", "EFCDAB89", "98BADCFE", "10325476", "C3D2E1F0"],
        "rfc3174_sha1.pdf", 7), # Page 7 contains the initialization constants
        
    Query("Describe the padding process for a message in SHA-1",
        ["padding", "512 bits", "64-bit integer", "0x80", "448"],
        "rfc3174_sha1.pdf", 4),

    # --- XMPP Core (RFC 6120) ---
    Query("Explain the opening of an XML stream in XMPP",
        ["stream:stream", "initiating entity", "receiving entity", "stream header", "version='1.0'"],
        "rfc6120_xmpp_core.txt.pdf", 23),
        
    Query("List common XMPP stream error conditions",
        ["bad-format", "host-unknown", "invalid-namespace", "see-other-host", "urn:ietf:params:xml:ns:xmpp-streams"],
        "rfc6120_xmpp_core.txt.pdf", 52),
        
    Query("Describe the STARTTLS negotiation flow in XMPP",
        ["STARTTLS", "mandatory-to-negotiate", "<proceed/>", "<failure/>", "urn:ietf:params:xml:ns:xmpp-tls"],
        "rfc6120_xmpp_core.txt.pdf", 69)
]

def SendQuery(workspace_id,chat_id,query,k,use_hyde,use_bm25):
    resp = session.post('http://localhost:8000/chat',json={
        "workspace_id":workspace_id,
        "chat_id":chat_id,
        "query":query,
        "k":k,
        "use_hyde":use_hyde,
        "use_bm25":use_bm25
    })
    return resp.json()['content']
def SearchQuery(workspace_id,query,k,use_hyde,use_bm25):
    resp = session.post('http://localhost:8000/search',json={
        "workspace_id":workspace_id,
        "query":query,
        "k":k,
        "use_hyde":use_hyde,
        "use_bm25":use_bm25
    })
    return resp.json()['matches']


def keyword_score(answer:str, expected_keywords:list[str]) -> float:
    """Expected keywords raiting"""
    a = answer.lower()
    hits = sum(1 for kw in expected_keywords if kw.lower() in a)
    return hits / len(expected_keywords)

def hit_at_k(matches:list[dict], gold_doc, gold_page, k=5):
    """Hit count per k chunks"""
    return int(any((
        m.get("meta",{}).get("file_name") == gold_doc and 
        m.get("meta",{}).get("page") == gold_page
        )
        for m in matches[:k]
    ))

def mrr(matches:list[dict], gold_doc, gold_page):
    """How high was first correct chunk ranked"""
    for i,m in enumerate(matches,start=1):
        meta = m.get("meta",{})
        if meta.get("file_name") == gold_doc and meta.get("page") == gold_page:
            return 1.0 / i
    return 0.0


def metrics(answer,matches,golden_doc,golden_page,expected_keywords):
    kw_score     = keyword_score(answer,expected_keywords)
    hits         = hit_at_k(matches,golden_doc,golden_page)
    _mrr         = mrr(matches,golden_doc,golden_page)
    return (kw_score,hits,_mrr)

def main():
    workspace_id    = "4992767c-bc28-4c5a-8148-965267cb9915"
    chat_id         = "d2db2b62-35a4-44b1-949b-3935d53521b5"
    k               = 8
    responses       = {}

    for i,q in enumerate(questions):
        for j,m in enumerate(['vector','vector+bm25','vector+hyde','vector+bm25+hyde']):
            print(f'TEST {i+1}.{j+1}/{len(questions)} "{q.question}" in mode [ {m} ]')

            use_bm25  = 'bm25' in m
            use_hyde  = 'hyde' in m
            answer    = SendQuery(workspace_id,chat_id,q.question,k,use_hyde,use_bm25)
            matches   = SearchQuery(workspace_id,q.question,k,use_hyde,use_bm25)
            metrics_default = metrics(answer,matches,
                q.expected_doc,q.expected_page,q.expected_keywords)
        
            responses[q.question+'_'+m] = {
                "query":q.question,
                "k":k,
                "mode":m,
                "use_bm25":use_bm25,
                "use_hyde":use_hyde,
                "result":answer,
                "matches":matches,
                "kw_score":metrics_default[0],
                "hits":metrics_default[1],
                "mrr":metrics_default[2],
            }

    with open('./results/raw.json','w') as f:
        json.dump(responses,f)
    columns = [
        "question","mode","k",
        "use_bm25","use_hyde",
        "kw_score","hit_at_5","mrr",
        "answer_len"
        ]

    with open("./results/metrics.csv",'w',newline="",encoding="utf-8") as f:
        w = csv.DictWriter(f,fieldnames=columns)
        w.writeheader()
        for r in responses.values():
            w.writerow({
                "question":r['query'],
                "mode":r['mode'],
                "k":r['k'],
                "use_bm25":r['use_bm25'],
                "use_hyde":r['use_hyde'],
                "kw_score":r["kw_score"],
                "hit_at_5":r['hits'],
                "mrr":r['mrr'],
                "answer_len":len(r['result'])
            })

if __name__ == '__main__':
    main()