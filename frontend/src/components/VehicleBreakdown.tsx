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
      type: 'Sepeda Motor',
      code: 'MC',
      icon: Bike,
      inCount: inbound.motorcycle,
      outCount: outbound.motorcycle,
      smp: '0.5 SMP',
    },
    {
      type: 'Mobil Penumpang',
      code: 'LV',
      icon: Car,
      inCount: inbound.car,
      outCount: outbound.car,
      smp: '1.0 SMP',
    },
    {
      type: 'Bus',
      code: 'BUS',
      icon: Bus,
      inCount: inbound.bus,
      outCount: outbound.bus,
      smp: '1.3 SMP',
    },
    {
      type: 'Truk / Angkutan',
      code: 'HV',
      icon: Truck,
      inCount: inbound.truck,
      outCount: outbound.truck,
      smp: '1.3 SMP',
    },
  ];

  return (
    <div className="bg-slate-50 border border-[#e2e8f0] rounded-lg p-3">
      <div className="flex items-center justify-between mb-2.5 px-0.5">
        <span className="text-[12px] font-semibold text-slate-500 uppercase tracking-wider">
          Distribusi Kendaraan (PKJI / MKJI)
        </span>
        <span className="text-[11px] text-slate-400 font-mono">
          Bobot Ekivalen Mobil Penumpang
        </span>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-2">
        {items.map((item) => {
          const Icon = item.icon;
          return (
            <div
              key={item.type}
              className="bg-white border border-[#e2e8f0] rounded-lg p-3 shadow-[0_1px_3px_rgba(0,0,0,0.04)] flex flex-col justify-between gap-2.5 hover:border-slate-300 transition-colors"
            >
              {/* Card Header: Icon + Label + SMP factor */}
              <div className="flex items-center justify-between gap-1.5">
                <div className="flex items-center gap-1.5 min-w-0">
                  <div className="p-1 rounded bg-slate-100 text-slate-700 shrink-0">
                    <Icon className="w-4 h-4" />
                  </div>
                  <span className="text-[13px] font-semibold text-slate-800 truncate">
                    {item.type}
                  </span>
                </div>
                <span className="text-[10px] font-mono font-medium px-1.5 py-0.5 rounded bg-slate-100 text-slate-500 shrink-0">
                  {item.smp}
                </span>
              </div>

              {/* IN / OUT Count Sub-cards */}
              <div className="flex gap-2">
                {/* Inbound Box */}
                <div className="flex-1 bg-emerald-50 rounded p-2 text-center border border-emerald-100/50">
                  <div className="text-[18px] font-bold text-emerald-700 font-mono leading-tight">
                    {item.inCount.toLocaleString('id-ID')}
                  </div>
                  <div className="text-[10px] text-emerald-600 font-semibold uppercase tracking-wider">
                    Masuk
                  </div>
                </div>

                {/* Outbound Box */}
                <div className="flex-1 bg-amber-50 rounded p-2 text-center border border-amber-100/50">
                  <div className="text-[18px] font-bold text-amber-700 font-mono leading-tight">
                    {item.outCount.toLocaleString('id-ID')}
                  </div>
                  <div className="text-[10px] text-amber-600 font-semibold uppercase tracking-wider">
                    Keluar
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
