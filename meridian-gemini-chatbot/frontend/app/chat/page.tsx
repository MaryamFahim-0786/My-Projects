"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";
import { Sidebar } from "@/components/Sidebar";
import { MessageBubble } from "@/components/MessageBubble";

type Message = { id: string; role: string; content: string };
type Conversation = { id: string; title: string };

export default function ChatPage() {
  const router = useRouter();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [useRag, setUseRag] = useState(true);
  const [useTools, setUseTools] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login");
      return;
    }
    api.listConversations().then(setConversations).catch(() => {});
  }, [router]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function selectConversation(id: string) {
    setActiveId(id);
    const msgs = await api.getMessages(id);
    setMessages(msgs);
  }

  function newChat() {
    setActiveId(null);
    setMessages([]);
  }

  async function handleSend() {
    if (!input.trim() || sending) return;
    const userMessage: Message = { id: crypto.randomUUID(), role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setSending(true);

    try {
      const res = await api.sendMessage(userMessage.content, activeId ?? undefined, useRag, useTools);
      setMessages((prev) => [...prev, { id: crypto.randomUUID(), role: "assistant", content: res.reply }]);

      if (!activeId) {
        setActiveId(res.conversation_id);
        const convos = await api.listConversations();
        setConversations(convos);
      }
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: "assistant", content: `⚠️ ${err.message}` },
      ]);
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="flex h-screen bg-ink">
      <Sidebar
        conversations={conversations}
        activeId={activeId}
        onSelect={selectConversation}
        onNewChat={newChat}
      />

      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto px-8 py-8 max-w-3xl mx-auto w-full">
          {messages.length === 0 && (
            <p className="text-muted text-sm mt-20 text-center">
              Ask a question, or upload a document from the sidebar to chat with it.
            </p>
          )}
          {messages.map((m) => (
            <MessageBubble key={m.id} role={m.role} content={m.content} />
          ))}
          {sending && <p className="text-muted text-sm">Meridian is thinking…</p>}
          <div ref={bottomRef} />
        </div>

        <div className="border-t border-line px-8 py-4">
          <div className="max-w-3xl mx-auto">
            <div className="flex gap-4 mb-2 text-xs text-muted">
              <label className="flex items-center gap-1.5 cursor-pointer">
                <input type="checkbox" checked={useRag} onChange={(e) => setUseRag(e.target.checked)} />
                Use my documents
              </label>
              <label className="flex items-center gap-1.5 cursor-pointer">
                <input type="checkbox" checked={useTools} onChange={(e) => setUseTools(e.target.checked)} />
                Allow tools (search, calculator)
              </label>
            </div>
            <div className="flex gap-2">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                rows={1}
                placeholder="Ask Meridian anything…"
                className="flex-1 bg-surface border border-line rounded px-4 py-3 outline-none focus:border-signal resize-none"
              />
              <button
                onClick={handleSend}
                disabled={sending}
                className="bg-signal text-white px-5 rounded font-medium hover:opacity-90 disabled:opacity-50 transition-opacity"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
