"use client";

import { useState, useEffect, useRef } from "react";

export default function CoinSearch({ apiBase, onSelect }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const boxRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(e) {
      if (boxRef.current && !boxRef.current.contains(e.target)) setOpen(false);
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      return;
    }
    setLoading(true);
    const timer = setTimeout(async () => {
      try {
        const res = await fetch(`${apiBase}/api/search?q=${encodeURIComponent(query)}`);
        const data = await res.json();
        setResults(Array.isArray(data) ? data : []);
        setOpen(true);
      } catch {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 350); // debounce so we don't hit the API on every keystroke
    return () => clearTimeout(timer);
  }, [query, apiBase]);

  return (
    <div ref={boxRef} className="relative w-full max-w-xs">
      <div className="flex items-center gap-2 bg-terminal-panel2 border border-terminal-line rounded-lg px-3 py-2 focus-within:ring-1 focus-within:ring-terminal-accent">
        <span className="text-terminal-muted text-sm">⌕</span>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => query && setOpen(true)}
          placeholder="Search any coin (e.g. shiba inu)"
          className="bg-transparent text-sm flex-1 outline-none placeholder:text-terminal-muted"
        />
        {loading && <span className="text-[10px] text-terminal-muted">…</span>}
      </div>

      {open && results.length > 0 && (
        <div className="absolute z-20 mt-1 w-full bg-terminal-panel border border-terminal-line rounded-lg shadow-lg overflow-hidden">
          {results.map((c) => (
            <button
              key={c.id}
              onClick={() => {
                onSelect(c.id);
                setQuery("");
                setResults([]);
                setOpen(false);
              }}
              className="w-full flex items-center gap-2 px-3 py-2 text-sm text-left hover:bg-terminal-panel2"
            >
              {c.thumb && <img src={c.thumb} alt="" className="w-4 h-4 rounded-full" />}
              <span className="font-medium">{c.name}</span>
              <span className="text-terminal-muted text-xs">{c.symbol}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
