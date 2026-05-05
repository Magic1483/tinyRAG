"use client"
import React, { useEffect, useState } from "react"
import { MarkdownMessage } from "./MarkdownMessage"
import type { ChatMessage,Citation } from "./ChatWindow"

export const ChatMessages = React.memo(function ChatMessages({
    messages,
}: {
    messages: ChatMessage[],
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
                                <MarkdownMessage message={m} />
                            </div>
                            : <div>{m.content} </div>
                        }
                    </div>
                ))}
            </div>
        </div>
    )
})