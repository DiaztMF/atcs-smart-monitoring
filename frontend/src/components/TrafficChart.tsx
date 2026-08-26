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

export default function TrafficChart({ inboundSMP, outboundSMP }: TrafficChartProps) {
  const [dataPoints, setDataPoints] = useState<ChartPoint[]>([]);

  useEffect(() => {
    const now = new Date().toLocaleTimeString('id-ID', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });

    setDataPoints((prev) => {
      const updated = [...prev, { time: now, inbound: inboundSMP, outbound: outboundSMP }];
      if (updated.length > 20) updated.shift();
      return updated;
    });
  }, [inboundSMP, outboundSMP]);

  return (
    <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4 shadow-lg">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-slate-200">Tren Beban Lalu Lintas (Real-Time)</h3>
          <p className="text-xs text-slate-400">Fluktuasi Rolling Laju SMP / Menit</p>
        </div>
        <div className="flex items-center space-x-4 text-xs">
          <span className="flex items-center gap-1.5 text-emerald-400 font-medium">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> Inbound
          </span>
          <span className="flex items-center gap-1.5 text-amber-400 font-medium">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500" /> Outbound
          </span>
        </div>
      </div>

      <div className="h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={dataPoints}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="time" stroke="#64748b" fontSize={10} tickLine={false} />
            <YAxis stroke="#64748b" fontSize={10} tickLine={false} domain={[0, 'auto']} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0f172a',
                borderColor: '#334155',
                borderRadius: '8px',
                fontSize: '12px',
                color: '#f8fafc',
              }}
            />
            <Line
              type="monotone"
              dataKey="inbound"
              stroke="#10b981"
              strokeWidth={2}
              dot={false}
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="outbound"
              stroke="#f59e0b"
              strokeWidth={2}
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
