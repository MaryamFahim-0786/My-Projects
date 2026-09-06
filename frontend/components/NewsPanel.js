"use client";

import { useEffect, useState } from "react";

export default function NewsPanel({ apiBase }) {
  const [news, setNews] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${apiBase}/api/news`)
      .then((r) => r.json())
      .then((data) => {
        if (Array.isArray(data)) {
          setNews(data);
          setError("");
        } else {
          setNews([]);
          setError(data?.error || "News service returned an unexpected response.");
        }
      })
      .catch(() => {
        setNews([]);
        setError("Could not reach the backend for news.");
      })
      .finally(() => setLoading(false));
  }, [apiBase]);

  return (
    <div className="bg-terminal-panel border border-terminal-line rounded-2xl p-4 lg:p-5">
      <h2 className="font-display text-sm font-semibold mb-3 flex items-center gap-2">
        <span className="text-terminal-accent">▤</span> Crypto Market News &amp; Regulatory
        Issues
      </h2>

      {loading && (
        <div className="text-terminal-muted text-sm">Loading latest headlines…</div>
      )}

      {!loading && news.length === 0 && (
        <div className="text-terminal-muted text-sm">
          {error || "No news available right now."}
        </div>
      )}

      <div className="space-y-3">
        {news.map((n, i) => (
          <a
            key={i}
            href={n.url}
            target="_blank"
            rel="noopener noreferrer"
            className="block border-b border-terminal-line last:border-0 pb-3 last:pb-0 hover:bg-terminal-panel2/50 -mx-2 px-2 rounded-lg transition-colors"
          >
            <div className="text-sm font-medium text-terminal-text leading-snug">
              {n.title}
            </div>
            <div className="flex items-center gap-2 mt-1 text-[11px] text-terminal-muted">
              <span>{n.source}</span>
              <span>·</span>
              <span>{new Date(n.published_on * 1000).toLocaleDateString()}</span>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}
