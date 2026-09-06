"use client";

import { useEffect, useRef, useState } from "react";

const SUGGESTIONS = [
  "What's Bitcoin's current price?",
  "Compare BTC and ETH",
  "Which coins are moving today?",
  "Analyze Solana's 7-day trend",
];

export default function ChatPanel({ apiBase, selectedCoin }) {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Welcome to Crypto AI Intelligence. Ask me about live prices, market moves, coin comparisons, or price trends.",
    },
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, sending]);

  async function sendMessage(text) {
    const content = (text ?? input).trim();
    if (!content || sending) return;

    const nextMessages = [...messages, { role: "user", content }];
    setMessages(nextMessages);
    setInput("");
    setSending(true);

    try {
      const res = await fetch(`${apiBase}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: content,
          history: nextMessages.slice(-10),
        }),
      });

      const data = await res.json();
      const reply =
        data.reply ||
        data.error ||
        "I couldn't get a response right now. Please try again.";

      setMessages((m) => [...m, { role: "assistant", content: reply }]);
    } catch {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content:
            "I couldn't connect to the AI service. Please make sure the Flask backend is running on port 5000.",
        },
      ]);
    } finally {
      setSending(false);
    }
  }

  return (
    <section className="relative overflow-hidden bg-terminal-panel border border-terminal-line rounded-3xl shadow-glow">
      {/* Decorative evolving signal line */}
      <div className="absolute left-0 right-0 top-[118px] h-px overflow-hidden opacity-80 pointer-events-none">
        <div className="ai-signal-line" />
      </div>

      <div className="relative px-5 pt-6 pb-4 sm:px-7 sm:pt-7">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <div className="inline-flex items-center gap-2 text-[11px] uppercase tracking-[0.22em] text-terminal-accent">
              <span className="w-1.5 h-1.5 rounded-full bg-terminal-accent live-dot" />
              AI market intelligence
            </div>
            <h2 className="font-display text-2xl sm:text-3xl font-semibold mt-2">
              Ask your crypto copilot
            </h2>
            <p className="text-sm text-terminal-muted mt-1 max-w-2xl">
              Real-time market questions, comparisons and trend analysis in one
              intelligent workspace.
            </p>
          </div>

          {selectedCoin && (
            <div className="rounded-full border border-terminal-line bg-terminal-panel2 px-3 py-1.5 text-xs text-terminal-muted">
              Tracking{" "}
              <span className="text-terminal-text font-medium">
                {selectedCoin.symbol || selectedCoin.name}
              </span>
            </div>
          )}
        </div>

        <div className="mt-7 relative">
          <div className="ai-command-glow absolute -inset-1 rounded-2xl opacity-60 blur-md pointer-events-none" />
          <form
            onSubmit={(e) => {
              e.preventDefault();
              sendMessage();
            }}
            className="relative flex items-center gap-2 rounded-2xl border border-terminal-line bg-terminal-panel2 p-2 focus-within:border-terminal-accent/60 transition-colors"
          >
            <span className="hidden sm:block pl-3 text-terminal-accent text-lg">
              ✦
            </span>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything about the crypto market..."
              className="min-w-0 flex-1 bg-transparent px-2 py-3 text-sm sm:text-base outline-none placeholder:text-terminal-muted"
            />
            <button
              type="submit"
              disabled={sending}
              className="shrink-0 rounded-xl bg-terminal-accent px-4 py-3 text-sm font-semibold text-terminal-bg hover:brightness-110 disabled:opacity-50 transition"
            >
              {sending ? "Thinking…" : "Ask AI"}
            </button>
          </form>
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          {SUGGESTIONS.map((suggestion) => (
            <button
              key={suggestion}
              onClick={() => sendMessage(suggestion)}
              disabled={sending}
              className="rounded-full border border-terminal-line bg-terminal-panel2 px-3 py-1.5 text-xs text-terminal-muted hover:text-terminal-accent hover:border-terminal-accent/40 transition disabled:opacity-50"
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>

      <div className="border-t border-terminal-line bg-terminal-bg/30">
        <div
          ref={scrollRef}
          className="max-h-[360px] min-h-[110px] overflow-y-auto px-5 py-4 sm:px-7 space-y-3"
        >
          {messages.map((message, index) => (
            <div
              key={`${message.role}-${index}`}
              className={`flex ${
                message.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[820px] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
                  message.role === "user"
                    ? "bg-terminal-accent2 text-terminal-bg font-medium"
                    : "bg-terminal-panel2 text-terminal-text border border-terminal-line"
                }`}
              >
                {message.content}
              </div>
            </div>
          ))}

          {sending && (
            <div className="flex items-center gap-2 text-sm text-terminal-muted">
              <span className="ai-thinking-dot" />
              AI is analyzing the market…
            </div>
          )}
        </div>
      </div>

      {/* Continuous evolving line inspired by the reference design */}
      <div className="relative h-12 overflow-hidden border-t border-terminal-line bg-terminal-bg/60">
        <div className="absolute inset-y-0 left-0 right-0 ai-evolving-track">
          <div className="ai-evolving-wave" />
          <div className="ai-evolving-wave ai-evolving-wave-two" />
        </div>
        <div className="relative h-full flex items-center justify-center">
          <span className="rounded-full border border-terminal-line bg-terminal-panel px-3 py-1 text-[10px] uppercase tracking-[0.2em] text-terminal-muted">
            Continuously evolving market intelligence
          </span>
        </div>
      </div>
    </section>
  );
}
