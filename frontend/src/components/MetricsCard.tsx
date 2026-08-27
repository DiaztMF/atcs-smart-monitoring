'use client';

import React from 'react';

interface KPICardProps {
  label: string;
  value: string;
  sub?: string;
  accent?: string;
}

export function KPICard({ label, value, sub, accent }: KPICardProps) {
  return (
    <div className="bg-white border border-[#e2e8f0] rounded-lg p-4 flex flex-col gap-1 shadow-[0_1px_3px_rgba(0,0,0,0.04)] hover:border-slate-300 transition-colors">
      <span className="text-[12px] font-semibold text-slate-500 uppercase tracking-wider">
        {label}
      </span>
      <span className={`text-[28px] lg:text-[30px] font-bold text-slate-900 leading-none font-mono ${accent || ''}`}>
        {value}
      </span>
      {sub && (
        <span className="text-[12px] text-slate-400 mt-1 truncate">
          {sub}
        </span>
      )}
    </div>
  );
}

interface KPIRowProps {
  totalVehicles: number;
  inboundSMP: number;
  outboundSMP: number;
  inboundCount: number;
  outboundCount: number;
  greenSplit: number;
}

export default function KPIRow({
  totalVehicles,
  inboundSMP,
  outboundSMP,
  inboundCount,
  outboundCount,
  greenSplit,
}: KPIRowProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
      <KPICard
        label="Total Kendaraan"
        value={totalVehicles.toLocaleString('id-ID')}
        sub="Total terakumulasi"
      />
      <KPICard
        label="SMP Masuk (Inbound)"
        value={inboundSMP.toFixed(1)}
        sub={`${inboundCount.toLocaleString('id-ID')} kendaraan masuk`}
        accent="text-emerald-700"
      />
      <KPICard
        label="SMP Keluar (Outbound)"
        value={outboundSMP.toFixed(1)}
        sub={`${outboundCount.toLocaleString('id-ID')} kendaraan keluar`}
        accent="text-amber-700"
      />
      <KPICard
        label="Rasio Sinyal Hijau"
        value={`${greenSplit}%`}
        sub="Rasio Beban Masuk / Keluar"
      />
    </div>
  );
}
