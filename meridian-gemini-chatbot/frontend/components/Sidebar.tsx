"use client";

import { useRouter } from "next/navigation";
import { clearTokens } from "@/lib/auth";
import { DocumentUpload } from "./DocumentUpload";

type Conversation = { id: string; title: string };

export function Sidebar({
  conversations,
  activeId,
  onSelect,
  onNewChat,
}: {
  conversations: Conversation[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNewChat: () => void;
}) {
  const router = useRouter();

  function handleLogout() {
    clearTokens();
    router.push("/login");
  }

  return (
    <aside className="w-72 border-r border-line flex flex-col h-screen">
      <div className="px-5 py-5 border-b border-line flex items-center justify-between">
        <span className="font-display italic text-lg">Meridian</span>
        <button onClick={onNewChat} className="text-xs text-signal hover:underline">
          New chat
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-3 py-3 space-y-1">
        {conversations.length === 0 && (
          <p className="text-xs text-muted px-2 py-4">No conversations yet — start one below.</p>
        )}
        {conversations.map((c) => (
          <button
            key={c.id}
            onClick={() => onSelect(c.id)}
            className={`w-full text-left text-sm px-3 py-2 rounded truncate transition-colors ${
              c.id === activeId ? "bg-surfaceRaised text-paper" : "text-muted hover:bg-surface"
            }`}
          >
            {c.title}
          </button>
        ))}
      </div>

      <div className="px-3 py-3 border-t border-line space-y-3">
        <DocumentUpload />
        <button onClick={handleLogout} className="text-xs text-muted hover:text-paper w-full text-left px-1">
          Log out
        </button>
      </div>
    </aside>
  );
}
