"use client";

import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export type TrendPoint = { sprint: string; risk: number };

type Props = {
  history: TrendPoint[];
};

export function RiskTrendChart({ history }: Props) {
  return (
    <div className="h-64 min-h-[256px] w-full min-w-0">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={history}>
          <defs>
            <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#2f81f7" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#2f81f7" stopOpacity={0} />
            </linearGradient>
          </defs>
          <XAxis dataKey="sprint" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" domain={[0, 100]} />
          <Tooltip
            cursor={{ stroke: "#38bdf8" }}
            contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #1e293b" }}
          />
          <Area
            type="monotone"
            dataKey="risk"
            stroke="#2f81f7"
            fillOpacity={1}
            fill="url(#colorRisk)"
            name="Risk score"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
