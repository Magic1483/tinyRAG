import {Delete, Ellipsis} from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { API_BASE } from "@/app/api"



export function Option({chat_id,workspace_id,onChatDeleted,onWorkspaceDeleted}: {
    chat_id?:string,
    workspace_id: string,
    onChatDeleted?: (chat_id:string) => void, 
    onWorkspaceDeleted: (workspace_id:string) => void,
}) {

    async function DeleteChat() {
        if (!chat_id) return
        const res = await fetch(`${API_BASE}/chats/${chat_id}`,{method:"DELETE"})
        if (!res.ok) return 
        onChatDeleted?.(chat_id)
    }

    async function DeleteWorkspace() {
        const res = await fetch(`${API_BASE}/workspaces/${workspace_id}`,{method:"DELETE"})
        if (!res.ok) return 
        onWorkspaceDeleted(workspace_id)
    }

    return (
        <DropdownMenu>
            <DropdownMenuTrigger className="cursor-pointer" asChild>
                <button type="button" className="cursor-pointer rounded p-1">
                    <Ellipsis className="h-4 w-4"/>
                </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
                {chat_id && 
                    <DropdownMenuItem className="cursor-pointer" onClick={()=> void DeleteChat()}>Delete Chat</DropdownMenuItem>    
                }
                <DropdownMenuItem className="cursor-pointer" onClick={()=> void DeleteWorkspace()}>Delete Worksapce</DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    )
}