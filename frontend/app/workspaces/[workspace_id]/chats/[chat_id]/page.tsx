import { ChatWindow } from "@/components/ChatWindow";

export default async function ChatPage({
  params,
}: {
  params: Promise<{ workspace_id: string; chat_id: string }>;
}) {
  const { workspace_id, chat_id } = await params;
  console.log(workspace_id,chat_id);
  
  return (
    <div className="h-dvh min-h-0">
      <ChatWindow workspace_id={workspace_id} chat_id={chat_id} />
    </div>
  );
}