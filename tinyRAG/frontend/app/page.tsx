


export default function Home() {
  return (
    <div>
      <div className="flex m-auto flex-col gap-4  pt-12 lg:w-120 w-[90%] text-[1.1rem] ">
        <h1 className="font-blid text-5xl italic text-center text-stone-600">tinyRAG</h1>
        <div className="text-stone-800 mt-2">
          <p >
            tinyRAG is local first RAG system that let you chat locally with your .PDF documents
          </p>
          <div className="text-start mt-4">
            <span className="italic text-2xl">Features</span>
            <ul className="list-[circle] ml-5 " >
              <li>Workspace and chat management</li>
              <li>PDF upload and background indexing</li>
              <li>Streaming chat responses (SSE)</li>
              <li>Source citations</li>
              <li>Markdown/LaTeX rendering in chat</li>
              <li>Local/LAN usage support</li>
            </ul>
            <div className="text-sm mt-6">
              Current version - 0.1.0 alpha
            </div>
          </div>
        </div>
        
      </div>
    </div>
  );
}
