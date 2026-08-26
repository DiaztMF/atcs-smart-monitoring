'use client';

import React from 'react';
import { Clock, ArrowDownLeft, ArrowUpRight } from 'lucide-react';
import { VehicleEvent } from '@/types';

interface LiveFeedProps {
  events: VehicleEvent[];
}

export default function LiveFeed({ events }: LiveFeedProps) {
  return (
    <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4 shadow-lg">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-200">Aktivitas Kendaraan Terdeteksi</h3>
        <span className="text-xs text-slate-400">15 Event Terakhir</span>
      </div>

      <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
        {events.length === 0 ? (
          <div className="text-center py-8 text-xs text-slate-500">
            Menunggu deteksi kendaraan pertama...
          </div>
        ) : (
          events.map((evt) => {
            const isInbound = evt.direction === 'inbound';
            return (
              <div
                key={evt.id}
                className="p-2.5 rounded-xl bg-slate-900/70 border border-slate-800/80 flex items-center justify-between text-xs hover:border-slate-700 transition-colors"
              >
                <div className="flex items-center space-x-2.5">
                  <span
                    className={`p-1.5 rounded-lg ${
                      isInbound
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                    }`}
                  >
                    {isInbound ? <ArrowDownLeft className="w-3.5 h-3.5" /> : <ArrowUpRight className="w-3.5 h-3.5" />}
                  </span>
                  <div>
                    <span className="font-semibold capitalize text-slate-200">
                      {evt.vehicle_type}
                    </span>
                    <span className="text-slate-400 ml-1.5">({evt.smp} SMP)</span>
                  </div>
                </div>

                <div className="flex items-center space-x-1.5 text-slate-400 font-mono text-[11px]">
                  <Clock className="w-3 h-3" />
                  <span>{evt.timestamp}</span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
