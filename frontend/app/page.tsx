"use client"

import { ChatWindow } from "@/components/ChatWindow";
import { useAppStore } from "./store";

export default function Home() {
  const chat_id = useAppStore((s)=>s.chat_id)
  const ws_id = useAppStore((s)=>s.ws_id)

  if (chat_id !== null && ws_id !== null) {
    return (
      <div className="h-dvh min-h-0">
      <ChatWindow workspace_id={ws_id} chat_id={chat_id} />
    </div>
    )
  } else {
    return (
      <div>
        <div className="flex m-auto flex-col gap-4  pt-12 lg:w-120 w-[90%] text-[1.1rem] ">
          <h1 className="font-blid text-5xl italic text-center text-stone-600">tinyRAG</h1>
          <div className="text-stone-800 mt-2">
            <p >
              tinyRAG is a local-first RAG workbench for PDF question answering and retrieval experiments.
            </p>
            <div className="text-start mt-4">
              <span className="italic text-2xl">Features</span>
              <ul className="list-[circle] ml-5 " >
                <li>Workspace and chat management</li>
                <li>PDF upload and background indexing</li>
                <li>Vector search with BM25 and HyDE retrieval modes</li>
                <li>Per-workspace retrieval settings: top_k, BM25, HyDE</li>
                <li>Streaming chat responses with citations</li>
                <li>Markdown and LaTeX rendering in chat</li>
                <li>JSON chat export</li>
                <li>Local data storage with SQLite and ChromaDB</li>
                <li>Portable Windows build served by FastAPI</li>
                <li>Evaluation scripts and benchmark reports</li>
              </ul>
              <div className="text-sm mt-6">
                Current version - 0.4.0
              </div>
            </div>
          </div>
          
        </div>
      </div>
    )
  }
}
