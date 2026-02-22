"use client"

import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarGroup,
    SidebarHeader,
} from "@/components/ui/sidebar";
import { Button } from "./ui/button";
import { Settings, Plus } from "lucide-react"
import Link from 'next/link'
import React from "react";
import { NewChat, NewWorkspace } from "@/components/NewChat"
import { Option } from "./Option";
import { API_BASE } from "@/app/api";

type WsButtonProps = React.ComponentProps<typeof Button> & {
    text: string;
    ws_id: string;
    chat_id: string;
};


type Chat = { "name": string, "id": string }
type Workspace = { name: string, id: string, chats: Chat[], }


export function AppSidebar() {
    const [workspaces, setWorkspaces] = React.useState<Workspace[]>([])

    console.log(API_BASE);
    
    React.useEffect(() => {
        async function getWs() {
            const res = await fetch(`${API_BASE}/workspaces`, { cache: "no-store" });
            if (!res.ok) return;
            const data: Workspace[] = await res.json();
            setWorkspaces(data);
        }
        getWs();
    }, []);

    function onWorkspaceCreated(ws: { id: string; name: string }) {
        setWorkspaces((prev) => [{ ...ws, chats: [] }, ...prev])
    }

    function onChatCreated(ws_id: string, chat: { id: string; name: string }) {
        setWorkspaces((prev) =>
            prev.map((ws) =>
                ws.id === ws_id ? { ...ws, chats: [chat, ...ws.chats] } : ws
            ))
    }

    function onChatDeleted(chatId: string) {
        setWorkspaces(prev =>
            prev.map(ws => ({ ...ws, chats: ws.chats.filter(c => c.id !== chatId) }))
        );
    }

    function onWorkspaceDeleted(workspaceId: string) {
        setWorkspaces(prev => prev.filter(ws => ws.id !== workspaceId));
    }


    function WsButton({ text, ws_id, chat_id, ...props }: WsButtonProps) {
        return (
            <div className="font-semibold inline-flex h-9 w-full items-center justify-between gap-2 rounded-md border bg-background px-3 text-sm shadow-xs transition-colors hover:bg-accent hover:text-accent-foreground">
                <Link href={`/workspaces/${ws_id}/chats/${chat_id}`} className="flex-1 min-w-0 max-w-[50%]">
                    <span className="min-w-0 flex-1 truncate text-left ">{text}</span>
                </Link>
                <Option
                    chat_id={chat_id}
                    workspace_id={ws_id}
                    onChatDeleted={onChatDeleted}
                    onWorkspaceDeleted={onWorkspaceDeleted}
                />
            </div>

        )
    }


    return (
        <Sidebar>
            <SidebarHeader className="flex flex-row gap-2 items-center">
                <span className="text-xl ">Workspaces</span>
                <NewWorkspace onCreated={onWorkspaceCreated} />
            </SidebarHeader>
            <SidebarContent className="p-2">
                {workspaces.map((ws) => (
                    <SidebarGroup key={ws.id} className="gap-2">
                        <div className="text-md font-semibold truncate">{ws.name}</div>
                        <NewChat
                            workspace_id={ws.id}
                            onCreated={(chat) => onChatCreated(ws.id, chat)} 
                            onWorkspaceDeleted={onWorkspaceDeleted}/>
                        {ws.chats.map((chat) => (
                            <WsButton text={chat.name} key={chat.id} chat_id={chat.id} ws_id={ws.id} />
                        ))}
                    </SidebarGroup>
                ))}
            </SidebarContent>
            <SidebarFooter>
                <Button variant="outline" size="icon" className="cursor-pointer">
                    <Link href="/settings">
                        <Settings className="w-5 h-5 text-foreground" />
                    </Link>
                </Button>
            </SidebarFooter>
        </Sidebar>
    )
}