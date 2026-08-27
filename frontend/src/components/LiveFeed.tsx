'use client';

import React from 'react';
import { Bike, Car, Bus, Truck, ArrowDownLeft, ArrowUpRight } from 'lucide-react';
import { DetectionLogEvent, VehicleType } from '@/types';

interface LiveFeedProps {
  events: DetectionLogEvent[];
}

const VEHICLE_META: Record<
  VehicleType,
  { label: string; icon: React.ComponentType<{ className?: string }>; smp: string }
> = {
  motorcycle: { label: 'Sepeda Motor', icon: Bike, smp: '0.5' },
  car: { label: 'Mobil Penumpang', icon: Car, smp: '1.0' },
  bus: { label: 'Bus', icon: Bus, smp: '1.3' },
  truck: { label: 'Truk', icon: Truck, smp: '1.3' },
};

export default function LiveFeed({ events }: LiveFeedProps) {
  return (
    <div className="bg-white border border-[#e2e8f0] rounded-lg flex flex-col min-h-0 flex-1 shadow-[0_1px_3px_rgba(0,0,0,0.04)] hover:border-slate-300 transition-colors overflow-hidden">
      {/* Header */}
      <div className="px-4 py-2.5 border-b border-[#e2e8f0] flex items-center justify-between shrink-0 bg-slate-50/50">
        <span className="text-[13px] font-semibold text-slate-800">
          Log Deteksi Real-Time
        </span>
        <span className="text-[11px] text-slate-400 font-mono">
          {events.length} event
        </span>
      </div>

      {/* Column Headers */}
      <div className="grid grid-cols-[64px_1fr_72px_64px_48px] px-4 py-1.5 border-b border-[#f1f5f9] bg-slate-50/30 text-[10px] font-semibold text-slate-400 uppercase tracking-wider shrink-0">
        <span>Waktu</span>
        <span>Kendaraan</span>
        <span>Jalur</span>
        <span>Status</span>
        <span className="text-right">Arah</span>
      </div>

      {/* Log Feed List */}
      <div
        className="overflow-y-auto flex-1 max-h-[220px] divide-y divide-[#f8fafc]"
        style={{ scrollbarWidth: 'thin' }}
      >
        {events.length === 0 ? (
          <div className="py-8 text-center text-[12px] text-slate-400">
            Menunggu deteksi kendaraan real-time...
          </div>
        ) : (
          events.map((d) => {
            const meta = VEHICLE_META[d.type] || VEHICLE_META.car;
            const Icon = meta.icon;
            const isInbound = d.direction === 'IN';

            return (
              <div
                key={d.id}
                className="grid grid-cols-[64px_1fr_72px_64px_48px] px-4 py-2 hover:bg-slate-50/80 transition-colors items-center text-xs"
              >
                {/* Time */}
                <span className="text-[11px] text-slate-400 font-mono">
                  {d.time}
                </span>

                {/* Vehicle Type + Icon */}
                <div className="flex items-center gap-1.5 min-w-0 pr-2">
                  <Icon className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                  <span className="text-[12px] font-medium text-slate-700 truncate">
                    {meta.label}
                  </span>
                  <span className="text-[10px] text-slate-400 font-mono shrink-0">
                    ({meta.smp})
                  </span>
                </div>

                {/* Lane */}
                <span className="text-[11px] text-slate-500 truncate">
                  {d.lane}
                </span>

                {/* Status / Speed */}
                <span className="text-[11px] text-slate-600 font-mono">
                  {d.status}
                </span>

                {/* Direction Badge */}
                <div className="flex justify-end">
                  <span
                    className={`inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px] font-bold ${
                      isInbound
                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                        : 'bg-amber-50 text-amber-700 border border-amber-200'
                    }`}
                  >
                    {isInbound ? (
                      <>
                        <ArrowDownLeft className="w-2.5 h-2.5" /> IN
                      </>
                    ) : (
                      <>
                        <ArrowUpRight className="w-2.5 h-2.5" /> OUT
                      </>
                    )}
                  </span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
