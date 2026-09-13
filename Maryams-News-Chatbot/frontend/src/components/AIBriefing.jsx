import { useEffect, useRef, useState } from "react";
import { sendChatMessage } from "../api/client";

export default function AIBriefing({ contextArticle, onClearContext }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, sending]);

  async function handleSend(e) {
    e.preventDefault();
    const text = input.trim();
    if (!text || sending) return;

    const nextMessages = [...messages, { role: "user", content: text }];
    setMessages(nextMessages);
    setInput("");
    setSending(true);
    setError(null);

    try {
      const articleContext = contextArticle
        ? `${contextArticle.title}\n\n${contextArticle.description || ""}`
        : null;
      const { reply } = await sendChatMessage(text, messages, articleContext);
      setMessages([...nextMessages, { role: "assistant", content: reply }]);
    } catch (err) {
      setError(err.message);
    } finally {
      setSending(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      handleSend(e);
    }
  }

  return (
    <aside className="briefing">
      <div className="briefing-header">
        <span className="pulse" />
        <h2>AI Briefing</h2>
      </div>

      {contextArticle && (
        <div className="briefing-context">
          Discussing: {contextArticle.title}
          <button onClick={onClearContext}>Clear</button>
        </div>
      )}

      <div className="briefing-messages" ref={scrollRef}>
        {messages.length === 0 && (
          <p className="briefing-empty">
            Ask about anything in today's coverage — for context on a story, a plain-language
            explainer, or how two headlines connect. Click "Ask AI Briefing" on any story to
            bring it into the conversation.
          </p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`message ${m.role}`}>
            {m.role === "assistant" && <span className="role-label">AI Briefing</span>}
            {m.content}
          </div>
        ))}
        {sending && (
          <div className="message assistant">
            <span className="role-label">AI Briefing</span>
            Thinking…
          </div>
        )}
        {error && <div className="summary-error">{error}</div>}
      </div>

      <form className="briefing-form" onSubmit={handleSend}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about the news…"
        />
        <button type="submit" disabled={sending || !input.trim()}>
          Send
        </button>
      </form>
    </aside>
  );
}
