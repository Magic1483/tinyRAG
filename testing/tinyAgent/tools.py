from typing import Any, Callable, Dict, List, Optional, TypedDict, Union
from dataclasses import dataclass
import os
import subprocess
import shutil
import json

WORKSPACE_DIR = "WSDIR"

@dataclass
class Tool:
    name:str
    description: str
    schema: Dict[str,Any]
    execute: Callable[[Dict,str],Any]

def ensure_workspace():
    os.makedirs(WORKSPACE_DIR,exist_ok=True)


def tool_print(args:Dict):
    text = args.get("text")
    print(text)
    return {"ok":True,"printed":text}
    
def tool_read_file(args:Dict):
    ensure_workspace()
    path = args.get("path")
    
    with open(path,'r') as f:
        return {"path":path,"content":f.read()[:5000]}

def tool_listdir(args:Dict):
    ensure_workspace()
    path = args.get("path")
    
    full = os.path.abspath(os.path.join(WORKSPACE_DIR, path))
    if not os.path.exists(full):
        raise ValueError(f"path not exists {full}")
    
    return {"path":full,"files":os.listdir(full)}
    
def tool_write_file(args:Dict):
    ensure_workspace()
    path    = args.get("path")
    content = args.get("content")

    full = os.path.abspath(os.path.join(WORKSPACE_DIR,path))
        
    os.makedirs(os.path.dirname(full),exist_ok=True)
    with open(path,'w') as f:
        f.write(content)
    return {"ok":True,"path":path}


def tool_play_audio(args:Dict):
    ensure_workspace()
    path    = args.get("path")
    if not path: raise ValueError("missing path")

    full = os.path.abspath(os.path.join(WORKSPACE_DIR, path))
    if not os.path.exists(full):
        raise ValueError(f"path not exists {full}")
    
    if shutil.which("mpv") is None:
        raise RuntimeError("mpv not found in PATH")
    
    cmd = ['mpv',full]

    proc = subprocess.Popen(cmd)
    return {"ok":True,"path":full,"pid":proc.pid} 



TOOLS: Dict[str,Tool] = {
    "read_file": Tool(
        name="read_file",
        description="read file content",
        schema={
            "type": "object",
            "required": ["path"],
            "properties": {"path":{"type":"string"}},
        },
        execute=tool_read_file
    ),
    "print": Tool(
        name="print",
        description="print console output",
        schema={
            "type": "object",
            "required": ["text"],
            "properties": {"text":{"type":"string"}},
        },
        execute=tool_print
    ),
    "listdir": Tool(
        name="listdir",
        description="list files in the directory",
        schema={
            "type": "object",
            "required": ["path"],
            "properties": {"path":{"type":"string"}},
        },
        execute=tool_listdir
    ),
    "write_file": Tool(
        name="write_file",
        description="write content into file",
        schema={
            "type": "object",
            "required": ["path","content"],
            "properties": {
                "path":{"type":"string"},
                "content":{"type":"string"},
            },
        },
        execute=tool_write_file
    ),
    "play_audio": Tool(
        name="play_audio",
        description="play audio file with MPV",
        schema={
            "type": "object",
            "required": ["path"],
            "properties": {
                "path":{"type":"string"},
            },
        },
        execute=tool_play_audio
    )
}

def tool_manifest() -> str:
    return [
        {"name":t.name,"schema":t.schema,"description":t.description}
        for t in TOOLS.values()]