import ReactMarkdown from "react-markdown";

export function MessageBubble({ role, content }: { role: string; content: string }) {
  const isUser = role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-5`}>
      <div
        className={`max-w-[75%] px-4 py-3 rounded ${
          isUser ? "bg-signal text-white" : "bg-surface border border-line text-paper"
        }`}
      >
        <div className="prose prose-invert prose-sm max-w-none prose-p:my-1">
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
}
