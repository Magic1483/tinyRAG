// app/workspaces/[workspace_id]/chats/[chat_id]/layout.tsx
import * as React from "react";

export default function ChatLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <div className="h-full w-full">{children}</div>;
}