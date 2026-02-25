from __future__ import annotations


from pypdf import PdfReader
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class Chunk:
    chunk_id: str
    text: str
    start_char: int
    end_char: int

def clean_text(s:str) -> str:
    s = s.replace("\x00", "")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

def parse_pdf_to_pages(path:Path) -> Dict:
    reader = PdfReader(str(path))
    pages: List[str] = []

    for i,page in enumerate(reader.pages):
        t = page.extract_text() or ""
        t = clean_text(t)
        pages.append(t)
    return pages

def chunk_text(text:str, chunk_size:int = 3500, overlap: int = 400) -> List[Chunk]:
    text = text.strip()
    if not text: return []

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk size")
    
    chunks: List[Chunk] = []
    step = chunk_size - overlap
    i = 0
    chunk_idx = 0
    while i < len(text):
        start = i
        end = min(i + chunk_size,len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(
                Chunk(
                    chunk_id=f'chunk_{chunk_idx:05d}',
                    text=chunk,
                    start_char=start,
                    end_char=end
                )
            )
            chunk_idx += 1
        i += step
    return chunks



