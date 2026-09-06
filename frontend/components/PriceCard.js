"use client";

import { useEffect, useRef, useState } from "react";

export default function PriceCard({ coin, loading, active, onClick }) {
  const prevPrice = useRef(null);
  const [flash, setFlash] = useState(null); // 'up' | 'down' | null

  useEffect(() => {
    if (!coin) return;
    if (prevPrice.current !== null && coin.price !== prevPrice.current) {
      setFlash(coin.price > prevPrice.current ? "up" : "down");
      const t = setTimeout(() => setFlash(null), 1200);
      prevPrice.current = coin.price;
      return () => clearTimeout(t);
    }
    prevPrice.current = coin.price;
  }, [coin]);

  if (loading || !coin) {
    return (
      <div className="bg-terminal-panel border border-terminal-line rounded-xl p-3 animate-pulse h-[74px]" />
    );
  }

  const up = coin.change_24h >= 0;

  return (
    <button
      onClick={onClick}
      className={`text-left bg-terminal-panel border rounded-xl p-3 transition-all duration-500 ${
        active
          ? "border-terminal-accent shadow-glow"
          : "border-terminal-line hover:border-terminal-accent/50"
      } ${
        flash === "up"
          ? "bg-terminal-up/10 border-terminal-up/50"
          : flash === "down"
          ? "bg-terminal-down/10 border-terminal-down/50"
          : ""
      }`}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-terminal-muted">{coin.symbol}</span>
        <span
          className={`text-[11px] font-mono tabular ${
            up ? "text-terminal-up" : "text-terminal-down"
          }`}
        >
          {up ? "▲" : "▼"} {Math.abs(coin.change_24h)}%
        </span>
      </div>
      <div className="font-mono tabular text-lg font-semibold mt-1">
        ${coin.price?.toLocaleString(undefined, { maximumFractionDigits: coin.price < 1 ? 4 : 2 })}
      </div>
      <div className="text-[11px] text-terminal-muted mt-0.5">
        Cap: ${formatCompact(coin.market_cap)}
      </div>
    </button>
  );
}

function formatCompact(n) {
  if (!n) return "—";
  if (n >= 1e12) return (n / 1e12).toFixed(2) + "T";
  if (n >= 1e9) return (n / 1e9).toFixed(2) + "B";
  if (n >= 1e6) return (n / 1e6).toFixed(2) + "M";
  return n.toLocaleString();
}
