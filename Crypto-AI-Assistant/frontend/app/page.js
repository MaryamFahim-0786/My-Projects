"use client";

import { useEffect, useState, useCallback } from "react";
import PriceCard from "../components/PriceCard";
import PriceChart from "../components/PriceChart";
import ChatPanel from "../components/ChatPanel";
import CoinSearch from "../components/CoinSearch";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:5000";
const REFRESH_MS = 120000;

export default function Home() {
  const [coins, setCoins] = useState([]);
  const [prices, setPrices] = useState([]);
  const [selectedCoin, setSelectedCoin] = useState("bitcoin");
  const [selectedInfo, setSelectedInfo] = useState(null);
  const [selectedSymbol, setSelectedSymbol] = useState("BTC");
  const [history, setHistory] = useState([]);
  const [historyError, setHistoryError] = useState("");
  const [days, setDays] = useState("30");
  const [loadingPrices, setLoadingPrices] = useState(true);
  const [loadingChart, setLoadingChart] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const selectCoin = useCallback((coinOrId) => {
    if (typeof coinOrId === "string") {
      setSelectedCoin(coinOrId);
      return;
    }
    if (coinOrId?.id) {
      setSelectedCoin(coinOrId.id);
      if (coinOrId.symbol) setSelectedSymbol(coinOrId.symbol);
    }
  }, []);

  const fetchPrices = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/prices`, { cache: "no-store" });
      const data = await res.json();

      if (Array.isArray(data) && data.length > 0) {
        setPrices(data);
        setError(null);
        setLastUpdated(new Date());
      } else {
        setError(data.error || "No market data available right now.");
      }
    } catch {
      setError("Backend not reachable. Make sure Flask is running on port 5000.");
    } finally {
      setLoadingPrices(false);
    }
  }, []);

  const fetchSelectedInfo = useCallback(
    async (coinId, symbol) => {
      try {
        const query = new URLSearchParams({ ids: coinId });
        if (symbol) query.set("symbol", symbol);
        const res = await fetch(`${API_BASE}/api/prices?${query}`, {
          cache: "no-store",
        });
        const data = await res.json();
        setSelectedInfo(Array.isArray(data) && data[0] ? data[0] : null);
      } catch {
        setSelectedInfo(null);
      }
    },
    []
  );

  const fetchHistory = useCallback(async (coinId, d, symbol) => {
    setLoadingChart(true);
    try {
      const query = new URLSearchParams({ days: d });
      if (symbol) query.set("symbol", symbol);
      const res = await fetch(
        `${API_BASE}/api/history/${encodeURIComponent(coinId)}?${query}`,
        { cache: "no-store" }
      );
      const data = await res.json();
      setHistory(Array.isArray(data.points) ? data.points : []);
      setHistoryError(!res.ok || data.error ? data.error || "Could not load chart data." : "");
    } catch {
      setHistory([]);
      setHistoryError("Backend not reachable for chart data.");
    } finally {
      setLoadingChart(false);
    }
  }, []);

  useEffect(() => {
    fetch(`${API_BASE}/api/coins`)
      .then((r) => r.json())
      .then((data) => setCoins(Array.isArray(data) ? data : []))
      .catch(() => setCoins([]));
  }, []);

  useEffect(() => {
    fetchPrices();
    const id = setInterval(fetchPrices, REFRESH_MS);
    return () => clearInterval(id);
  }, [fetchPrices]);

  useEffect(() => {
    fetchHistory(selectedCoin, days, selectedSymbol);
    fetchSelectedInfo(selectedCoin, selectedSymbol);

    const id = setInterval(
      () => fetchSelectedInfo(selectedCoin, selectedSymbol),
      REFRESH_MS
    );
    return () => clearInterval(id);
  }, [
    selectedCoin,
    selectedSymbol,
    days,
    fetchHistory,
    fetchSelectedInfo,
  ]);

  const selectedFromCards =
    prices.find((coin) => coin.id === selectedCoin) || selectedInfo;

  return (
    <main className="min-h-screen bg-terminal-bg bg-grid bg-fixed">
      <header className="sticky top-0 z-30 flex flex-wrap items-center justify-between gap-3 px-4 sm:px-6 py-4 border-b border-terminal-line bg-terminal-bg/90 backdrop-blur-xl">
        <div className="flex items-center gap-2">
          <span className="text-terminal-accent text-xl">⌁</span>
          <div>
            <h1 className="font-display font-semibold text-lg tracking-tight">
              Crypto AI Assistant
            </h1>
            <p className="hidden sm:block text-[10px] uppercase tracking-[0.16em] text-terminal-muted">
              Market intelligence workspace
            </p>
          </div>
        </div>

        <CoinSearch apiBase={API_BASE} onSelect={selectCoin} />

        <div className="flex items-center gap-2 text-xs text-terminal-muted">
          <span className="w-2 h-2 rounded-full bg-terminal-up live-dot" />
          {lastUpdated
            ? `Live · ${lastUpdated.toLocaleTimeString()}`
            : "Connecting…"}
        </div>
      </header>

      {error && (
        <div className="mx-4 sm:mx-6 mt-4 px-4 py-2.5 rounded-xl bg-terminal-down/10 border border-terminal-down/30 text-terminal-down text-sm">
          {error}
        </div>
      )}

      <div className="p-4 sm:p-6 space-y-5">
        {/* Market overview */}
        <section>
          <div className="flex items-end justify-between gap-3 mb-3">
            <div>
              <div className="text-[10px] uppercase tracking-[0.2em] text-terminal-accent">
                Live market
              </div>
              <h2 className="font-display text-xl font-semibold mt-1">
                Market overview
              </h2>
            </div>
            <span className="hidden sm:block text-xs text-terminal-muted">
              Prices refresh every 2 minutes
            </span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-3">
            {(loadingPrices ? Array.from({ length: 6 }) : prices).map(
              (p, i) => (
                <PriceCard
                  key={p?.id || i}
                  coin={p}
                  loading={loadingPrices}
                  active={p?.id === selectedCoin}
                  onClick={() => p && selectCoin(p)}
                />
              )
            )}
          </div>
        </section>

        {/* Chart */}
        <section className="bg-terminal-panel border border-terminal-line rounded-3xl p-4 sm:p-5 shadow-glow">
          <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
            <div>
              <div className="text-[10px] uppercase tracking-[0.2em] text-terminal-accent">
                Technical view
              </div>
              <h2 className="font-display text-base font-semibold mt-1">
                {selectedFromCards?.name || "Coin"} price trend
              </h2>
            </div>

            <div className="flex items-center gap-2">
              <select
                value={selectedCoin}
                onChange={(e) => {
                  const coin = coins.find((c) => c.id === e.target.value);
                  selectCoin(coin || e.target.value);
                }}
                className="max-w-[190px] bg-terminal-panel2 border border-terminal-line text-sm rounded-xl px-3 py-2 text-terminal-text focus:outline-none focus:ring-1 focus:ring-terminal-accent"
              >
                {coins.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name} ({c.symbol})
                  </option>
                ))}
              </select>

              <div className="flex bg-terminal-panel2 border border-terminal-line rounded-xl overflow-hidden text-xs">
                {["7", "30", "90"].map((d) => (
                  <button
                    key={d}
                    onClick={() => setDays(d)}
                    className={`px-3 py-2 ${
                      days === d
                        ? "bg-terminal-accent/20 text-terminal-accent"
                        : "text-terminal-muted hover:text-terminal-text"
                    }`}
                  >
                    {d}D
                  </button>
                ))}
              </div>
            </div>
          </div>

          <PriceChart
            data={history}
            loading={loadingChart}
            positive={selectedInfo ? selectedInfo.change_24h >= 0 : true}
            error={historyError}
          />
        </section>

        {/* AI assistant moved below the dashboard and upgraded */}
        <ChatPanel
          apiBase={API_BASE}
          selectedCoin={selectedFromCards}
        />
      </div>
    </main>
  );
}
