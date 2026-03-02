"use client"
import React from "react"
import { MarkdownMessage } from "./MarkdownMessage"

export type ChatMessage = { id: string; role: "user" | "assistant"; content: string };
export type Citation = { file_name: string; page: string };


export const ChatMessages = React.memo(function ChatMessages({
    messages,
    citations,
}: {
    messages: ChatMessage[],
    citations: Citation[],
}) {
    return (
        <div className="lg:px-2 max-w-screen lg:max-w-[1200px] m-auto">
            <div className="p-4 space-y-3 bg-gray lg:px-8">
                {messages.map((m) => (
                    <div key={m.id} id={m.id} className={[
                        "lg:max-w-[70%] w-[95%] rounded-lg px-3 py-2 text-md leading-6",
                        m.role === "user"
                            ? "ml-auto bg-stone-300 whitespace-pre-wrap "
                            : "mr-auto bg-muted"
                    ].join(" ")}>
                        {m.role === "assistant" ?
                            <div className="md-content prose max-w-none dark:prose-invert text-md leading-6">
                                <MarkdownMessage content={m.content} />
                            </div>
                            : <div>{m.content} </div>
                        }
                    </div>
                ))}

                {citations.length > 0 && (
                    <div className="mt-2 text-xs text-muted-foreground lg:max-w-[70%] w-[95%]">
                        <span className="font-semibold">Sources: </span>
                        {citations.map((c, i) => (
                            <span key={`${c.file_name}-${c.page}-${i}`}>
                                {" • "} {c.file_name} page {c.page}
                            </span>
                        ))}
                    </div>
                )}
            </div>


        </div>
    )
})