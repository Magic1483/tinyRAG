"use client"

import * as React from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { UploadDocument } from "./UploadDoc";
import { MarkdownMessage } from "./MarkdownMessage";
import { ChatMessages } from "./ChatMessages";
import { makeId } from "@/app/idGenerator";
import { API_BASE } from "@/app/api";

type ChatMessage = {
    id: string,
    role: "user" | "assistant",
    content:string
}

type Citation = {
    file_name: string,
    page: string
}


export function ChatWindow({
    workspace_id,
    chat_id,
}: {
    workspace_id: string,
    chat_id:string
}) {
    const [messages,setMessages] = React.useState<ChatMessage[]>([]);
    const [input,setInput]  = React.useState("");
    const [isSending,setIsSending] = React.useState(false);
    const [citations,setCitations] = React.useState<Citation[]>([]);
    
    const bottomRef = React.useRef<HTMLDivElement | null>(null);
    const pendingRef = React.useRef<string | null>("");
    const flushTimerRef = React.useRef<number | null>(null);
    
    const renderedMessages = React.useMemo(() => messages.slice(-50), [messages]);

    React.useEffect(()=>{
        bottomRef.current?.scrollIntoView({behavior:"smooth"});
    },[messages]);


    React.useEffect(()=> {
        async function loadMessages() {
            const res = await fetch(`${API_BASE}/chats/${chat_id}/messages?limit=200`,{
                cache:"no-store",
            });
            if (!res.ok) return
            const rows: Array<ChatMessage> = await res.json();

            setMessages(
                rows.map((m)=> ({
                    id:m.id,
                    role: m.role,
                    content:m.content,
                }))
            );
            setCitations([]);
        }

        loadMessages();
    },[chat_id])


    function scheduleFlush(assistantId:string) {
        if (flushTimerRef.current != null) return
        flushTimerRef.current = window.setTimeout(()=>{
            const chunk = pendingRef.current;
            pendingRef.current = "";
            flushTimerRef.current = null;
            if (!chunk) return
            setMessages((prev)=>
                prev.map((msg)=>
                    msg.id === assistantId ? {...msg,content:msg.content+chunk} : msg))
        },40)
    }

    async function send() {
        const text = input.trim();
        if (!text || isSending) return;


        let use_hyde:boolean = false
        if (localStorage.getItem("use_hyde_"+workspace_id) === "true") use_hyde = true

        let use_bm25 = false
        if (localStorage.getItem("use_bm25_"+workspace_id) === "true") use_bm25 = true

        setInput("");
        setIsSending(true);
        setCitations([])

        const userMsg:ChatMessage = {id: makeId(),role:"user",content:text}
        const assistantId = makeId()

        setMessages((m)=> [
            ...m,
            userMsg,
            {id:assistantId,role:'assistant',content:""},
        ])

        try {
            const res = await fetch(`${API_BASE}/chat/stream`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    workspace_id: workspace_id,
                    chat_id: chat_id,
                    query: text,
                    k: 6,
                    use_hyde: use_hyde,
                    use_bm25: use_bm25
                }),
            });

            if (!res.ok || !res.body) {
                throw new Error(`Bad response ${res.status}`);
            }

            const reader = res.body.getReader();
            const decoder = new TextDecoder("utf-8")
            
            // SSE parser
            // data: token\n\n
            // event: citations\ndata []\n\n
            let buffer = ""
            while (true) {
                const {value,done} = await reader.read() // read chunk
                if (done) break;

                buffer += decoder.decode(value,{stream:true});

                const parts = buffer.split(/\r?\n\r?\n/);
                buffer = parts.pop() ?? "";

                for (const frame of parts ) {
                    const lines = frame.split(/\r?\n/).filter(Boolean);

                    let eventType = "message"
                    let dataLines: string[] = [];

                    for (const line of lines) {
                        if (line.startsWith("event:")) eventType = line.slice(6).trim();
                        if (line.startsWith("data:")) dataLines.push(line.slice(5));
                    }

                    const data = dataLines.join("\n");
                    if (eventType == "citations") {
                        try {
                            setCitations(JSON.parse(data))
                        } catch { }
                        continue
                    }
                    if (eventType == "done") continue

                    if (eventType === "token") {
                        try {
                            const parsed = JSON.parse(data) as {text?:string}
                            const token = parsed.text ?? "";
                            pendingRef.current += token
                            scheduleFlush(assistantId)
                        } catch  {  }
                        continue
                    }
                }
            }

            buffer += decoder.decode()
        } catch (err) {
            setMessages((prev) => 
                prev.map((msg) => 
                msg.role == "assistant" && msg.content == "" 
                ? {...msg, content:"Error generating response"}
                : msg))
        } finally {
            setIsSending(false);
            if (flushTimerRef.current !== null) {
                clearTimeout(flushTimerRef.current);
                flushTimerRef.current = null;
            }
            if (pendingRef.current) {
                const chunk = pendingRef.current
                pendingRef.current = null
                setMessages((prev)=>
                    prev.map((msg)=>
                        msg.id === assistantId ? {...msg, content: msg.content + chunk} : msg))
            }

        }
    }

    return (
        <div className="flex h-full flex-col pt-12">
            <div className="flex-1 min-h-0">
                <ScrollArea className="h-full">
                    <ChatMessages messages={renderedMessages} citations={citations} />
                    <div ref={bottomRef}></div>
                </ScrollArea>
            </div>

            <div className="border-t p-3 mb-2">

                <div className="w-full md:w-[80%] m-auto max-w-[1200px]">
                    <div className="flex gap-2 items-center">
                    <Textarea
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask a question about your documents…"
                        className="resize-none w-[80%]"
                        rows={2}
                        onKeyDown={(e) => {
                        if (e.key === "Enter" && !e.shiftKey) {
                            e.preventDefault();
                            send();
                        }
                        }}
                    />

                    <div className="flex md:flex-row gap-2">
                        <Button onClick={send} disabled={isSending || !input.trim()} 
                            variant={"outline"} className="cursor-pointer">
                            {isSending ? "…" : "Send"}
                        </Button>
                        <UploadDocument workspace_id={workspace_id} messages={renderedMessages} />
                    </div>

                    </div>
                    <div className="mt-1 text-xs text-muted-foreground md:block hidden">
                    Enter = send, Shift+Enter = new line
                    </div>
                </div>
            </div>
        </div>
    )


}