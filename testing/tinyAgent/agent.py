import toml
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, TypedDict, Union
from urllib.request import Request, urlopen
import requests
from pprint import pprint
import tools
import traceback
import json
import logging

CONFIG = toml.load('CONFIG.toml')

def validate(schema:Dict[str,Any], args: Any) -> bool:
    if not isinstance(args,dict):
        return False
    
    props    = schema.get("properties",{})
    required = schema.get("required",[])

    for k in required:
        if k not in args:
            return False
    
    for k,rule in props.items():
        if k not in args:
            continue

        t = rule.get("type")
        v = args[k]
        if t == "string"    and not isinstance(v,str): 
            return False
        if t == "number"    and not isinstance(v,(int,float)): 
            return False
        if t == "boolean"   and not isinstance(v,bool): 
            return False
        if t == "object"   and not isinstance(v,dict): 
            return False
        if t == "array"     and not isinstance(v,list): 
            return False
    
    return True

def call_llm(goal,history,tools_spec):
    prompt = f"""
You are an autonomous planner that can only respond with valid JSON.

Goal:
{goal}

Available tools (name, description, JSON schema):
{json.dumps(tools_spec)}

Execution history (tool results from previous steps):
{json.dumps(history)}

Rules:
1. Return ONLY one JSON object. No markdown, no comments, no extra text.
2. JSON must match exactly this shape:
{{
  "final": string | null,
  "actions": [
    {{
      "id": "string",
      "tool": "tool_name",
      "args": {{}}
    }}
  ]
}}
3. If the goal is already completed based on history, set:
   "final": "<short completion summary>"
   and "actions": [].
4. If more work is needed, set:
   "final": null
   and provide 1-3 actions.
5. Use only tool names that exist in tools_spec.
6. args must satisfy each tool schema exactly.
7. Never invent fields outside "final" and "actions".
8. When you work with files always check current directory with list files and go deep step by step

Return JSON now.
""".strip()
    resp = requests.post("http://localhost:11434/api/generate",
            json={
                "model": CONFIG['server']['model_name'], 
                "prompt": prompt, "stream": False,
                "format":"json","temperature":0})
    
    data = resp.json()
    return data["response"]


class Action(TypedDict):
    id:str
    tool:str
    args:Dict[str,Any]

class Plan(TypedDict):
    actions: List[Action]
    final: Optional[str]

class ToolResult(TypedDict):
    id:str
    tool:str
    ok:bool
    output: Optional[Any]
    error: Optional[Dict[str,Any]]



def agent_loop(goal:str, max_steps:int = 8, max_actions_per_step:int = 4) -> str:
    history: List[Dict[str,Any]] = []
    tools_spec = tools.tool_manifest()

    for step in range(max_steps):
        try:
            plan = json.loads(call_llm(goal,history,tools_spec))
            print('Provided plan '+str(plan))
        except:
            raise Exception("plan couldn't be parsed")

        final = plan.get("final")
        if final:
            return final
        
        actions = plan.get("actions",[])
        actions = actions[:max_actions_per_step]
        if not actions:
            return "No actions returned and no final."

        results: List[ToolResult] = []

        for a in actions:
            tool_name = a.get("tool")
            if tool_name not in tools.TOOLS.keys():
                results.append({"id":a.get("id","?"),"tool":tool_name,"ok":False,"output":None,
                    "error":{"code":"UNKNOWN_TOOL"}})
                continue
            tool = tools.TOOLS[tool_name]
            
            args = a.get("args",{})
            if not validate(tool.schema,args):
                results.append({"id":a.get("id","?"),"tool":tool_name,"ok":False,"output":None,
                    "error":{"code":"BAD_ARGS"}})
                continue

            try:
                out = tool.execute(args)
                results.append({"id":a.get("id","?"),"tool":tool_name,"ok":True,"output":out,
                    "error":None})
            except Exception as e:
                results.append({"id":a.get("id","?"),"tool":tool_name,"ok":False,"output":None,
                    "error":{"tool":tool_name,"code":"EXEC_ERROR","message":str(e)}})
                traceback.print_exc()

        print('results '+str(results))
        # if results and all(r["ok"] for r in results):
        #     return "Goal completed successfully."
        history.append({"role":"tool_result","results":results})  
    
    return "Stopped: step limit reached"



if __name__ == "__main__":
    print(agent_loop("PLay audio 'INside Job opening' from music folder", max_steps=10))
