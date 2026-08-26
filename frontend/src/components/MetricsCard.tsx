'use client';

import React from 'react';
import { ArrowDownLeft, ArrowUpRight } from 'lucide-react';
import { DirectionMetrics } from '@/types';

interface MetricsCardProps {
  title: string;
  direction: 'inbound' | 'outbound';
  data: DirectionMetrics;
}

export default function MetricsCard({ title, direction, data }: MetricsCardProps) {
  const isInbound = direction === 'inbound';
  
  const getDensityBadge = (level: string) => {
    switch (level) {
      case 'LANCAR':
        return 'bg-emerald-950/80 text-emerald-400 border-emerald-700/80';
      case 'SEDANG':
        return 'bg-yellow-950/80 text-yellow-400 border-yellow-700/80';
      case 'PADAT':
        return 'bg-orange-950/80 text-orange-400 border-orange-700/80';
      case 'MACET':
        return 'bg-rose-950/80 text-rose-400 border-rose-700/80';
      default:
        return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  return (
    <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex flex-col justify-between space-y-4 shadow-lg">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div
            className={`p-2 rounded-xl ${
              isInbound
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
            }`}
          >
            {isInbound ? <ArrowDownLeft className="w-5 h-5" /> : <ArrowUpRight className="w-5 h-5" />}
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-200">{title}</h3>
            <span className="text-xs text-slate-400">Arah {isInbound ? 'Masuk' : 'Keluar'}</span>
          </div>
        </div>
        <span
          className={`px-2.5 py-1 rounded-full text-xs font-semibold border ${getDensityBadge(
            data.density_level
          )}`}
        >
          {data.density_level}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 pt-2 border-t border-slate-800/80">
        <div>
          <div className="text-xs text-slate-400">Total Akumulasi Beban</div>
          <div className="text-2xl font-bold font-mono text-slate-100">
            {data.total_smp.toFixed(1)}{' '}
            <span className="text-xs font-normal text-slate-400">SMP</span>
          </div>
        </div>
        <div>
          <div className="text-xs text-slate-400">Laju Kepadatan (60s)</div>
          <div className="text-2xl font-bold font-mono text-slate-100">
            {data.smp_per_minute.toFixed(1)}{' '}
            <span className="text-xs font-normal text-slate-400">SMP/mnt</span>
          </div>
        </div>
      </div>
    </div>
  );
}
