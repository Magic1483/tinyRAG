"use client"

import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import remarkMath from "remark-math"
import rehypeKatex from "rehype-katex"
import rehypePrettyCode from "rehype-pretty-code"
import rehypeHighlight from "rehype-highlight"
import React, { useEffect, useState } from "react"
import type { ChatMessage,Citation } from "./ChatWindow"


const prettyCodeOpts = {
    theme: "github-dark",
    keepBackground: false
}

export const MarkdownMessage = React.memo(function MarkdownMessage({
    message,
}: {
    message: ChatMessage
}) {
    const [fullCitation,setfullCitation]       = useState(false);
    const [renderCitations,setRenderCitations] = useState<Citation[]>(message.citations)
        
    useEffect(()=>{
        if (fullCitation) {
            setRenderCitations(message.citations)
        } else {
            setRenderCitations(message.citations.slice(0,Math.min(5,message.citations.length)))
        }
    },[fullCitation,message.citations])
        
    return (
        <div>
            <div>
                <ReactMarkdown
                    remarkPlugins={[remarkGfm, remarkMath]}
                    rehypePlugins={[rehypeHighlight, rehypeKatex]}
                    components={{
                        a: (props) => <a {...props} target="_blank" rel="norefer" className="underline" />
                    }}>
                    {message.content}
                </ReactMarkdown>
            </div>
            { message.role == "assistant" &&
                <div className="mt-2 text-xs text-muted-foreground lg:max-w-[70%] w-[95%]">
                    <div>
                        {(message.use_bm25 || message.use_hyde) &&
                            <span className="font-semibold">Features:
                                {message.use_hyde && <span> HyDE </span>}
                                {message.use_bm25 && <span> BM25 </span>}
                            </span>
                        }
                    </div>

                    {message.citations.length > 0 && (
                        <div>
                            <span className="font-semibold cursor-pointer"
                                onClick={() => setfullCitation(!fullCitation)}>Sources: </span>
                            <div className={fullCitation ? "flex flex-col" : "max-w-128 text-nowrap truncate"}>
                                {
                                    renderCitations.map((c, i) => (
                                        <span key={`${c.file_name}-${c.page}-${i}`}>
                                            {" • "} {c.file_name} page {c.page}
                                        </span>
                                    ))}
                            </div>
                        </div>
                    )}
                </div> 
            }
        </div>
    )
})
