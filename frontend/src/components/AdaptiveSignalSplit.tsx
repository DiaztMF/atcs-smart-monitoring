'use client';

import React from 'react';
import { ArrowDownLeft, ArrowUpRight, Clock } from 'lucide-react';

interface AdaptiveSignalSplitProps {
  greenSplit: number; // Inbound percentage (0 - 100)
  cycleTimeSeconds?: number;
}

export default function AdaptiveSignalSplit({
  greenSplit,
  cycleTimeSeconds = 90,
}: AdaptiveSignalSplitProps) {
  const clampedSplit = Math.max(10, Math.min(90, greenSplit));
  const outboundSplit = 100 - clampedSplit;

  return (
    <div className="bg-white border border-[#e2e8f0] rounded-lg px-4 py-3 shadow-[0_1px_3px_rgba(0,0,0,0.04)] hover:border-slate-300 transition-colors">
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-[13px] font-semibold text-slate-700">
          Rasio Pembagian Waktu Hijau Sinyal Adaptif
        </span>
        <span className="text-[11px] font-mono text-slate-400 flex items-center gap-1">
          <Clock className="w-3 h-3" /> Siklus: {cycleTimeSeconds}s
        </span>
      </div>

      {/* Split Progress Bar */}
      <div className="relative h-5 bg-slate-100 rounded-full overflow-hidden flex shadow-inner">
        {/* Inbound Portion */}
        <div
          className="h-full bg-emerald-500 transition-all duration-700 flex items-center justify-center"
          style={{ width: `${clampedSplit}%` }}
        >
          {clampedSplit >= 15 && (
            <span className="text-[10px] font-bold text-white font-mono tracking-tight px-1">
              {clampedSplit}%
            </span>
          )}
        </div>

        {/* Outbound Portion */}
        <div className="flex-1 h-full bg-amber-500 transition-all duration-700 flex items-center justify-center">
          {outboundSplit >= 15 && (
            <span className="text-[10px] font-bold text-white font-mono tracking-tight px-1">
              {outboundSplit}%
            </span>
          )}
        </div>
      </div>

      {/* Footer Labels */}
      <div className="flex justify-between mt-1.5 text-[11px] font-medium">
        <span className="text-emerald-600 flex items-center gap-1">
          <ArrowDownLeft className="w-3.5 h-3.5" /> Masuk ({clampedSplit}%)
        </span>
        <span className="text-amber-600 flex items-center gap-1">
          Keluar ({outboundSplit}%) <ArrowUpRight className="w-3.5 h-3.5" />
        </span>
      </div>
    </div>
  );
}
