"use client";

import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

export default function PriceChart({ data, loading, positive, error }) {
  const color = positive ? "#3ED598" : "#FF5C7A";

  if (loading) {
    return (
      <div className="h-[320px] flex items-center justify-center text-terminal-muted text-sm">
        Loading chart…
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="h-[320px] flex items-center justify-center text-terminal-muted text-sm text-center px-8">
        {error || "No data available."}
      </div>
    );
  }

  const chartData = data.map((p) => ({
    time: new Date(p.timestamp).toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
    }),
    price: p.price,
  }));

  return (
    <div className="h-[320px]">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="priceFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={color} stopOpacity={0.35} />
              <stop offset="100%" stopColor={color} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="#1C2740" strokeDasharray="3 3" vertical={false} />
          <XAxis
            dataKey="time"
            tick={{ fill: "#7E8CA8", fontSize: 11 }}
            axisLine={{ stroke: "#1C2740" }}
            tickLine={false}
            minTickGap={30}
          />
          <YAxis
            tick={{ fill: "#7E8CA8", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            domain={["auto", "auto"]}
            tickFormatter={(v) => `$${v.toLocaleString(undefined, { maximumFractionDigits: 0 })}`}
            width={70}
          />
          <Tooltip
            contentStyle={{
              background: "#0E1523",
              border: "1px solid #1C2740",
              borderRadius: 8,
              fontSize: 12,
            }}
            labelStyle={{ color: "#7E8CA8" }}
            formatter={(v) => [`$${Number(v).toLocaleString()}`, "Price"]}
          />
          <Area
            type="monotone"
            dataKey="price"
            stroke={color}
            strokeWidth={2}
            fill="url(#priceFill)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
