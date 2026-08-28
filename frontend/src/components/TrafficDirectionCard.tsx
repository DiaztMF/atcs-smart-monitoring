'use client';

import React from 'react';
import { ArrowDownLeft, ArrowUpRight } from 'lucide-react';
import { DirectionMetrics, DensityLevel } from '@/types';

interface TrafficDirectionCardProps {
  direction: 'inbound' | 'outbound';
  metrics: DirectionMetrics;
  totalVehicles: number;
}

const STATUS_STYLE: Record<
  DensityLevel,
  { bg: string; text: string; dot: string; border: string }
> = {
  LANCAR: {
    bg: 'bg-emerald-50',
    text: 'text-emerald-700',
    dot: 'bg-emerald-500',
    border: 'border-emerald-200',
  },
  SEDANG: {
    bg: 'bg-yellow-50',
    text: 'text-yellow-700',
    dot: 'bg-yellow-500',
    border: 'border-yellow-200',
  },
  PADAT: {
    bg: 'bg-orange-50',
    text: 'text-orange-700',
    dot: 'bg-orange-500',
    border: 'border-orange-200',
  },
  MACET: {
    bg: 'bg-red-50',
    text: 'text-red-700',
    dot: 'bg-red-500',
    border: 'border-red-200',
  },
};

export function StatusBadge({ status }: { status: DensityLevel }) {
  const s = STATUS_STYLE[status] || STATUS_STYLE.LANCAR;
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold tracking-wide border ${s.bg} ${s.text} ${s.border}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${s.dot} animate-pulse`} />
      {status}
    </span>
  );
}

export default function TrafficDirectionCard({
  direction,
  metrics,
  totalVehicles,
}: TrafficDirectionCardProps) {
  const isInbound = direction === 'inbound';
  const accentBorder = isInbound ? 'border-l-4 border-l-emerald-500' : 'border-l-4 border-l-amber-500';
  const numberAccent = isInbound ? 'text-emerald-700' : 'text-amber-700';
  const Icon = isInbound ? ArrowDownLeft : ArrowUpRight;
  const title = isInbound ? 'Trafik Masuk (Inbound)' : 'Trafik Keluar (Outbound)';

  return (
    <div
      className={`bg-white border border-[#e2e8f0] rounded-lg p-4 shadow-[0_1px_3px_rgba(0,0,0,0.04)] ${accentBorder} flex flex-col gap-2 hover:border-slate-300 transition-colors`}
    >
      {/* Card Header: Title + Status Badge */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <Icon className={`w-4 h-4 ${isInbound ? 'text-emerald-600' : 'text-amber-600'}`} />
          <span className="text-[13px] font-semibold text-slate-800">
            {title}
          </span>
        </div>
        <StatusBadge status={metrics.density_level} />
      </div>

      {/* 3 Metric Columns Row */}
      <div className="flex items-end gap-4 pt-1">
        {/* Total Vehicles */}
        <div>
          <span
            className={`text-[32px] font-bold leading-none font-mono ${numberAccent}`}
          >
            {totalVehicles.toLocaleString('id-ID')}
          </span>
          <div className="text-[12px] text-slate-400 mt-1">kendaraan</div>
        </div>

        {/* Total SMP */}
        <div className="border-l border-[#e2e8f0] pl-4">
          <div className="text-[20px] font-bold text-slate-900 font-mono leading-none">
            {metrics.total_smp.toFixed(1)}
          </div>
          <div className="text-[12px] text-slate-400 mt-1">SMP</div>
        </div>

        {/* SMP Rate */}
        <div className="border-l border-[#e2e8f0] pl-4">
          <div className="text-[20px] font-bold text-slate-900 font-mono leading-none">
            {metrics.smp_per_minute.toFixed(1)}
          </div>
          <div className="text-[12px] text-slate-400 mt-1">SMP/menit</div>
        </div>
      </div>
    </div>
  );
}
