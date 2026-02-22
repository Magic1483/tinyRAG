import {
  Popover,
  PopoverContent,
  PopoverDescription,
  PopoverHeader,
  PopoverTitle,
  PopoverTrigger,
} from "@/components/ui/popover"
import { Button } from "./ui/button"
import { Input } from "@/components/ui/input"
import { Plus } from "lucide-react"
import React from "react";
import { Option } from "./Option";
import { API_BASE } from "@/app/api";

export function NewChat({workspace_id,onCreated,onWorkspaceDeleted}: {
    workspace_id:string,
    onCreated: (chat: {id:string;name:string}) => void,
    onWorkspaceDeleted: (workspace_id:string) => void
}) {

    const [open, setOpen] = React.useState(false);
    const [chat,setChat] = React.useState("");
    async function createChat() {
        if (!chat) return
        const name = chat.trim()

        const res = await fetch(`${API_BASE}/workspaces/${workspace_id}/chats`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name }),
        });

        if (!res.ok) throw new Error(`Create chat failed: ${res.status}`);
        const created = await res.json();
        onCreated({id:created.id, name: created.name})
        setChat("")
        setOpen(false)
    }

    return (
        <Popover open={open} onOpenChange={setOpen}>
            <div className="font-semibold  cursor-pointer inline-flex h-9 w-full items-center justify-between gap-2 rounded-md border bg-background px-3 text-sm shadow-xs transition-colors hover:bg-accent hover:text-accent-foreground">
                <PopoverTrigger asChild>
                <span >New Chat</span>
                </PopoverTrigger>
                <Option
                    workspace_id={workspace_id}
                    onWorkspaceDeleted={onWorkspaceDeleted}
                />
            </div>
        
        <PopoverContent align="start">
            <div className="grid gap-4">
                <div className="space-y-2">
                    <h4 className="leading-none font-medium">New Chat</h4>
                    <p className="text-muted-foreground text-sm">
                    Set name for a new chat
                    </p>
                </div>
                <div className="grid gap-2">
                    <Input
                        id="width"
                        onChange={(val)=> setChat(val.target.value)}
                        className="col-span-2 h-8"
                        onKeyDown={(e)=>{
                            if (e.key === "Enter") {
                                e.preventDefault();
                                void createChat();
                            }
                        }}
                    />
                </div>
                <Button variant={"outline"} className="cursor-pointer" onClick={()=>{createChat()}}>Start</Button>
            </div>
        </PopoverContent>
        </Popover>
    )
}

export function NewWorkspace({onCreated}:
    {onCreated: (chat: {id:string;name:string}) => void,}) {
    
    const [open, setOpen] = React.useState(false);
    const [ws,setWs] = React.useState("");
    async function createWs() {
        if (!ws) return
        const name = ws.trim()

        const res = await fetch(`${API_BASE}/workspaces`,{
            method:"POST",
            headers: { "Content-Type": "application/json" },
            body:JSON.stringify({name})
        })

        if (!res.ok) throw new Error(`Create workspace failed: ${res.status}`);
        const created = await res.json();
        onCreated({id:created.id, name:created.name});
        setWs("")
        setOpen(false)
    }

    return (
        <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
            <Button variant="outline"  size="icon" className="cursor-pointer h-8 w-8">
                <Plus className="text-foreground h-4 w-4" />
            </Button>
        </PopoverTrigger>
        <PopoverContent align="start">
            <div className="grid gap-4">
                <div className="space-y-2">
                    <h4 className="leading-none font-medium">New Workspace</h4>
                    <p className="text-muted-foreground text-sm">
                    Set name for a new workspace
                    </p>
                </div>
                <div className="grid gap-2">
                    <Input
                        id="width"
                        className="col-span-2 h-8"
                        onChange={(val)=>setWs(val.target.value)}
                        onKeyDown={(e)=>{
                            if (e.key === "Enter") {
                                e.preventDefault();
                                void createWs();
                            }
                        }}
                    />
                </div>
                <Button variant={"outline"} className="cursor-pointer" onClick={()=>createWs()}>Start</Button>
            </div>
        </PopoverContent>
        </Popover>
    )
}
