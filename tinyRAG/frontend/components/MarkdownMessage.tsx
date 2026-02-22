"use client"

import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import remarkMath from "remark-math"
import rehypeKatex from "rehype-katex"
import rehypePrettyCode from "rehype-pretty-code"
import rehypeHighlight from "rehype-highlight"
import React from "react"

const prettyCodeOpts = {
    theme: "github-dark",
    keepBackground: false
}

export const MarkdownMessage = React.memo(function MarkdownMessage({
    content
}: {
    content:string
}) {
    return (
        <ReactMarkdown
            remarkPlugins={[remarkGfm,remarkMath]}
            rehypePlugins={[rehypeHighlight, rehypeKatex]}
            components={{
                a: (props) => <a {...props} target="_blank" rel="norefer" className="underline"/>
            }}>
            {content}
        </ReactMarkdown>
    )
})
