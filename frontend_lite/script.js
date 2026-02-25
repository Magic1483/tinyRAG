
let documents = []
let docPollTimer = null;
let g_workspace_id = null

const scroll_chat = () => {
    const chat_window = document.getElementById("chat")
    if (!chat_window) return;
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            chat_window.scrollTop = chat_window.scrollHeight;
        });
    });
}

const getWs = async () => {
    const res = await fetch("/workspaces");
    const ws_bar = document.getElementById('workspace')
    ws_bar.innerHTML = ""

    for (const ws of await res.json()) {
        let wel = document.createElement("div")
        wel.classList = "h1 font-bold text-xl"
        wel.textContent = ws['name']
        wel.id = ws['id']


        ws_bar.appendChild(wel)
        for (const chat of ws['chats']) {
            let c = document.createElement("div")
            c.classList = "btn w-[70%]"
            c.textContent = chat['name']
            c.id = chat['id']
            c.onclick = async () => await getMessages(c['id'], ws['id'])
            ws_bar.appendChild(c)
        }
    }

    const chat_id = localStorage.getItem('chat_id')
    const ws_id = localStorage.getItem('workspace_id')
    g_workspace_id = ws_id;
    if (chat_id && ws_id) {
        await getMessages(chat_id, ws_id)
        await getDocuments(ws_id)
    }


}

const addMsg = (element) => {
    const chat_window = document.getElementById("chat")

    let msg = document.createElement("div")
    let content = document.createElement("div")
    content.classList = "overflow-y-scroll"
    content.innerHTML = marked.parse(element['content']);

    msg.classList = `lg:w-[60%] w-[90%] border p-2 items-end bg-white
        ${element['role'] === "user" ? "self-end" : ""}`
    msg.appendChild(content)

    chat_window.appendChild(msg)
}

const getMessages = async (id, ws_id) => {
    const res = await fetch(`/chats/${id}/messages`);
    const data = await res.json()
    const chat_window = document.getElementById("chat")
    chat_window.innerHTML = ""
    data.forEach(addMsg);
    
    


    localStorage.setItem("chat_id", id)
    localStorage.setItem("workspace_id", ws_id)

    await getDocuments(ws_id)
    scroll_chat()
}

// Documents
const getDocuments = async (ws_id) => {
    const res = await fetch(`/docs/${ws_id}/documents`);
    if (!res.ok) return
    const data = await res.json()
    documents = []
    doc_table.innerHTML = ""

    data.forEach(d => {

        documents.push({
            "file_name": d['file_name'],
            "status": d['status'],
            "id": d['id'],
        })
        let tr = document.createElement("tr")

        let file_name = document.createElement("td")
        file_name.textContent = d['file_name']

        let status = document.createElement("td")
        status.textContent = d['status']
        tr.appendChild(file_name)
        tr.appendChild(status)

        doc_table.appendChild(tr)
    })
}

const hasPendingDocs = () =>
    documents.some((d) => d.status === "uploaded" || d.status === "indexing");

const stopDocPolling = () => {
    if (docPollTimer) {
        clearInterval(docPollTimer);
        docPollTimer = null;
    }
};

const startDocPolling = (ws_id) => {
    stopDocPolling(); // avoid duplicate intervals

    docPollTimer = setInterval(async () => {
        try {
            await getDocuments(ws_id); // refresh global `documents`
            if (!hasPendingDocs()) stopDocPolling();
        } catch (e) {
            console.error("doc polling failed", e);
            // optional: stop after repeated failures
        }
    }, 3000);
};

const sendDocument = async () => {
    let form = new FormData()
    let file = document.getElementById("doc").files?.[0]
    if (!file || !file.name.includes(".pdf") || !g_workspace_id) return

    form.append("file", file)
    const res = await fetch(`/docs/upload?workspace_id=${g_workspace_id}`, {
        method: "POST",
        body: form
    });
    if (!res.ok) return


    await getDocuments(g_workspace_id)
    if (hasPendingDocs()) startDocPolling(g_workspace_id)
}


const sendMessage = async (workspace_id, chat_id, query, k) => {
    const res = await fetch(`/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            "workspace_id": workspace_id,
            "chat_id": chat_id,
            "k": k,
            "query": query
        })
    });
    const data = await res.json()
    addMsg(data)

    scroll_chat()
}


const handleSendMsg = () => {
    let textArea = document.getElementById("input")
    const ch_id = localStorage.getItem('chat_id')
    const ws_id = localStorage.getItem('workspace_id')
    const query = textArea.value
    if (ch_id && ws_id && query) {
        addMsg({
            "content": query,
            "role": "user"
        })
        
        textArea.value = null
        scroll_chat()
        sendMessage(ws_id, ch_id, query, 5)
    }
}

const load = async () => {
    await getWs()
    hljs.registerLanguage("javascript", window.hljsDefineJavascript);
    mermaid.initialize({ startOnLoad: false, securityLevel: "loose" });


    document.getElementById('btn_send').addEventListener('click', () => 
        handleSendMsg())

    document.getElementById("input").addEventListener('keydown', (e) => {
        if (e.key === "Enter") {
            e.preventDefault()
            handleSendMsg()
        }
    })
}



