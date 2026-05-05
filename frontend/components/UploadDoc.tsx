
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"

import { Button } from "./ui/button"
import { Input } from "@/components/ui/input"
import { Plus, Upload } from "lucide-react"
import React, { useState } from "react";
import { API_BASE } from "@/app/api";
import type { ChatMessage } from "./ChatWindow";
import { useAppStore } from "@/app/store";

export type UploadDoc = {
    id: string,
    file_name:string,
    status:"uploaded" | "indexing" | "ready" | "failed" 
}

export function UploadDocument({workspace_id,messages}:
    {
        workspace_id:string,
        messages: ChatMessage[]
    }) {
    
    const [open, setOpen] = React.useState(false);
    const [doc,setDoc] = React.useState<File | null>(null);
    const [documents,setDocuments] = React.useState<UploadDoc[]>([]);

    const wsSettings = useAppStore((s)=>s.workspace_settings[workspace_id]);
    const set_hyde_state  = useAppStore((s)=>s.set_hyde);
    const set_bm25_state  = useAppStore((s)=>s.set_bm25);
    const set_top_k_state = useAppStore((s)=>s.set_top_k);

    const hyde = wsSettings?.use_hyde ?? false;
    const bm25 = wsSettings?.use_bm25 ?? false;
    const topK = wsSettings?.top_k    ?? 20;

    async function loadDocuments() {
            const res = await fetch(`${API_BASE}/docs/${workspace_id}/documents`,{
                cache:"no-store",
            });
            if (!res.ok) return
            const rows: Array<UploadDoc> = await res.json();

            setDocuments(
                rows.map((m)=> ({
                    id: m.id,
                    file_name: m.file_name,
                    status: m.status
                }))
            );
        }

    React.useEffect(()=> {
        loadDocuments();

        
    },[workspace_id])

    React.useEffect(()=>{
        const hasPending = documents.some((d)=>d.status === "uploaded" || d.status === "indexing")
        if (!hasPending) return
        const id = setInterval(loadDocuments,3000)
        return () => clearInterval(id);
    },[documents,workspace_id])

    async function uploadDoc() {
        if (doc === null) return
        if (!doc.name.toLocaleLowerCase().endsWith(".pdf")) return
        if (documents.some((d) => d.file_name === doc.name && d.status !== "failed")) {
            console.error("Document already uploaded")
            return;
        }


        const form = new FormData()
        form.append("file",doc)

        const res = await fetch(
            `${API_BASE}/docs/upload?workspace_id=${encodeURIComponent(workspace_id)}`,
            {
            method: "POST",
            body: form,
            }
        );

        if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
        await res.json();
        setDoc(null)
        await loadDocuments()
    }

    function export_chat() {
        const content = JSON.stringify(messages,null,4)
        const el = document.createElement("a")
        const file = new Blob([content],{'type':"application/json"})
        el.href = URL.createObjectURL(file)
        el.download = 'chat.json'
        document.body.appendChild(el)
        el.click()
        document.body.removeChild(el);
    }

    return (
        <Dialog open={open} onOpenChange={setOpen} >
        <DialogTrigger asChild>
            <Button variant="outline"  size="icon" className="cursor-pointer">
                <Upload className="w-5 h-5"/>
            </Button>
        </DialogTrigger>
        <DialogContent className="lg:w-[70vw] lg:max-w-[1000px] lg:min-h-[40vh] lg:h-fit h-[70vh] p-0" id="12">
            <DialogTitle className="hidden"></DialogTitle>
            
            <div className="grid h-full grid-rows-[1fr_auto] lg:grid-rows-1 lg:grid-cols-[2fr_1fr]">
                
                <div className="min-h-0 p-3 sm:p-4">
                <div className="h-full overflow-auto rounded-md border">
                    <Table className="w-full">
                    <TableHeader className="sticky top-0 z-10 bg-background">
                        <TableRow>
                        <TableHead>Filename</TableHead>
                        <TableHead>Status</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {documents.map((d) => (
                        <TableRow key={d.id}>
                            <TableCell className="max-w-0 truncate text-xs sm:text-sm">{d.file_name}</TableCell>
                            <TableCell className="text-muted-foreground text-xs sm:text-sm">{d.status}</TableCell>
                        </TableRow>
                        ))}
                    </TableBody>
                    </Table>
                </div>
                </div>

                <div className="border-t p-3 md:border-t-0 md:border-l">
                    <div className="space-y-2">
                        <h4 className="leading-none font-medium">Upload new document</h4>
                        <p className="text-muted-foreground text-sm">
                            Only PDF allowed
                        </p>
                    </div>
                    <div className="mt-4 space-y-3">
                        <Input
                            type="file"
                            className="col-span-2 h-16"
                            onChange={(val)=> setDoc(val.target.files?.[0] ?? null)}
                        />
                        <Button 
                        variant={"outline"} 
                        className="w-full cursor-pointer" 
                        onClick={uploadDoc} disabled={!doc}
                        >Upload</Button>

                        <div className="flex flex-row gap-2 font-nroma w-fulll">
                            <Switch id="use_hyde" 
                            onCheckedChange={(e)=>set_hyde_state(e,workspace_id)}
                            checked={hyde}
                            />
                            <Label htmlFor="use_hyde">Use HyDE - fake answer</Label>
                        </div>
                        <div className="flex flex-row gap-2 font-nromal w-full">
                            <Switch id="use_bm25" 
                            onCheckedChange={(e)=>set_bm25_state(e,workspace_id)}
                            checked={bm25}
                            />
                            <Label htmlFor="use_bm25">Use BM25 - text search</Label>
                        </div>
                        <div className="flex flex-row gap-2 font-nromal w-full">
                            <Input className="w-18"  type="number" id="topK" 
                                min={1}
                                max={100}
                                value={topK}
                                onChange={(e)=>{
                                    const val = Number(e.target.value);
                                    set_top_k_state(Number.isFinite(val) && val > 0 ? val : 1, workspace_id);
                                }}/>
                            <Label className="" htmlFor="topK" >Top K</Label>
                        </div>
                        <Button 
                        variant={"outline"} 
                        className="w-full cursor-pointer" 
                        onClick={export_chat}
                        >Export Chat</Button>
                        
                    </div>
                    
                </div>
            </div>
            
        </DialogContent>
        </Dialog>
    )
}
