'use client';

import React from 'react';
import { Bike, Car, Bus, Truck } from 'lucide-react';
import { VehicleBreakdown as BreakdownType } from '@/types';

interface VehicleBreakdownProps {
  inbound: BreakdownType;
  outbound: BreakdownType;
}

export default function VehicleBreakdown({ inbound, outbound }: VehicleBreakdownProps) {
  const items = [
    {
      label: 'Sepeda Motor',
      icon: Bike,
      inboundVal: inbound.motorcycle,
      outboundVal: outbound.motorcycle,
      smp: '0.5 SMP',
    },
    {
      label: 'Mobil Penumpang',
      icon: Car,
      inboundVal: inbound.car,
      outboundVal: outbound.car,
      smp: '1.0 SMP',
    },
    {
      label: 'Bus',
      icon: Bus,
      inboundVal: inbound.bus,
      outboundVal: outbound.bus,
      smp: '1.3 SMP',
    },
    {
      label: 'Truk / Angkutan',
      icon: Truck,
      inboundVal: inbound.truck,
      outboundVal: outbound.truck,
      smp: '1.3 SMP',
    },
  ];

  return (
    <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4 shadow-lg">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-200">Distribusi Kendaraan (PKJI / MKJI)</h3>
        <span className="text-xs text-slate-400">Faktor Ekivalen Mobil Penumpang</span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {items.map((item) => {
          const Icon = item.icon;
          return (
            <div
              key={item.label}
              className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80 space-y-2 hover:border-slate-700 transition-colors"
            >
              <div className="flex items-center justify-between text-slate-400">
                <Icon className="w-4 h-4 text-slate-300" />
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                  {item.smp}
                </span>
              </div>
              <div className="text-xs font-medium text-slate-300">{item.label}</div>
              <div className="flex items-center justify-between pt-1.5 border-t border-slate-800 text-xs font-mono">
                <span className="text-emerald-400 font-bold">{item.inboundVal} In</span>
                <span className="text-amber-400 font-bold">{item.outboundVal} Out</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
