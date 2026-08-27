'use client';

import React, { useEffect, useState } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';

interface TrafficChartProps {
  inboundSMP: number;
  outboundSMP: number;
}

interface ChartPoint {
  time: string;
  inbound: number;
  outbound: number;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: { name: string; value: number; color: string }[];
  label?: string;
}

const CustomTooltip = ({ active, payload, label }: CustomTooltipProps) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-white border border-[#e2e8f0] rounded-lg px-3 py-2 shadow-[0_4px_12px_rgba(0,0,0,0.08)]">
      <p className="text-[11px] text-slate-400 mb-1 font-sans font-medium">
        Waktu: {label}
      </p>
      {payload.map((p) => (
        <div key={p.name} className="flex items-center gap-2">
          <span
            className="w-2 h-2 rounded-full"
            style={{ backgroundColor: p.color }}
          />
          <span className="text-[12px] text-slate-600 font-sans">
            {p.name}:
          </span>
          <span className="text-[12px] font-semibold text-slate-900 font-mono">
            {typeof p.value === 'number' ? p.value.toFixed(1) : p.value} SMP
          </span>
        </div>
      ))}
    </div>
  );
};

export default function TrafficChart({ inboundSMP, outboundSMP }: TrafficChartProps) {
  const [dataPoints, setDataPoints] = useState<ChartPoint[]>(() => {
    const now = Date.now();
    return Array.from({ length: 15 }, (_, i) => {
      const t = new Date(now - (14 - i) * 3000);
      return {
        time: t.toLocaleTimeString('en-GB'),
        inbound: Number(Math.max(0, inboundSMP + (Math.random() * 2 - 1)).toFixed(1)),
        outbound: Number(Math.max(0, outboundSMP + (Math.random() * 2 - 1)).toFixed(1)),
      };
    });
  });

  useEffect(() => {
    const now = new Date().toLocaleTimeString('en-GB');

    setDataPoints((prev) => {
      const updated = [
        ...prev.slice(1),
        { time: now, inbound: Number(inboundSMP.toFixed(1)), outbound: Number(outboundSMP.toFixed(1)) },
      ];
      return updated;
    });
  }, [inboundSMP, outboundSMP]);

  return (
    <div className="bg-white border border-[#e2e8f0] rounded-lg p-4 shadow-[0_1px_3px_rgba(0,0,0,0.04)] shrink-0 hover:border-slate-300 transition-colors">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <span className="text-[13px] font-semibold text-slate-800">
          Tren Beban Lalu Lintas (Volume / 3s)
        </span>
        <div className="flex items-center gap-3 text-[11px] text-slate-500 font-medium">
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-0.5 bg-emerald-500 inline-block rounded" />
            Masuk
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-0.5 bg-amber-500 inline-block rounded" />
            Keluar
          </span>
        </div>
      </div>

      {/* Chart */}
      <div className="w-full h-[140px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={dataPoints} margin={{ top: 4, right: 4, left: -24, bottom: 0 }}>
            <CartesianGrid stroke="#f1f5f9" strokeDasharray="0" vertical={false} />
            <XAxis
              dataKey="time"
              tick={{ fontSize: 9, fill: '#94a3b8', fontFamily: 'JetBrains Mono, monospace' }}
              tickLine={false}
              axisLine={false}
              interval="preserveStartEnd"
            />
            <YAxis
              tick={{ fontSize: 9, fill: '#94a3b8', fontFamily: 'JetBrains Mono, monospace' }}
              tickLine={false}
              axisLine={false}
              domain={[0, 'auto']}
            />
            <Tooltip content={<CustomTooltip />} />
            <Line
              type="monotone"
              dataKey="inbound"
              name="Masuk"
              stroke="#059669"
              strokeWidth={1.5}
              dot={false}
              activeDot={{ r: 3, fill: '#059669' }}
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="outbound"
              name="Keluar"
              stroke="#d97706"
              strokeWidth={1.5}
              dot={false}
              activeDot={{ r: 3, fill: '#d97706' }}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
